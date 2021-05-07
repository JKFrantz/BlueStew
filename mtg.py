import csv
import glob
import os
import numpy
import scrython
import pandas as pd
import time
import math
from collections import defaultdict

class Card:
    def __init__(self, dict):
        # val_list must be a dictionary with keys like "cmc"
        self.values = dict

# return method for any variable
    def get(self, val):
        return self.values[val]

class Deck:
    def __init__(self):
        self.values = {
            'mb': [],
            'sb': [],
            'seventyfive': [],
            'curve': defaultdict(int),
            'mana_pips': defaultdict(int),
            'max_pip_map': defaultdict(int)
        }

    def get(self, val):
        return self.values[val]

    def asDict(self):
        deck_tallies = {
            'mb': defaultdict(int),
            'sb': defaultdict(int)
        }
        for mb_or_sb in ['mb', 'sb']:
            for card in self.get(mb_or_sb):
                deck_tallies[mb_or_sb][card] += 1
        return deck_tallies

    def MTGO_list(self):
        d = self.asDict()
        mtgo_list = []
        for mb_or_sb in ['mb', 'sb']:
            for card in d[mb_or_sb]:
                mtgo_list.append(f"{d[mb_or_sb][card]} {card.get('name')}")
            if mb_or_sb == "mb":
                mtgo_list.append("\n")
        return mtgo_list

    def formatted_list(self):
        d = self.asDict()
        formatted_list = []
        type_map = {
            "Creatures": ["Creature"],
            "Planeswalkers": ["Planeswalker"],
            "Spells": ["Instant", "Sorcery"],
            "Artifacts": ["Artifact"],
            "Enchantments": ["Enchantment"],
            "Lands": ["Land"]
        }
        formatted_dict = {
            "Creatures": defaultdict(int),
            "Planeswalkers": defaultdict(int),
            "Spells": defaultdict(int),
            "Artifacts": defaultdict(int),
            "Enchantments": defaultdict(int),
            "Lands": defaultdict(int)
        }

        for card in d['mb']:
            category = None
            for label in type_map:
                for type in type_map[label]:
                    if type in card.get('type_line'):
                        category = label
                        break
                if category != None:
                    break
            formatted_dict[category][card.get('name')] += d['mb'][card]

        for label in formatted_dict:
            if formatted_dict[label] != {}:
                formatted_list.append(f"{label} ({sum(formatted_dict[label].values())}):")
                for card_name in formatted_dict[label]:
                    formatted_list.append(f"{formatted_dict[label][card_name]} {card_name}")
                formatted_list.append("\n")
        formatted_list.append(f"Sideboard ({sum(d['sb'].values())}):")
        for card in d['sb']:
            formatted_list.append(f"{d['sb'][card]} {card.get('name')}")

        return formatted_list

    def save(self, formatted_path, mtgo_path, formatted = True, mtgo = True):
        formatted_list, mtgo_list = display_lists()
        d = {
            formatted: {'list': formatted_list, 'path': formatted_path},
            mtgo: {'list': mtgo_list, 'path': mtgo_path},
        }
        for val in d:
            if val:
                f = open(f"{d[val]['path']}.txt", "w")
                for val2 in d[val]['list']:
                    f.write(val2)
                f.close()

    def add(self, newcard, mb_or_sb, number = 1):
        if ('Land' not in newcard.get('type_line')) and (mb_or_sb == 'mb'):
            for color in color_map().keys():
                sum = 0
                for pip in newcard.get('pips'):
                    if pip == color:
                        sum += 1
                if sum > self.get('max_pip_map')[color]:
                    self.values['max_pip_map'][color] = sum
        for val in range(0, number):
            self.values[mb_or_sb].append(newcard)
            self.values['seventyfive'].append(newcard)
            if ('Land' not in newcard.get('type_line')) and (mb_or_sb == 'mb'):
                self.values['curve'][newcard.get('cmc')] += 1
            if not isinstance(newcard.get('pips'), float):
                for color in color_map().keys():
                    for char in newcard.get('pips'):
                        if color == char:
                            self.values['mana_pips'][color] += 1


