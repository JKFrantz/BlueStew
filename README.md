# BlueStew

To generate decks with Blue Stew, the appropriate directory structure is like this:

|BlueStew/

|BlueStew/Input/

|BlueStew/Input/Input_Decks/

Place mtg.py, generator_setup.py, and generator.py in BlueStew/, put the Synergy_Groups, spinner, and master_list csv's in BlueStew/Input/, and unzip blue_stew_decks.zip in Input/Input_Decks/

If you open a terminal in the BlueStew/ directory and start a python3 session, you should be able to generate a deck by typing

import generator

the_deck = generator.make(debug=True)

which will show you the generated deck along with various indicators used in the debugging process.


