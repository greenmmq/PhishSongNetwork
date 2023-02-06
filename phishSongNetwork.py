import json
import networkx as nx
import numpy as np
import pandas as pd
import pprint
import requests

print("Getting Setlist Data...")
# songNetwork API Key - get one for free on: https://phish.net/api
apiKey = 'YOUR API KEY HERE' 

# get song data
songLink = 'https://api.phish.net/v5/songs.json?apikey='+apiKey
songFile = requests.get(songLink)
songData = json.loads(songFile.text)['data']
songDf = pd.DataFrame({
    'songid':[int(s['songid']) for s in songData],
    'song':[s['song'] for s in songData],
    'artist':[s['artist'] for s in songData],
    'times_played':[int(s['times_played']) for s in songData],
    'debut':[s['debut'] for s in songData]
})
songDf['index'] = songDf.index
songDict = songDf.set_index('songid').T.to_dict()

# get show data
showLink = 'https://api.phish.net/v5/shows.json?apikey='+apiKey
showFile = requests.get(showLink)
showDict = json.loads(showFile.text)['data']
shows = [sh['showid'] for sh in showDict]
# get single setlist data
# showDate = '1997-11-22'
# setLink = 'https://api.phish.net/v5/setlists/showdate/'+showDate+'.json?apikey='+apiKey

setLink = 'https://api.phish.net/v5/setlists.json?apikey='+apiKey
setFile = requests.get(setLink)
setDict = json.loads(setFile.text)['data']
# pprint.pprint(setdict)

print("Complete!")
print("---")
print("Creating Adjacency Matrix...")

# create adjacency matrix
a_mat = np.zeros((songDf.shape[0], songDf.shape[0]))
for show in shows:
    setBreakdown = {s['songid']: s['set'] for s in setDict if s['showid'] == show}

    # breakdown the songlists for each set of the show
    setList = {}
    for pair in setBreakdown.items():
        if pair[1] not in setList.keys():
            setList[pair[1]] = []
        try:
            setList[pair[1]].append(songDict[int(pair[0])]['index'])
        except KeyError:
            pass

    # increment adjacency matrix weight by 1 for songs played next to each other in a setlist
    for pair in setList.items():
        for i in range(0,len(pair[1])-1):
            if i==0:
                a_mat[pair[1][i]][[pair[1][i+1]]] += 1
            elif iter==len(pair[1])-1:
                a_mat[pair[1][i]][[pair[1][i-1]]] += 1
            else:
                a_mat[pair[1][i]][[pair[1][i+1]]] += 1
                a_mat[pair[1][i]][[pair[1][i-1]]] += 1


print("Complete!")
print("---")
print("Building Graph...")

# build the graph
G = nx.from_pandas_adjacency(pd.DataFrame(a_mat))
nx.set_node_attributes(G, songDf.to_dict('index'))
nx.write_gexf(G, 'phishsongs.gexf')

print("Complete!")

# nx.draw(G)

