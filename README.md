# BlueStew

You want a directory structure like this:

|BlueStew/

|BlueStew/Input

|BlueStew/Input/Input_Decks

place mtg.py, generator_setup.py, and generator.py in BlueStew/, unzip blue_stew_decks.zip in Input/Input_Decks/, and put the Synergy_Groups, spinner, and master_list csv's in BlueStew/Input/

If you open a terminal in the BlueStew directory and start a python3 session, you should be able to generate a deck by typing

import generator

the_deck = generator.make(debug=True)

which will show you the generated deck along with various things used in the debugging process.


