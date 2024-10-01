#1 convert json to csv
import sys, os, json
import pandas as pd

from modules import config

with open(f'./channel_messages/{config["TARGET_CHANNEL"]}.json', 'r') as json_data:
    data = json.load(json_data)

df = pd.json_normalize(data)

df_messages = df[['id', 'date', 'message', 'views', 'forwards']]
df_formatted = df_messages.replace('', pd.NA).dropna()

df_sample = df_formatted.head(100)
#print(df_sample)

# SAVE TO CSV
df_sample.to_csv('messages.csv', index_label='index')