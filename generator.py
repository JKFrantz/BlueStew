import mtg
import numpy
import math
import random

def make(debug = False):
    master_list = mtg.csv_to_card_list("Input/master_list.csv")
    mb_spinner = mtg.csv_to_spinner("Input/mb_spinner.csv", master_list)
    sb_spinner = mtg.csv_to_spinner("Input/sb_spinner.csv", master_list)
    synergy_groups = mtg.csv_to_synergy_list("Input/Synergy_Groups.csv")
    the_deck = mtg.Deck()

    number_of_colors = numpy.random.choice([2, 3, 4, 5], p = [.02, .83, .10, .05])
    colors = mtg.random_colors(number_of_colors, required_colors = ['U'],
                W = .25, U = 0, B = .2, R = .25, G = .3)
    out_colors = mtg.other_colors(colors)
    mtg.prune_spinner(out_colors, 'color_identity', mb_spinner)
    # this ought to remove lands that produce mana outside your color range, but not fetches
    mtg.prune_spinner(out_colors, 'color_identity', sb_spinner)

    have_synergy_group = numpy.random.choice([True, False], p = [.4, .6])
    synergy_allow = [] # cards that would normally be excluded from the spinner,
    # but are allowed by the synergy group
    if have_synergy_group:
        synergy_odds_total = 0
        synergy_names = []
        synergy_odds = []
        for group in synergy_groups:
            synergy_odds_total += group.get('relative_likelihood')
        for group in synergy_groups:
            synergy_names.append(group.get('name'))
            synergy_odds.append(float(group.get('relative_likelihood')) / float(synergy_odds_total))
        while True:
            the_group = mtg.find_synergy_group(numpy.random.choice(synergy_names, p = synergy_odds), synergy_groups)
            valid = True
            for color in the_group.get('colors'):
                if color not in colors:
                    valid = False
            if valid:
                for card_name in the_group.get('permit'):
                    synergy_allow.append(card_name[0])
                break

        if the_group.get('name') == 'Miracles':
            for card in mb_spinner.get():
                if "Creature" in card.get('type_line') and (card.get('name') not in ['Ice-Fang Coatl', 'Monastery Mentor', 'Snapcaster Mage', "Uro, Titan of Nature's Wrath", 'Baleful Strix']):
                    mb_spinner.multiply(card, 0)
        the_group.apply(colors, the_deck, mb_spinner, sb_spinner, master_list)
    for spinner in [mb_spinner, sb_spinner]:
        for card in spinner.get():
            if ("Synergy" in card.get('custom_keywords')) and (card.get('name') not in synergy_allow):
                spinner.multiply(card, 0)

    mb_spell_spinner = {}
    old_mb_spinner = mb_spinner.get()
    for card in old_mb_spinner:
        if ("Land" not in card.get('type_line')) and ("Synergy" not in card.get('custom_keywords')):
            mb_spell_spinner[card] = old_mb_spinner[card]
    mb_spell_spinner = mtg.Spinner(mb_spell_spinner)
    mb_spell_spinner.balance()

    mb_land_spinner = {}
    old_mb_spinner = mb_spinner.get()
    for card in old_mb_spinner:
        if ("Land" in card.get('type_line')) and ("Synergy" not in card.get('custom_keywords')):
            mb_land_spinner[card] = old_mb_spinner[card]
    mb_land_spinner = mtg.Spinner(mb_land_spinner)
    mb_land_spinner.balance()

    mtg.prune_spinner(['Synergy'], 'custom_keywords', sb_spinner)

    yorion = numpy.random.choice([True, False], p = [.12, .88])
    if yorion:
        mb_target_size = 80
        the_deck.add(mtg.find("Yorion, Sky Nomad", "name", master_list), "sb")
        mb_spinner.multiply("Ice-Fang Coatl", 2.5)
    else:
        mb_target_size = 60

    keyword_values = dict()
    keyword_values['Land'] = .35
    keyword_values['Fetch'] = .133
    keyword_values['Basic'] = .067
    keyword_values['Dual'] = .058
    keyword_values['Answer'] = .15
    keyword_values['Threat'] = .1
    if number_of_colors == 2:
        keyword_values['Utility'] = .016
    else:
        keyword_values['Utility'] = 0
    keyword_minima= {}
    for val in keyword_values:
        keyword_minima[val] = math.floor(keyword_values[val] * mb_target_size) - 1
    lt = round(keyword_values['Land'] * mb_target_size)
    lands_target = random.choice([lt - 1, lt, lt + 1])
    spells_target = mb_target_size - lands_target
    if have_synergy_group:
        if the_group.get('name') == "PFire_Dack":
            spells_target += 2

    colors_minus_blue = []
    for val in colors:
        if val != 'U':
            colors_minus_blue.append(val)

    Snow = False
    for val in the_deck.get('mb'):
        if ("Ice-Fang Coatl" in val.get("name")) or ("Dead of Winter" in val.get("name")):
            Snow = True

    for t in [(spells_target, mb_spell_spinner, ["Threat", "Answer"]), (mb_target_size, mb_land_spinner, ["Basic", "Fetch", "Dual", "Utility"])]:
        if t[1] == mb_spell_spinner:
            the_deck.add(mtg.find("Brainstorm", "name", master_list), "mb", number = 4)
            the_deck.add(mtg.find("Force of Will", "name", master_list), "mb", number = 4)
            the_deck.add(mtg.find("Ponder", "name", master_list), "mb", number = 3)
        else:
            if Snow:
                for pair in [("Plains", "Snow-Covered Plains"),("Island", "Snow-Covered Island"),("Swamp", "Snow-Covered Swamp"),("Mountain", "Snow-Covered Mountain"),("Forest", "Snow-Covered Forest")]:
                    for card in mb_land_spinner.get():
                        if card.get('name') == pair[0]:
                            val = mb_land_spinner.get()[card]
                            mb_land_spinner.multiply(card, 0)
                    for card in mb_land_spinner.get():
                        if card.get('name') == pair[1]:
                            mb_land_spinner.add(card, val)
            for card in master_list:
                if 'Land' in card.get('type_line'):
                    dual = 'Dual' in card.get('custom_keywords')
                    fetch = (('Fetch' in card.get('custom_keywords')) & ('Prismatic Vista' not in card.get('name')))
                    snow = 'Snow' in card.get('type_line')
                    basic = 'Basic' in card.get('type_line')
                    utility = 'Utility' in card.get('type_line')
                    makes_blue = 'U' in (card.get('mana_production'))
                    for color in colors_minus_blue:
                        makes_this_color = color in (card.get('mana_production'))
                        if makes_this_color and (makes_blue and (dual or fetch)):
                            if debug:
                                print(f"adding {card.get('name')}")
                            the_deck.add(card, "mb")
                            if dual and (the_deck.get('max_pip_map')[color] > 1):
                                the_deck.add(card, "mb")
                    for color in card.get('mana_production'):
                        if color not in colors:
                            if dual or basic or utility:
                                if debug:
                                    print(f"removing {card.get('name')}")
                                mb_land_spinner.multiply(card, 0)
                            if fetch:
                                if not makes_blue:
                                    if debug:
                                        print(f"removing {card.get('name')}")
                                    mb_land_spinner.multiply(card, 0)
                                else:
                                    mb_land_spinner.multiply(card, .3)
                        else:
                            if basic and ((snow and Snow) or ((not Snow) and (not snow))) and (the_deck.get('mana_pips')[color] > 2):
                                the_deck.add(card, "mb")
                                if not (the_deck.get('mana_pips')[color] > 4):
                                    mb_land_spinner.multiply(card, 0)

                    if ("Fetch" in card.get('custom_keywords')) and ("Prismatic Vista" not in card.get('name')):
                        for color in card.get('mana_production'):
                            if color not in colors:
                                mb_land_spinner.multiply(card, .3)
                    if basic:
                        mb_land_spinner.multiply(card, .8)


        while len(the_deck.get('mb')) < t[0]:
            new_card = t[1].spin()
            if (mtg.card_in_list_number(new_card, the_deck.get('seventyfive')) < 4) or ("Basic" in card.get('type_line')):
                custom_keywords = new_card.get('custom_keywords')
                current_mb = the_deck.get('mb')
                under_any_minima = False
                added_already = False
                snow_spell = ("Ice-Fang Coatl" in new_card.get("name")) or ("Dead of Winter" in new_card.get("name"))
                for keyword in t[2]:
                    if (mtg.keyword_in_list_number(keyword, "custom_keywords", current_mb) < keyword_minima[keyword]):
                        if (keyword in custom_keywords):
                            the_deck.add(new_card, 'mb')
                            if snow_spell:
                                Snow = True
                            added_already = True
                            break
                        else:
                             under_any_minima = True
                if under_any_minima:
                    continue
                if not added_already:
                    the_deck.add(new_card, 'mb')
                    if snow_spell:
                        Snow = True

    while len(the_deck.get('sb')) < 15:
        new_card = sb_spinner.spin()
        if (mtg.card_in_list_number(new_card, the_deck.get('seventyfive')) < 4) or ("Basic" in card.get('type_line')):
            the_deck.add(new_card, 'sb')

    if debug:
        print("")
        if have_synergy_group:
            print(f"Synergy Group: {the_group.get('name')}")
        else:
            print("No Synergy Group")
        print("")
        formatted_decklist = the_deck.formatted_list()
        for line in formatted_decklist:
            print(line)
        print("")
        print("Deck's Colors:")
        print(colors)
        print("")
        pips = the_deck.get('mana_pips')
        print("Total mana pips:")
        for color in mtg.color_map():
            print(f"{color}: {pips[color]}")
        print("")
        max_pips = the_deck.get('max_pip_map')
        print("Max pips:")
        for color in mtg.color_map():
            print(f"{color}: {max_pips[color]}")
        print("")
        print("Keywords:")
        for term in keyword_minima:
            print(f"{term}")
            if term == "Land":
                field = "type_line"
            else:
                field = "custom_keywords"
            print(f"min: {keyword_minima[term]} total: {mtg.keyword_in_list_number(term, field, the_deck.get('mb'))}")

    return the_deck
