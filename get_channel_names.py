import json
import os
from dateutil.relativedelta import relativedelta

from pyvis.network import Network

from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
import telethon

# env variables
from modules import config
# initialize client object with credentials
client = TelegramClient(config['phone'], config['api_id'], config['api_hash'])

#^ switch from offline to online
from msg_scrapper import filename, target_channel
#filename = f'./path/channel_name.json'

# *1. Get telegram channels' names

# open json
with open(filename, 'r') as f: # Use file to refer to the file object
        json_file = f.read()
data = json.loads(json_file)

# source channel id.
source_channel_id = (data[0]['peer_id']['channel_id'])

# create a list for fwd channels' ids list with repeated occurence
result_list = [source_channel_id]
# create a set for unique fwd channels' ids list
result_set = set()

# loop thru json to find channels' ids
for i in data:
    for key_a, value_a in i.items():
        #go in fwd_from dict
        if value_a is not None and key_a == 'fwd_from':
            for key_b, value_b in i['fwd_from'].items():
                #find all ids of the forwarded channels
                if key_b == 'from_id' and value_b is not None:
                        for key_c, value_c in value_b.items():
                                if key_c == 'channel_id':
                                        result_list.append(value_c)
                #some msgs forwared from users not channels. find this instances and save user names
                elif i['fwd_from']['from_id'] is None:
                        result_list.append(i['fwd_from']['from_name'])

# save channels ids in the set to keep only unique values
result_set = set(result_list)

# *2. Get telegram channels' names
result_dict = {}
channel_names = f'{target_channel}_output.json'
filepath = f'./channels_output/{channel_names}'

# & OFFLINE if there is no json file request channel names from telegram api
#^ delete NOT to force online, not = check if the json file exist
if not os.path.isfile(filepath):
    # request to telegram api
    async def main():
        for i in result_set:
            # for ids which are int
            if isinstance(i, int):
                # get all channel ids from the set, find names, and save them in dict
                try:
                    result = await client.get_entity(i)
                    channel_full_info = await client(GetFullChannelRequest(channel=result))

                    # push creation date 1 month back, for some reason it is one month off
                    creation_date_adj = channel_full_info.chats[0].date - relativedelta(
                        months=1)

                    # merge subkeyes and subsets under key (channel id)
                    result_dict[i] = {
                        **{'channel_name': channel_full_info.chats[0].username},
                        **{'title': channel_full_info.chats[0].title},
                        **{'creation_date': creation_date_adj.strftime('%d-%B-%Y')},
                        **{'participants_count': channel_full_info.full_chat.participants_count},
                        **{'about': channel_full_info.full_chat.about},
                        **{'linked_chat_id': channel_full_info.full_chat.linked_chat_id},
                        **{'source_channel': True if i == source_channel_id else False},
                        **{'fwd_count': 0}
                    }

                # if there is a private channel, save name as 'private'
                except telethon.errors.rpcerrorlist.ChannelPrivateError:
                    print(
                        f'Error: telethon.errors.rpcerrorlist.ChannelPrivateError. Channel (id: {i}) saved as \'private\'')
                    
                    result_dict[i] = {
                        **{'channel_name': 'private'},
                        **{'participants_count': 0},
                        **{'source_channel': True if i == source_channel_id else False},
                        **{'fwd_count': 0}
                    }
            # for usernames (users not channels) which are str
            else:
                    result_dict[i] = {
                        **{'channel_name': f'user: {i}'},
                        **{'participants_count': 0},
                        **{'source_channel': True if i == source_channel_id else False},
                        **{'fwd_count': 0}
                    }

        
            # save forward occurrences as "nested value set" within nested key 'fwd_count'
            for i in result_list:
                for key, value in result_dict.items():
                    #try:
                        if i == key:
                            result_dict[key]['fwd_count'] += 1
                    # except Exception as e:
                    #     print(e)
                    #     i == key
        
        # once request to Telethon done, create a new channel_names JSON file and save result,
        # to use this JSON rather than send requests every time
        with open(filepath, 'w') as f:
            json.dump(result_dict, f, default=str)

    with client:
        client.loop.run_until_complete(main())

# & OFFLINE if there is a json file skip request to telethon
else:
    with open(filepath, 'r') as f:
        json_file = f.read()
    result_dict = json.loads(json_file)

    # make it str type to avoid error in pyvis node
    source_channel_id = str(source_channel_id)

#& OFFLINE Master List
# create master list of channels
master_list_file = 'master_list.json'
master_list_dict = {k: {sub_k: sub_v for sub_k,sub_v in v.items() if sub_k=='channel_name' or sub_k=='creation_date' or sub_k=='linked_chat_id' } for k,v in result_dict.items()}

# if there is no master list exist -> create new
if not os.path.isfile(master_list_file):
    with open(master_list_file, 'w') as f:
        json.dump(master_list_dict, f, default=str, indent=4)
# if master list exist
else:
    # open master list from the file
    with open(master_list_file, 'r') as f:
        master_json_file = json.load(f)
    # compare master list with master dictonary (the dict with new data)
    for k in master_list_dict.keys():
        if k not in master_json_file.keys():
            # update master list with missing channels
            master_json_file.update({k: master_list_dict[k]})
            # save the updated master list back to the file
            with open(master_list_file, 'w') as f:
                json.dump(master_json_file, f, default=str, indent=4)

# * ---

# find max value and calc 1%
def one_percent(n):
    tmp_list = []
    for k,v in result_dict.items():
        tmp_list.append(v[n])
    print(tmp_list)
    result = max(tmp_list)/100
    return result

fwd_one_percent = one_percent('fwd_count')
participants_one_percent = one_percent('participants_count')

