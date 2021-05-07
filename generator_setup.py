import mtg
import pandas as pd
master_list = pd.DataFrame(mtg.dir_to_master_list("Input/Input_Decks/"))
master_list.to_csv("Input/master_list.csv", index=False)
mtg.dir_to_csv_spinners("Input/Input_Decks/", "Input/")
