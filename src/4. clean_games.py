import pandas as pd
import numpy as np
import string
from collections import OrderedDict
import json

'''
Cleans the app list scraped online into a readable format

INPUT: List of all Steam apps (including video trailers, DLC, etc)
OUTPUT: List of Steam games with info such as game price, game type, game genre, etc
'''

df = pd.read_csv('Data/game_data/all_apps.csv')

# Select only game type = game
df = df[df['Game Type'] == 'game']
df['Game Type'] = [string.capwords(x) for x in df['Game Type']]
df = df.drop(['Game DLC', 'Game Free'], axis=1)

# Change formatting of Game Genres
temp = df['Game Genres'].tolist()
temp = [x[1:-1].split(",") for x in temp]
df['Game Genres'] = temp

# Change formatting of Game Cateogory
temp3 = df['Game Category'].tolist()
temp3 = [x[1:-1].split(",") for x in temp3]
df['Game Category'] = temp3

# Change formatting of Game Desc
df['Game Desc'] = df['Game Desc'].fillna('')
df['Game Desc'] = df['Game Desc'].astype('str')
temp4 = []
for desc in df['Game Desc']:
    desc = re.sub('[\n\r\t]', '', str(desc))
    desc = " ".join(desc.split())
    temp4.append(desc)
df['Game Desc'] = temp4

# Change Release Date to Release Year
df['Release Date'] = df['Release Date'].fillna('')
df = df[df['Release Date'] != 'Soon']
df = df[df['Release Date'] != 'Coming Soon']
df = df[df['Release Date'] != '2017']
df = df[~df['Release Date'].str.contains("(?i)Q|Early|Coming")]

dates = df['Release Date'].tolist()
dates = [x.replace(',','') for x in dates]
dates = [x.split() for x in dates]
for date in dates:
    for item in date:
        if len(item) <= 2:
            date.remove(item)
dates = [' '.join(x) for x in dates]
df['Release Date'] = dates

clean = []
for y in df['Game Category']:
    clean2 = []
    for x in y:
        clean2.append(x.replace('\xef\xbb\xbf',''))
    clean.append(clean2)
df['Game Category'] = clean

audio = []
for x in df['Game Genres']:
    checked = 0
    for y in x:
        if 'audio' in y.lower():
            audio.append(1)
            checked +=1
            break
    if checked != 0:
        continue
    else:
        audio.append(0)

sound = []
for x in df['Game Title']:
    if 'sound' in x.lower():
        sound.append(1)
    else:
        sound.append(0)

multi = []
for x in df['Game Category']:
    checked = 0
    for y in x:
        if 'multi' in y.lower() or 'co-op' in y.lower():
            multi.append(1)
            checked +=1
            break
    if checked != 0:
        continue
    else:
        multi.append(0)

single = []
for x in df['Game Category']:
    checked = 0
    for y in x:
        if 'single' in y.lower():
            single.append(1)
            checked +=1
            break
    if checked != 0:
        continue
    else:
        single.append(0)

df['Multiplayer'] = multi
df['Singleplayer'] = single
df['Single_or_Multi'] = np.logical_or(multi,single)*1
df['Audio'] = audio

df = df[df['Single_or_Multi'] != 0]
df = df[df['Audio'] == 0]
df = df.reset_index(['Game ID'])
df = df.drop(['index','Initial Price','Single_or_Multi', 'Audio'], axis=1)

df2 = pd.read_csv('Data/game_data/game_tags.csv')
df = pd.merge(df, df2, on='Game ID')

id_ = df['Game ID'].tolist()
title = df['Game Title'].tolist()
multiplay = df['Multiplayer'].tolist()
d = OrderedDict()
d.update(zip(id_, zip(title, multiplay)))

with open('Data/game_data/game_dict.json', 'w') as f:
    json.dump(d, f)

df.to_csv('Data/game_data/gameslist.csv', index=0)