# *3. Visualize in pyvis network

g = Network(height='100%', width='100%',
            bgcolor='#222222', font_color='white')

# build the source node
g.add_node(int(source_channel_id),
#borderWidth=10,
color='#D1F2EB',
label=result_dict[source_channel_id]['channel_name'],
title=f'id: {k}' +
'\ntitle: ' + result_dict[source_channel_id]['title'] +
'\ncreation date: ' + result_dict[source_channel_id]['creation_date'] +
'\nfollowers: ' + str("{:,}".format(result_dict[source_channel_id]['participants_count'])),
size=25
)

# build all other nodes
for k, v in result_dict.items():

    # find percentage for each edge and divide it on 10 to fit from 1 to 10 edge width range
    edge_width = v['fwd_count']/fwd_one_percent/10
    # find percentage for each edge and divide it on 2 to fit from 1 to 50 edge width range
    part_count = v['participants_count']/participants_one_percent/2

    # keep edge width within .5 to 10 range
    if edge_width > 10:
        edge_width = 10
    elif edge_width < .5:
        edge_width = .5

    if part_count < 10:
        part_count = 10
    
    if v['source_channel'] == False:
    #private channel nodes
        if v['channel_name'] == 'private':
            # add id to private channels' names
            v['channel_name'] += f' channel\nid:{k}'
            
            g.add_node(k,
            color='#E8DAEF',
            label=v['channel_name'],
            title=f'id: {k}\ntitle: unknown\ncreation date: unknown\nfollowers: unknown',
            size=10             
            )
            
            g.add_edge(int(source_channel_id), k,
            color='#1565C0',
            width=edge_width,
            title='forward count: ' + str("{:,}".format(v['fwd_count']))
            )
        # users (non-channels)
        elif v['channel_name'] == f'user: {k}':
            
            g.add_node(k,
            color='#ECF87F',
            label=v['channel_name'],
            title=f'id: {k}\ntitle: n/a\ncreation date: n/a\nfollowers: n/a',
            size=10               
            )
            
            g.add_edge(int(source_channel_id), k,
            color='#1565C0',
            width=edge_width,
            title='forward count: ' + str("{:,}".format(v['fwd_count']))
            )
        # other nodes

        else:

            #~ +++basecamp
            if v['channel_name'] == 'vasylevka' or v['channel_name'] == 'polohy_ru' or v['channel_name'] == 'tokmak_ru' or v['channel_name'] == 'energodar_ru' or v['channel_name'] == 'berdyansk_ru' or v['channel_name'] == 'melitopol_ru' or v['channel_name'] == 'hercon_ru' or v['channel_name'] == 'infodniprorudne' or v['channel_name'] == 'Kharkov_Z_news' or v['channel_name'] == 'KupyanskZ' or v['channel_name'] == 'VolchanskVGA' or v['channel_name'] == 'russiankupiansk':
                g.add_node(k,
                color='#e61809',
                label=v['channel_name'],
                title=f'id: {k}' + '\ntitle: ' + v['title'] + '\n creation date: ' + v['creation_date'] + '\n followers: ' + str("{:,}".format(v['participants_count'])),
                size=part_count               
                )
            #~ ---basecamp

            # public channels (most common nodes)
            elif v['channel_name'] is not None:
                g.add_node(k,
                color='#64B5F6',
                label=v['channel_name'],
                title=f'id: {k}' + '\ntitle: ' + v['title'] + '\n creation date: ' + v['creation_date'] + '\n followers: ' + str("{:,}".format(v['participants_count'])),
                size=part_count
                )
            
            else:
                # designate private channels with public invite url
                v['channel_name'] = f'private channel\nwith public link\nid:{k}'

                g.add_node(k,
                color='#E8DAEF',
                label=v['channel_name'],
                title=f'id: {k}' + '\ntitle: ' + v['title'] + '\n creation date: ' + v['creation_date'] + '\n followers: ' + str("{:,}".format(v['participants_count'])),
                size=part_count
                )
            

            g.add_edge(int(source_channel_id), k,
            color='#1565C0',
            width=edge_width,
            title='forward count: ' + str("{:,}".format(v['fwd_count']))
            )

#g.barnes_hut()
g.force_atlas_2based()
#g.hrepulsion()

# g.show_buttons(
#      filter_=['physics', 'edges']
#       )

g.width = '100%'
g.height = '100%'
OPTIONS = """const options = {
  "edges": {
    "color": {
      "inherit": true
    },
    "selfReferenceSize": null,
    "selfReference": {
      "angle": 0.75
    },
    "smooth": {
      "type": "cubicBezier",
      "forceDirection": "none"
    }
  },
  "physics": {
    "enabled": false,
    "forceAtlas2Based": {
      "gravitationalConstant": -150,
      "springLength": 200
    },
    "minVelocity": 0.75,
    "solver": "forceAtlas2Based"
  }
}"""

# OPTIONS = """const options = {
#   "edges": {
#     "color": {
#       "inherit": true
#     },
#     "selfReferenceSize": null,
#     "selfReference": {
#       "angle": 0.7853981633974483
#     },
#     "smooth": {
#       "type": "cubicBezier",
#       "forceDirection": "none"
#     }
#   },
#   "physics": {
#     "enabled": false,
#     "forceAtlas2Based": {
#       "gravitationalConstant": -100,
#       "springLength": 300
#     },
#     "minVelocity": 0.75,
#     "solver": "forceAtlas2Based"
#   }
# }"""
g.set_options(OPTIONS)

#g.toggle_physics(False)

#^ Enable pyvis
g.show('nodemap.html')
