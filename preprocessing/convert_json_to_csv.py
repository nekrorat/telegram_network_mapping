#1 convert json to csv
import json
import pandas as pd

with open('../channel_messages/nach_shtabu.json', 'r') as json_data:
    data = json.load(json_data)

df = pd.json_normalize(data)

df_messages = df[['id', 'date', 'message', 'views', 'forwards']]
df_formatted = df_messages.replace('', pd.NA).dropna()

df_sample = df_formatted.head(100)
#print(df_sample)

# SAVE TO CSV
df_sample.to_csv('messages.csv', index_label='index')