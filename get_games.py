
from bs4 import BeautifulSoup
import requests
from urllib2 import urlopen
from collections import OrderedDict
import json
import pandas as pd
import re
import time

def get_gameslist():
    gamelist = pd.DataFrame(columns=['App_ID', 'Title', 'App_Type'])
    app_id = []
    app_title = []
    url = urlopen('http://api.steampowered.com/ISteamApps/GetAppList/v0001/')
    games = json.loads(url.read())
    for ind in xrange(len(games['applist']['apps'].values()[0])):
        app_id.append(int(games['applist']['apps'].values()[0][ind]['appid']))
        app_title.append(str(games['applist']['apps'].values()[0][ind]['name'].encode('ascii', 'ignore')))
    gamelist['App_ID'] = app_id
    gamelist['Title'] = app_title
    return gamelist

def label_games(gameslist):
    types = []
    for i in xrange(len(gameslist['App_ID'])):
        url = 'https://steamdb.info/app/'+ str(gameslist['App_ID'][i])
        try:
            html = requests.get(url).text
        except requests.ConnectionError:
            time.sleep(5)
            html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        app_type = str(soup.find(itemprop = 'applicationCategory'))
        patt = re.compile(r'<.*?>')
        app_type = patt.sub('', app_type)
        types.append(app_type)
    gameslist['App_Type'] = types
    return gameslist

def write_games(df,path):
    return df.to_csv(path)

if __name__ == '__main__':
    gameslist = get_gameslist()
    allgames = label_games(gameslist)
    write_games(allgames, 'Data/games.csv')
