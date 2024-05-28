#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 11:24:08 2023

@author: roman
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 09:01:01 2023

@author: ubuntu
https://query.wikidata.org/
"""
import json
import requests
def apiquery(searchterm,language="en", limit = 7):
    url = "https://www.wikidata.org/w/api.php?action=wbsearchentities&limit="+str(limit)+"&format=json&search=" + searchterm + "&language=" + language
    r = requests.get(url)
    j = r.json()
    return j["search"]

#%%

results = apiquery("evolutionary biology",limit = 20)
# results[0]
for r in results: 
    if 'description' in r.keys(): 
        print(r['id'] + ": \t" + r['description'])


#%%
from qwikidata.entity import WikidataItem
from qwikidata.json_dump import WikidataJsonDump
from qwikidata.utils import dump_entities_to_json


from qwikidata.entity import WikidataItem, WikidataLexeme, WikidataProperty
from qwikidata.linked_data_interface import get_entity_dict_from_api
from qwikidata.sparql import (get_subclasses_of_item,
                              return_sparql_query_results)

ECOLOGY = 'Q7150'
q42_dict = get_entity_dict_from_api(ECOLOGY)
q42 = WikidataItem(q42_dict)
subs = get_subclasses_of_item(ECOLOGY)

i_dict = get_entity_dict_from_api(subs[1])
i = WikidataItem(i_dict)
i

#%%
Q_RIVER = "Q4022" #try Q7150
subclasses_of_river = get_subclasses_of_item(Q_RIVER)
for i_id in subclasses_of_river:
    i_dict = get_entity_dict_from_api(i_id)
    i = WikidataItem(i_dict)
    print(i_id + ": "+ i.get_label()+ "\n\t" + i.get_description())
    
#%%    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#%%
import networkx as nx
import matplotlib.pyplot as plt
from qwikidata.sparql import get_subclasses_of_item
import numpy as np
import time
#%%
def addchildren(parent_id, G, limit = 100):
    # Fetch all subclasses
    subclasses = get_subclasses_of_item(parent_id)
    count=0
    for subclass_id in subclasses:
        count+=1
        if limit != None:
            if count>limit: break
        i = get_entity_dict_from_api(subclass_id)
        item = WikidataItem(i)
        subclass_label = item.get_label()
        if subclass_label != '':
            print('add->' + subclass_label)
            G.add_node(subclass_id, label=subclass_label)
            G.add_edge(subclass_id, parent_id)
    return subclasses

def get_matters_of_study(code):
    query_string = """
    SELECT ?WDid ?label
    WHERE {{
      ?WDid (wdt:P2579)* wd:{} .
      ?WDid rdfs:label ?label.
      FILTER(LANGMATCHES(LANG(?label), "en"))
    }}
    """.format(
        code
    )
    results = return_sparql_query_results(query_string)
    uris = [binding["WDid"]["value"] for binding in results["results"]["bindings"]]
    
    qids = [uri.split("/")[-1] for uri in uris]
    labels = [binding["label"]["value"] for binding in results["results"]["bindings"]]
    return (qids,labels)

def addSO(parent_id, G, limit = 100):
    # Fetch all matters
    subclasses, labels = get_matters_of_study(parent_id)
    count=0
    for subclass_id, subclass_label in zip(subclasses, labels):
        count+=1
        if limit != None:
            if count>limit: break
        if subclass_label != '':
            print('add->' + subclass_label)
            G.add_node(subclass_id, label=subclass_label)
            G.add_edge(subclass_id, parent_id)
    return subclasses


def get_this_from_this(prop,item):
    query_string = """
    SELECT ?WDid ?label
    WHERE {{
      ?WDid (wdt:{})* wd:{} .
      ?WDid rdfs:label ?label.
      FILTER(LANGMATCHES(LANG(?label), "en"))
    }}
    """.format(
        prop,
        item
    )
    results = return_sparql_query_results(query_string)
    uris = [binding["WDid"]["value"] for binding in results["results"]["bindings"]]
    
    qids = [uri.split("/")[-1] for uri in uris]
    labels = [binding["label"]["value"] for binding in results["results"]["bindings"]]
    return (qids,labels)

def add_from_prop(parent_id, G, prop, limit = 100):
    # Fetch all matters
    subclasses, labels = get_this_from_this(prop, parent_id)
    count=0
    for subclass_id, subclass_label in zip(subclasses, labels):
        count+=1
        if limit != None:
            if count>limit: break
        if subclass_label != '':
            print('add->' + subclass_label)
            G.add_node(subclass_id, label=subclass_label)
            G.add_edge(subclass_id, parent_id)
    return subclasses


#%% some examples

# dl = [get_entity_dict_from_api(subclass_id) for subclass_id in subclasses[:limit]]
# il = [WikidataItem(i) for i in dl]
# labels = [item.get_label() for item in il] 
# get_matters_of_study("Q840400")[1]
get_this_from_this("P2578","Q788926") #study of
get_this_from_this("P2579","Q788926") #studied by

#=== evolutionary biology ===#
code = "Q840400"
r = get_entity_dict_from_api(code) #Q43478
r['labels']['en']['value']

get_this_from_this("P2579", code)[1] # studied by it
get_this_from_this("P31",   code)[1] # instances of it
get_this_from_this("P279",  code)[1] # subclasses of it

get_this_from_this("P361",  code)[1] # parts of it
get_this_from_this("P921",  code)[1] # thing in which is main subject
get_this_from_this("P4224",  code)[1] # 


'''
Q1063
Q1094654
Q43478
Q7150
Q840400
'''


code = 'Q105441712'
get_this_from_this("P921",  code)[1]


#%% Initialize parent node

#Q840400
#Q7150
ECO = "Q840400"
ECO_dict = get_entity_dict_from_api(ECO)
ECO_item = WikidataItem(ECO_dict)
# Initialize a directed graph
G = nx.DiGraph()
G.add_node(ECO, label=ECO_item.get_label())
print( 'initialized parent node \"' + ECO_item.get_label() + '\"')
populated_nodes = []
#%% populate network at random
for i in range(1000):
    unpopulated = list(set(G.nodes()) - set(populated_nodes))
    parent_id = np.random.choice(unpopulated)
    # if parent_id not in populated_nodes:
    print('='*10+" CHOSEN: "+G.nodes[parent_id]['label']+' '+'='*10)
    subclasses = addchildren(parent_id, G,limit=None) # you can change limit to None
    populated_nodes.append(parent_id)
    time.sleep(0.5) # this is to avoid sending too many requests to the server


#%% final changes
# remove self loops
G.remove_edges_from(list(nx.selfloop_edges(nx.Graph(G))))

#%% Plot
# Create a basic graph visualization using networkx and matplotlib
plt.figure(figsize=(12, 12))
# pos = nx.spring_layout(G, seed=42)
# pos = nx.kamada_kawai_layout(G)
# pos = nx.spring_layout(G)
pos = nx.spring_layout(G, k=.4)

labels = dict([(node, data['label']) for node, data in G.nodes(data=True)])
sizes=np.sqrt(list(dict(G.degree()).values()))*200 # or 2000
nx.draw(G, pos, labels=labels, node_size=sizes, edge_color='darkgrey', node_color='lightgreen', font_size=8, font_color='black', with_labels=True)
plt.title("Ecology roadmap")
plt.axis('off')
plt.show()





#%% Save

from os import chdir, environ
from pathlib import Path
import pickle5
import bz2
chdir(environ['HOME'] + '/LAB/MIKI') #this line is for Spyder IDE only
# os.getcwd()
root = Path(".")
obj_path = root / 'obj'

filename='wdgraph_' + ECO_item.get_label() + '.obj'

with bz2.BZ2File(obj_path / filename, 'wb') as f:
    pickle5.dump(G, f)

print ("saved as " + filename)
# with bz2.BZ2File(obj_path / filename, 'rb') as f:
# 	G = pickle5.load(f)
#%%load
with bz2.BZ2File(obj_path / "wdgraph_ecology.obj", 'rb') as f:
 	G = pickle5.load(f)
#%% POPULATE SO "study of"

populated_nodes_SO = []
#%% POPULATE SO "study of"
for i in range(1000):
    unpopulated = list(set(G.nodes()) - set(populated_nodes_SO))
    parent_id = np.random.choice(unpopulated)
    if parent_id not in populated_nodes_SO:
        print('='*10+" CHOSEN: "+G.nodes[parent_id]['label']+' '+'='*10)
        subclasses = addSO(parent_id, G,limit=None) # you can change limit to None
        populated_nodes_SO.append(parent_id)
        # populated_nodes_SO.extend(subclasses) # assuming no subject of study can be the study of another subject
    time.sleep(0.8) # this is to avoid sending too many requests to the server

#%%


#%% populate network from a specific property
pN_P2579=[]
pN_P2578=[]
pN_P361=[]
pN_P31=[]
pN_P279=[]
#%%
timeout = 0.9

while (
list(set(G.nodes()) - set(pN_P2579)) != [] or
list(set(G.nodes()) - set(pN_P2578)) != [] or
list(set(G.nodes()) - set(pN_P361))  != [] or
list(set(G.nodes()) - set(pN_P31))   != [] or
list(set(G.nodes()) - set(pN_P279))  != [] ):
    
    # STUDIED BY
    unpopulated = list(set(G.nodes()) - set(pN_P2579))
    while unpopulated != []:
        unpopulated = list(set(G.nodes()) - set(pN_P2579))
        parent_id = np.random.choice(unpopulated)
        print('\n'+'='*10+" studied by: "+G.nodes[parent_id]['label']+' '+'='*10)
        subclasses = add_from_prop(parent_id, G, "P2579", limit=None) # you can change limit to None
        pN_P2579.append(parent_id)
        time.sleep(timeout) # this is to avoid sending too many requests to the server
    # STUDY OF
    unpopulated = list(set(G.nodes()) - set(pN_P2578))
    while unpopulated != []:
        unpopulated = list(set(G.nodes()) - set(pN_P2578))
        parent_id = np.random.choice(unpopulated)
        print('\n'+'='*10+" studies "+G.nodes[parent_id]['label']+' '+'='*10)
        subclasses = add_from_prop(parent_id, G, "P2578", limit=None) # you can change limit to None
        pN_P2578.append(parent_id)
        time.sleep(timeout) # this is to avoid sending too many requests to the server
    
    # PART OF
    unpopulated = list(set(G.nodes()) - set(pN_P361))
    while unpopulated != []:
        unpopulated = list(set(G.nodes()) - set(pN_P361))
        parent_id = np.random.choice(unpopulated)
        print('\n'+'='*10+" part of "+G.nodes[parent_id]['label']+' '+'='*10)
        subclasses = add_from_prop(parent_id, G, "P361", limit=None) # you can change limit to None
        pN_P361.append(parent_id)
        time.sleep(timeout) # this is to avoid sending too many requests to the server
        
    # INSTANCE OF (BEWARE!)
    # unpopulated = list(set(G.nodes()) - set(pN_P31))
    # while unpopulated != []:
    #     unpopulated = list(set(G.nodes()) - set(pN_P31))
    #     parent_id = np.random.choice(unpopulated)
    #     print('\n'+'='*10+" CHOSEN: "+G.nodes[parent_id]['label']+' '+'='*10)
    #     subclasses = add_from_prop(parent_id, G, "P31", limit=None) # you can change limit to None
    #     pN_P31.append(parent_id)
    #     time.sleep(timeout) # this is to avoid sending too many requests to the server
        
    # SUBCLASS OF
    unpopulated = list(set(G.nodes()) - set(pN_P279))
    while unpopulated != []:
        unpopulated = list(set(G.nodes()) - set(pN_P279))
        parent_id = np.random.choice(unpopulated)
        print('\n'+'='*10+" subclasses of "+G.nodes[parent_id]['label']+' '+'='*10)
        subclasses = add_from_prop(parent_id, G, "P279", limit=None) # you can change limit to None
        pN_P279.append(parent_id)
        time.sleep(timeout) # this is to avoid sending too many requests to the server
    
#%%

tst = get_entity_dict_from_api("P2579")
tst["labels"]['es']['value']
tst_item = WikidataProperty(tst)

