#1 convert json to csv
import json
from pathlib import Path
import pandas as pd

from utils.modules import config

with open(f'{Path(__file__).parent.parent}/channel_messages/{config["TARGET_CHANNEL"]}.json', 'r') as json_data:
    data = json.load(json_data)

df = pd.json_normalize(data)

df_messages = df[['id', 'date', 'message', 'views', 'forwards']]
df_formatted = df_messages.replace('', pd.NA).dropna()

df_sample = df_formatted.head(100)
#print(df_sample)

# SAVE TO CSV
df_sample.to_csv('./src/preprocessing/messages.csv', index_label='index')