class Spinner:
    def __init__(self, dictionary):
        self.spinner = dictionary

    def spin(self):
        keys = []
        values = []
        for val in self.spinner.keys():
            keys.append(val)
            values.append(self.spinner[val])
        new_card = numpy.random.choice(keys, p = values)
        return (new_card)

    def multiply(self, card, multiplier):
        for card2 in self.spinner:
            if card == card2:
                self.spinner[card2] *= multiplier
        self.balance()

    def add(self, card, number):
        for card2 in self.spinner:
            if card == card2:
                self.spinner[card2] += number
                if self.spinner[card2] < 0:
                    self.spinner[card2] = 0
        self.balance()

    def balance(self):
        s = sum(self.spinner.values())
        if s != 1:
            r = 1 / s
            for val in self.spinner:
                self.spinner[val] *= r

    def get(self):
        return self.spinner

class Synergy_Group:
    def __init__(self, setup_dict):
        self.values = setup_dict

    def get(self, value_being_asked_for):
        return self.values[value_being_asked_for]

    def get_group(self):
        return self.values

    def apply(self, colors, deck, mb_spinner, sb_spinner, master_list):
        for val in self.get('mb_add'):
            a = int(val[1] // 1)
            in_color = True
            card = find(val[0], 'name', master_list)
            if not isinstance(card.get('color_identity'), float):
                for val2 in card.get('color_identity'):
                    if val2 not in colors:
                        in_color = False
            if in_color:
                for val2 in range(0, a):
                    print(f"adding {card.get('name')}")
                    deck.add(card, 'mb')
                m = val[1] % 1
                if m > 0:
                    add = numpy.random.choice([True, False], p = [m, 1-m])
                    if add:
                        deck.add(card, 'mb')
        if not isinstance(self.get('sb_add'), float):
            for val in self.get('sb_add'):
                a = int(val[1] // 1)
                in_color = True
                card = find(val[0], 'name', master_list)
                for val2 in card.get('color_identity'):
                    if val2 not in colors:
                        in_color = False
                if in_color:
                    for val2 in range(0, a):
                        deck.add(card, 'sb')
                    m = val[1] % 1
                    if m > 0:
                        add = numpy.random.choice([True, False], p = [m, 1-m])
                        if add:
                            deck.add(card, 'sb')
        if not isinstance(self.get('mb_multipliers'), float):
            for val in self.get('mb_multipliers'):
                card = find(val[0], 'name', master_list)
                mb_spinner.multiply(card, val[1])
        if not isinstance(self.get('sb_multipliers'), float):
            for val in self.get('sb_multipliers'):
                card = find(val[0], 'name', master_list)
                sb_spinner.multiply(card, val[1])

# randomly selects a given number of colors with optional
# required colors and option to given different
# odds for each color. If you use the latter option, make sure
# the odds for all 5 colors add up to 1.
def random_colors(number_of_colors, required_colors = [],
    W = .2, U = .2, B = .2, R = .2, G = .2):
    colors = []
    colors += required_colors
    while len(colors) < number_of_colors:
        new_color = numpy.random.choice(['W', 'U', 'B', 'R', 'G'],
        p = [W, U, B, R, G])
        if new_color not in colors:
            colors.append(new_color)
    return colors

def find(name, field, list):
    for val in list:
        if val.get(field) == name:
            return val
    return None

def count(name, field, list):
    count = 0
    for val in list:
        if val.get(field) == name:
            count += 1
    return count


############################################################################
# These methods are used by the Generator program. They read files
# and do something with them, like make card objects or spinner objects.
############################################################################

def csv_to_spinner(file_name, master_list):
    spinner_frame = pd.read_csv(file_name)
    spinner_frame_dict = spinner_frame.to_dict()
    spinner_dict = {}
    for val in range(0, len(spinner_frame_dict['names'])):
        spinner_dict[find(spinner_frame_dict['names'][val], 'name_in_decklist', master_list)] = \
            spinner_frame_dict['numbers'][val]
    return Spinner(spinner_dict)

def csv_to_synergy_list(file_name):
    list_of_synergy_groups = []
    list_of_synergy_dicts = []
    synergy_dataframe = pd.read_csv(file_name)
    synergy_column_names = synergy_dataframe.columns.values.tolist()
    synergy_list_lines = synergy_dataframe.values.tolist()
    for line in synergy_list_lines:
        new_dict = {}
        for val in range(len(synergy_column_names)):
            new_dict[synergy_column_names[val]] = line[val]
        list_of_synergy_dicts.append(new_dict)
    for val in list_of_synergy_dicts:
        for val2 in ["mb_add", "sb_add", "mb_multipliers", "sb_multipliers", "permit"]:
            if isinstance(val[val2], str):
                val[val2] = val[val2].split("|")
                for val3 in range(len(val[val2])):
                    val[val2][val3] = val[val2][val3].split("/")
                    if len(val[val2][val3]) > 1:
                        if val[val2][val3][1].isdigit():
                            val[val2][val3][1] = int(val[val2][val3][1])
                        else:
                            val[val2][val3][1] = float(val[val2][val3][1])
            else:
                val[val2] = []
    for val in list_of_synergy_dicts:
        list_of_synergy_groups.append(Synergy_Group(val))
    return list_of_synergy_groups

# reads a csv file and returns a list of card objects
def csv_to_card_list(file_name):
    cards = pd.read_csv(file_name)
    cards_dict = cards.to_dict()
    cards_list = []
    for val in range(0, len(cards_dict['name'])):
        new_dict = {}
        for val2 in cards_dict:
            if isinstance(cards_dict[val2][val], float):
                new_dict[val2] = ""
            else:
                new_dict[val2] = cards_dict[val2][val]
        cards_list.append(Card(new_dict))
    return cards_list

############################################################################
# These methods are mostly used in the setup process for a generator:
# creating master_list and spinner csv's from the Input_Decks folder.
############################################################################

# creates mb and sb spinner csvs in the output_directory for the pool
# of decks in the input_directory
def dir_to_csv_spinners(input_directory, output_directory):
    individual_card_totals = {'mb': defaultdict(int), 'sb': defaultdict(int)}
    overall_card_totals = {'mb': 0, 'sb': 0}
    for filename in glob.glob(f"{input_directory}*.txt"):
        f = open(filename, "r")
        mb_or_sb = 'mb'
        for line in f:
            if (line == "\n") or (line == ""):
                mb_or_sb = 'sb'
            else:
                stripped_line = line.strip()
                line_list = stripped_line.split()
                cards_added = int(line_list[0])
                individual_card_totals[mb_or_sb][' '.join(line_list[1:])] += cards_added
                overall_card_totals[mb_or_sb] += cards_added
    dicts = {'mb': {'names': [], 'numbers': []}, 'sb': \
                    {'names': [], 'numbers': []}}
    for val in individual_card_totals:
        for val2 in individual_card_totals[val]:
            dicts[val]['names'].append(val2)
            dicts[val]['numbers'].append(float(individual_card_totals[val][val2]) / overall_card_totals[val])
    for val in ['mb', 'sb']:
        frame = pd.DataFrame(dicts[val])
        frame.to_csv(f"{output_directory}{val}_spinner.csv", index=False)

# Makes a Deck object out of a normal MTGO decklist
def txt_to_deck(file_name, master_list):
    f = open(file_name, "r")
    the_deck = Deck()
    mb_or_sb = 'mb'
    for line in f:
        if line == "\n":
            mb_or_sb = 'sb'
        else:
            stripped_line = line.strip()
            line_list = stripped_line.split()
            new_card = find(' '.join(line_list[1:]), 'name', master_list)
            the_deck.add(new_card, mb_or_sb, master_list, number = [int(line_list[0])])
    return the_deck

# takes a directory and returns a list of Deck objects for every
# txt file in that directory
# Don't forget the final slash in the directory path!
def dir_to_decks(path, master_list):
    decks_list = []
    for filename in glob.glob(f"{path}*.txt"):
        decks_list.append(txt_to_deck(filename, master_list))
    return decks_list

# returns a dictionary of lists where each list index corresponds to the same card
# USES: dir_to_card_names, txt_to_card_names
def dir_to_master_list(input_dir):
    all_card_names = dir_to_card_names(input_dir)
    all_cards = {}
    for val in all_card_names:
        print("making Scryfall request")
        all_cards[val] = scrython.cards.Named(fuzzy=val)
        time.sleep(0.1)
# if you want to use card attributes other than these these,
# add them to the cards list below and the loop after that.
# If the field is a custom field (not a Scryfall one),
# you can also just manually make it
# in the csv file after you've already output it.
    cards = {
        "name_in_decklist": [],
        "name": [],
        "cmc": [],
        "color_identity": [],
        "type_line": [],
        "mana_cost": [],
        "custom_keywords": [],
    }
    for val in all_cards:
        cards["name_in_decklist"].append(val)
# bc it might be "Brazen Borrower" in the decklist but
# "Brazen Borrower // Petty Theft" in Scryfall
        cards["name"].append(all_cards[val].name())
        cards["cmc"].append(all_cards[val].cmc())
        cards["color_identity"].append(all_cards[val].color_identity())
        cards["type_line"].append(all_cards[val].type_line())
        try:
            cards["mana_cost"].append(all_cards[val].mana_cost())
        except KeyError:
            cards["mana_cost"].append("")
        cards["custom_keywords"].append("")
    return cards

# returns a set of all card names in an entire directory
# don't forget the final slash in the directory path
# USES: text_to_card_names
def dir_to_card_names(dir_name):
    card_set = set()
    for filename in glob.glob(f"{dir_name}*.txt"):
        s = txt_to_card_names(filename)
        for val in s:
            card_set.add(val)
    return card_set

# returns a set containing all the card names in a specific
# deck txt file
def txt_to_card_names(file_name):
    card_set = set()
    f = open(file_name, "r")
    for line in f:
        if line != "\n":
            stripped_line = line.strip()
            line_list = stripped_line.split()
            card_set.add(' '.join(line_list[1:]))
    return card_set

def find_deck_files(input_directory, card_name):
    print(f"Decks containing {card_name}:")
    for filename in glob.glob(f"{input_directory}*.txt"):
        f = open(filename, "r")
        contains_card = False
        for line in f:
            if not ((line == "\n") or (line == "")):
                stripped_line = line.strip()
                line_list = stripped_line.split()
                if ' '.join(line_list[1:]) == card_name:
                    contains_card = True
        if contains_card == True:
            print(filename)

def prune_spinner(list, field, spinner):
    for card in spinner.get():
        for val in list:
            if not isinstance(card.get(field), float):
                if val in card.get(field):
                    spinner.multiply(card, 0)

def other_colors(input_list):
    output_list = ['W', 'U', 'B', 'R', 'G']
    for color in input_list:
        output_list.remove(color)
    return output_list

def card_in_list_number(card, list):
    total = 0
    for list_card in list:
        if card == list_card:
            total += 1
    return total

def keyword_in_list_number(keyword, field, list):
    total = 0
    for list_card in list:
        if keyword in list_card.get(field):
            total += 1
    return total

def find_synergy_group(name, list):
    for group in list:
        if name == group.get('name'):
            return group

def color_map():
    color_map = {
        'W' : 'White',
        'U' : 'Blue',
        'B' : 'Black',
        'R' : 'Red',
        'G' : 'Green'
    }
    return color_map

def basic_lands():
    return ["Plains", "Island", "Swamp", "Mountain", "Forest",
    "Snow-Covered Plains", "Snow-Covered Island", "Snow-Covered Swamp",
    "Snow-Covered Mountain", "Snow-Covered Forest", "Wastes"]
