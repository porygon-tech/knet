#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 12:35:11 2024

@author: roman
"""


from qwikidata.entity import WikidataItem
from qwikidata.json_dump import WikidataJsonDump
from qwikidata.utils import dump_entities_to_json

from qwikidata.entity import WikidataItem, WikidataLexeme, WikidataProperty
from qwikidata.linked_data_interface import get_entity_dict_from_api
from qwikidata.sparql import (get_subclasses_of_item,
                              return_sparql_query_results)

import networkx as nx
import matplotlib.pyplot as plt
from qwikidata.sparql import get_subclasses_of_item
import numpy as np
import time

from os import chdir, environ
from pathlib import Path
import pickle5
import bz2
root = Path(".")
obj_path = root / 'data/obj'
img_path = root / 'img'
metadata_path = root / 'data/metadata'


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

#%%
import json
import requests
def apiquery(searchterm,language="en", limit = 7):
    url = "https://www.wikidata.org/w/api.php?action=wbsearchentities&limit="+str(limit)+"&format=json&search=" + searchterm + "&language=" + language
    r = requests.get(url)
    j = r.json()
    return j["search"]

#%%
print("="*30+"\nLoad project [0] or generate from scratch[1]?")
while True:
    try:
        generate = int(input()) # ex. 1000
        if generate == 0 or generate == 1:
            break
    except:    
        pass

    print ('\nIncorrect input, try again')

#%%
from os import listdir
import re
if generate == 1:
    #/////////////////////////////
    query = input("Query term: ") # term to populate the network (ex. "evolutionary biology")
    nres = 20                      # number of results from the query
    #/////////////////////////////
    
    results = apiquery(query,limit = nres)
    # results[0]
    for i, r in enumerate(results): 
        if 'description' in r.keys(): 
            print("[" + str(i) + "]\t" + r['id'] + ": \t" + r['description'])
    print("="*30+"\nSelect query result from above (enter number and press intro):")
    
    DAD = results[int(input())]['id'] # parent term from which to populate
    DAD_dict = get_entity_dict_from_api(DAD)
    DAD_item = WikidataItem(DAD_dict)
    easyname = DAD_item.get_label()
    # Initialize a directed graph
    G = nx.DiGraph()
    G.add_node(DAD, label=easyname)
    print( 'initialized parent node \"' + easyname + '\"')
    populated_nodes = []
elif generate == 0:
    lproj = listdir(obj_path)
    for i, r in enumerate(lproj): 
        print("[" + str(i) + "]\t" + r)
    print("="*30+"\nSelect project from above (enter number and press intro):")
    filename = lproj[int(input())]
    pattern = r'wdgraph_(.*?).obj'
    easyname = re.search(pattern, filename).group(1)
    with bz2.BZ2File(obj_path / filename, 'rb') as f:
     	G = pickle5.load(f)
    print("loaded project for " + easyname)
    
    populated_nodes = [] # !!!!!!!!!!!!!!!!!! will be deprecated soon


#%% populate network at random (subclasses)
print("="*30+"\nEnter No. of nodes to populate:")
while True:
    try:
        npop = int(input("-> ")) # ex. 1000
        break
    except:    
        pass

    print ('\nIncorrect input, try again')

for i in range(npop):
    unpopulated = list(set(G.nodes()) - set(populated_nodes))
    if len(unpopulated) ==0: 
        print("Early termination: Graph is fully populated.")
        break
    parent_id = np.random.choice(unpopulated)
    # if parent_id not in populated_nodes:
    print('='*10+" CHOSEN: "+G.nodes[parent_id]['label']+' '+'='*10)
    subclasses = addchildren(parent_id, G,limit=None) # you can change limit to None
    populated_nodes.append(parent_id)
    time.sleep(0.5) # this is to avoid sending too many requests to the server


#%% populate network from multiple properties
while True:
    choice_superpopulate = input("="*30+"\nPopulate further using other properties? [y/n]")
    if choice_superpopulate == 'n':
        break
    elif choice_superpopulate == 'y':
        language='en'
        properties_ids = (
        'P2579', # studied in
        'P2578', # is the study of
        'P361',  # part of
        #'P31',   # instance of is sometimes too profuse
        'P279'   # subclass of
        )
        
        properties_labels={}
        if generate == 1:
            populated_P = {} # dict of populated nodes for each property
            unpopulated_P={}
            for prop in properties_ids:
                tst = get_entity_dict_from_api(prop)
                populated_P[prop]= []
                unpopulated_P[prop]= []
                properties_labels[prop] = tst["labels"][language]['value']
                
        elif generate == 0:
            try:
                with bz2.BZ2File(metadata_path / easyname +"_populated_P.obj", 'rb') as f:
                 	populated_P = pickle5.load(f)
            except:    
                populated_P ={}
                for prop in properties_ids:
                    populated_P[prop]= []
            unpopulated_P={}
            for prop in properties_ids:
                tst = get_entity_dict_from_api(prop)
                unpopulated_P[prop]= []
                properties_labels[prop] = tst["labels"][language]['value']
        
        timeout = 0.8
        print('properties to explore:\n-\t'+'\n-\t'.join(properties_labels.values()))
        for i in range(npop):
            for prop in properties_ids:
                unpopulated_P[prop] = list(set(G.nodes()) - set(populated_P[prop]))
                if unpopulated_P[prop] == []: 
                    print("Early termination on category '"+prop+"': Graph is currently fully populated for that property.")
                else:
                    unpopulated_P[prop] = list(set(G.nodes()) - set(populated_P[prop]))
                    parent_id = np.random.choice(unpopulated_P[prop])
                    print('\n'+'='*10+" "+properties_labels[prop]+": "+G.nodes[parent_id]['label']+' '+'='*10)
                    subclasses = add_from_prop(parent_id, G, prop, limit=None) # you can change limit to None
                    populated_P[prop].append(parent_id)
                    time.sleep(timeout) # this is to avoid sending too many requests to the server
        break
    print ('\nIncorrect input, try again')


#%% final changes
# remove self loops
G.remove_edges_from(list(nx.selfloop_edges(nx.Graph(G))))

#%%

#chdir(environ['HOME'] + '/LAB/MIKI') #this line is for Spyder IDE only
# os.getcwd()

filename='wdgraph_' + easyname + '.obj'
metadataname = easyname +"_populated_P.obj"
with bz2.BZ2File(metadata_path / metadataname, 'wb') as f:
    pickle5.dump(G, f)

with bz2.BZ2File(obj_path / filename, 'wb') as f:
    pickle5.dump(G, f)

print ("-"*30+"\nSaved network as " + filename)
# with bz2.BZ2File(obj_path / filename, 'rb') as f:
# 	G = pickle5.load(f)

#%% Plot
timecode = str(time.ctime().replace(' ','_').replace(':','_'))
while True:
    choice_display = input("="*30+"\nDisplay network of "+ str(len(G.nodes())) + " nodes? [y/n]")
    if choice_display == 'y':
        figname = ('plot_' + easyname + '_'+timecode+'.pdf').replace(' ','_')
        # Create a basic graph visualization using networkx and matplotlib
        fig = plt.figure(figsize=(12, 12)); ax = fig.add_subplot(111)
        # pos = nx.spring_layout(G, seed=42)
        # pos = nx.kamada_kawai_layout(G)
        # pos = nx.spring_layout(G)
        pos = nx.spring_layout(G, k=.4)
        
        labels = dict([(node, data['label']) for node, data in G.nodes(data=True)])
        sizes=np.sqrt(list(dict(G.degree()).values()))*200 # or 2000
        nx.draw_networkx(G, ax=ax, pos=pos, labels=labels, node_size=sizes, edge_color='darkgrey', node_color='lightgreen', font_size=8, font_color='black', with_labels=True)


        #plt.title("Ecology roadmap")
        #plt.axis('off')
        fig.savefig(str(img_path / figname))
        print ("saved image as " + figname)
        break
    elif choice_display == 'n':
        break
    print ('\nIncorrect input, try again')
        






