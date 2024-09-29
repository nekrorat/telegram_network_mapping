#STEP 1
import json
import os
from datetime import datetime

from telethon import TelegramClient
from telethon.tl.functions.messages import (GetHistoryRequest)


# modules.py
# env variables
from modules import config

# initialize client object with credentials
client = TelegramClient(config['phone'], config['api_id'], config['api_hash'])

# *1---------------
# datetime format to JSON
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return list(o)

        return json.JSONEncoder.default(self, o)
# *2---------------
# open a file
target_channel = 'readovkanews'

filename = f'./channels/{target_channel}.json'
# extract filename from the path
#target_channel = re.findall('[^/]+(?=\.json)', filename)


min_id = 0

# if a json file (for target channel) exist, open the file
if os.path.isfile(filename):
    with open(filename, 'r') as f: # Use file to refer to the file object
        channel_data = f.read()
    channel_data_dict = json.loads(channel_data)
    # save the id of the last scrapped message
    min_id = channel_data_dict[0]['id']
    
#print(last_msg)
# *3---------------
async def main():

    offset_id = 0
    limit = 100
    all_messages = []
    total_messages = 0
    total_count_limit = 0

    # print(offset_id)
    while True:
        print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
        history = await client(GetHistoryRequest(
            peer=target_channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=min_id,
            hash=0
        ))

        # break the cycle if list index out of range (no more messages left)
        messages = history.messages
        if not messages:
            break

        if messages[0].id > min_id and messages[0].id - min_id <= 100:
            limit = 1

        # move offset_id to 100 (limit) + 1 message and restart cycle (scrape another 100 messages)
        offset_id = messages[len(messages) - 1].id

        # save message dict into list
        for message in messages:
            all_messages.append(message.to_dict())
        # count total messages
        total_messages = len(all_messages)

        # setup limit of messages in total_count_limit value
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break

    # if there is JSON for the channel and it needs an update new messages do this
    if min_id != 0:
        #load JSON to file_data list
        with open(f'./channels/{target_channel}.json') as json_file:
            file_data = json.load(json_file) 
            # add new scrapped messaged to file_data list
            file_data = [*all_messages, *file_data]
        # save to JSON (raw)
        with open(f'./channels/{target_channel}.json', 'w') as f:
            json.dump(file_data, f, cls=DateTimeEncoder)
    #if the channel was never scrapped do this (has no JSON yet)
    else:
        #save to JSON (raw)
        with open(f'./channels/{target_channel}.json', 'w') as f:
            json.dump(all_messages, f, cls=DateTimeEncoder)

    #save to JSON (beautified)
    # with open('./channels/group_project_LIMMA.json', 'w+', encoding='utf-8') as f:
    #     json.dump(all_messages, f, ensure_ascii=False, cls=DateTimeEncoder, indent=4)

with client:
    client.loop.run_until_complete(main())


