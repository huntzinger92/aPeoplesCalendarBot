import pandas as pd

with open('newEventLibrary.json', encoding='utf-8') as inputfile:
    df = pd.read_json(inputfile)

df.to_csv('eventLibrary.csv', encoding='utf-8', index=False)