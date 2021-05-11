# BlueStew

To generate decks with Blue Stew, the appropriate directory structure is like this:

|BlueStew/

|BlueStew/Input/

|BlueStew/Input/Input_Decks/

Place mtg.py, generator_setup.py, and generator.py in BlueStew/, put the Synergy_Groups, spinner, and master_list csv's in BlueStew/Input/, and unzip blue_stew_decks.zip in BlueStew/Input/Input_Decks/

Note that you don't actually need the generator_setup.py or blue_stew_decks.zip files if you're just creating decks. They were used in the creation of the deck generator, so I thought I'd include them.

If you open a terminal in the BlueStew/ directory and start a python3 session, you should be able to generate a deck by typing

import generator

the_deck = generator.make(debug=True)

which will show you the generated deck along with various indicators used in the debugging process.

----

The overall structure is that there should be three main files that create the generator:

generator_setup.py - this reads a directory of deck files (|BlueStew/Input/Input_Decks/) and from that creates the mb_spinner.csv, sb_spinner.csv, and master_list.csv files. The spinner files merely show the average representation of each card in the entire directory of decks -- so if, say, the mb_spinner number for Brainstorm were .01, it would mean that Brainstorm is 1% of all cards across all mainboards. (Of course, in reality, it is much higher than that.) The master_list file will contain data for each card, pulled from scrython, but you'll need to supplement this by adding some columns, changing some column names, or altering data to fit your needs. You don't need to run this unless you're creating your own generator using a new pool of decks, and you shouldn't because it will overwrite the master_list.csv file with a new one taken straight from scryfall with none of the custom changes made by hand.

generator.py - this actually creates the deck as a deck object if you run its "make" function. You can then display that deck in MTGO or Formatted formats as you see fit. On bluestew.net, the deck object is displayed as part of a Django view.

mtg.py - this contains most of the overall code, which is used by generator.py. The idea is that a generator file is a python script that creates a specific type of deck in a certain meta, while mtg.py is meant to contain code useful in creating any deck in any meta.

mtg.py contains four basic types of objects:
- Card object, which is composed of a dictionary of values (cmc, name, etc) and that's it
- a Deck object contains lists for mb, sb, 75 (so you don't have more than 4 of a card), and some metrics to keep track of mana pips in the overall deck
- Spinner objects contain references to cards along with associated odds. Spinners create the randomness: if you "spin" a spinner, it gives you a random card with weighted odds.
- Synergy_Groups are really crude ways of handling synergy. I'd kind of rather not talk about it, but I guess I ought to. "Synergy_Groups.csv" is a file where cards are clustered together into groups, with names like "Miracles" or "GSZ", and if a Synergy Group is used, then cards under "mb_add" and "sb_add" are added with their designated quantity, and spinners are changed according to "mb_multiply" and "sb_multiply". Cards that would normally be excluded from spinners because they only work with certain synergies are included if they are under "permit"
