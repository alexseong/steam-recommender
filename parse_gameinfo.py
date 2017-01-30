# -*- coding: utf-8 -*-
import requests
import json
import pandas as pd
import numpy as np
import boto
from boto.s3.key import Key
import time
import re
import unicodedata
from urllib2 import urlopen

def get_gameids():
    game_ids = []
    game_titles = []
    url = 'http://api.steampowered.com/ISteamApps/GetAppList/v2/'
    response = requests.get(url)
    result = response.json()
    num_games = result.values()[-1].values()[-1]
    for i in xrange(len(num_games)):
        gameid = result.values()[-1].values()[-1][i].values()[-1]
        game_ids.append(gameid)
        gametitle = result.values()[-1].values()[-1][i].values()[0]
        game_titles.append(gametitle)
    df = pd.DataFrame({'Game ID': game_ids, 'Game Title': game_titles})
    return df

def parse(game_info):
    i = 0
    url = 'http://store.steampowered.com/api/appdetails'
    payload = {}
    data_df = game_info
    games = data_df['Game ID'].tolist()
    game_titles = data_df['Game Title'].tolist()
    game_type = []
    game_desc = []
    game_img = []
    game_DLC = []
    game_free = []
    game_price_final = []
    game_price_init = []
    game_meta_rating = []
    game_category = []
    game_genre = []
    game_release = []

    for game in games:
        if i % 200 == 0 and i != 0:
            print str(i) + ' games have been processed!'
            data_df2 = pd.DataFrame()
            data_df2['Game ID'] = games[:i]
            data_df2['Game Title'] = game_titles[:i]
            data_df2['Game Type'] = game_type
            data_df2['Game Desc'] = game_desc
            data_df2['Initial Price'] = game_price_init
            data_df2['Final Price'] = game_price_final
            data_df2['Release Date'] = game_release
            data_df2['Game Free'] = game_free
            data_df2['Img URL'] = game_img
            data_df2['Game DLC'] = game_DLC
            data_df2['Metacritic Rating'] = game_meta_rating
            data_df2['Game Category'] = game_category
            data_df2['Game Genres'] = game_genre
            data_df2.to_csv('Data/game_info_{}.csv'.format(i/200), index=False, encoding='utf-8')
            time.sleep(300)

        payload['appids'] = game
        response = requests.get(url, params=payload)
        result = response.json()
        print str(games[i]) + ' --- ' + str(i)
        success = result.values()[-1]['success']

        if success:
            game_type.append(str(result.values()[-1]['data']['type']))
            game_free.append(result.values()[-1]['data']['is_free'])

            try:
                game_price_final.append((result.values()[-1]['data']['price_overview']['final'])/100.)
                game_price_init.append((result.values()[-1]['data']['price_overview']['initial'])/100.)
            except KeyError:
                game_price_final.append(0)
                game_price_init.append(0)

            try:
                game_meta_rating.append(result.values()[-1]['data']['metacritic']['score'])
            except KeyError:
                game_meta_rating.append(0)

            try:
                game_release.append(str(result.values()[-1]['data']['release_date']['date']))
            except (KeyError, UnicodeEncodeError):
                game_release.append('')

            try:
                cats = []
                for j, cat in enumerate(result.values()[-1]['data']['categories']):
                    cats.append(str(result.values()[-1]['data']['categories'][j]['description']))
                game_category.append(cats)
            except KeyError:
                game_category.append([])

            try:
                genres = []
                for k, genre in enumerate(result.values()[-1]['data']['genres']):
                    genres.append(str(result.values()[-1]['data']['genres'][k]['description']))
                game_genre.append(genres)
            except KeyError:
                game_genre.append([])

            try:
                game_img.append(str(result.values()[-1]['data']['header_image']))
            except KeyError:
                game_img.append('')

            try:
                game_text = result.values()[-1]['data']['detailed_description']
                game_text = unicodedata.normalize('NFKD', game_text).encode('ascii','ignore')
                game_text = re.sub("<.*?>", "", game_text)
                game_text = re.sub("\t", "", game_text)
                game_desc.append(game_text)
            except (KeyError,UnicodeEncodeError):
                game_text = ''
                game_desc.append(game_text)

            try:
                game_DLC.append(result.values()[-1]['data']['dlc'])
            except KeyError:
                game_DLC.append([])

        else:
            game_type.append('')
            game_free.append('')
            game_img.append('')
            game_desc.append('')
            game_DLC.append([])
            game_price_final.append(0)
            game_price_init.append(0)
            game_meta_rating.append(0)
            game_release.append('')
            game_category.append([])
            game_genre.append([])

        i += 1

    data_df['Game Type'] = game_type
    data_df['Game Desc'] = game_desc
    data_df['Initial Price'] = game_price_init
    data_df['Final Price'] = game_price_final
    data_df['Release Date'] = game_release
    data_df['Game Free'] = game_free
    data_df['Img URL'] = game_img
    data_df['Game DLC'] = game_DLC
    data_df['Metacritic Rating'] = game_meta_rating
    data_df['Game Category'] = game_category
    data_df['Game Genres'] = game_genre
    data_df.to_csv('Data/game_info.csv', index=False, encoding='utf-8')
    return data_df

if __name__ == '__main__':
    game_ids = get_gameids()
    games_df = parse(game_ids)
    print games_df
