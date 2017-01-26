from bs4 import BeautifulSoup
import requests
from urllib2 import urlopen
import json
import pandas as pd
import numpy as np
import re
import boto
from boto.s3.key import Key
from threading import Thread
import os
import time

def read_10_users(start, stepsize):
    userlist = []
    for i in xrange(start,start+stepsize):
        link = 'Data/user_ids/user_ids_{}.txt'.format(i)
        with open(link, 'r') as f:
            for line in f:
                userlist.append(line.split('\n')[0])
    return userlist

def get_game(userlist, bucket_name, steam_key):
    '''
    user = user_id
    bucket = something like a file object that could be passed onto json.dump function
    '''
    access_key = os.environ['AWS_ACCESS_KEY']
    access_secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
    i = 0
    for user in userlist:
        url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key='+\
        steam_key + '&steamid=' + user + '&include_appinfo=1&include_played'+\
        '_free_games=1&format=json'
        try:
            url = urlopen(url)
        except urllib2.URLError:
            time.sleep(5)
            url = urlopen(url)
        i += 1
        user_id = {'userid':user}
        user_gamelist = json.loads(url.read())
        user_gamelist.update(user_id)
        json_str = str(user_gamelist)

        if i % 200 == 0:
            print str(i) + "files have been downloaded"
            time.sleep(300)
        else:
            conn = boto.connect_s3(access_key, access_secret_key)
            if conn.lookup(bucket_name) is None:
                bucket = conn.create_bucket(bucket_name, policy='public-read')
            else:
                bucket = conn.get_bucket(bucket_name)
            k = Key(bucket)
            filename = 'user_'+ user +'_games.json'
            k.key = 'Data/RK/'+filename
            result = k.set_contents_from_string(json_str)

if __name__ == '__main__':
    users_1 = read_10_users(51,60)
    # Make 1000 threads
    steam_keys = [os.environ['STEAM_API_KEY'], os.environ['STEAM_API_KEY_BK'], \
                 os.environ['STEAM_API_KEY_ZR'], os.environ['STEAM_API_KEY_TN'], \
                 os.environ['STEAM_API_KEY_JV'], os.environ['STEAM_API_KEY_RK'], \
                 os.environ['STEAM_API_KEY_CC']]
    get_game(users_1, 'steam-recommender', steam_keys[5])
