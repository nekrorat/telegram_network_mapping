#STEP 2
import json
from pyvis.network import Network

f = open("channel_messages.json")
data= json.load(f)

# for i in data:
    # if i['fwd_from'] and not None:
    #     print(i['fwd_from'])

result_list = []

#print(data[0]['peer_id']['channel_id'])
d = (data[0]['peer_id']['channel_id'])

for i in data:
    for key, value in i.items():
         if value is not None and key == 'fwd_from':
             for m in i['fwd_from']:
                #print(i['fwd_from']['from_id']['channel_id'])
                result_list.append(i['fwd_from']['from_id']['channel_id'])

result_set = set(result_list)
#print(result_set)

g = Network(height='1500px', width='100%', bgcolor='#222222', font_color='white')

g.add_node(d, label=f'{d}')

for i in result_set:
    g.add_node(i, label=f'{i}')
    g.add_edge(d, i)

g.show('nodemap.html')

# list [
#   dict {
#        key: value
#   }
# ]