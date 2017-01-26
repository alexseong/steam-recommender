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
import datetime

def read_10_users(start, stepsize):
    userlist = []
    for i in xrange(start,start+stepsize):
        link = 'Data/user_ids/user_ids_{}.txt'.format(i)
        with open(link, 'r') as f:
            for line in f:
                userlist.append(line.split('\n')[0])
    return userlist

def parallelize_task(userlist, bucket_name, steam_key):
    threads = [Thread(target=get_game, args=(user, bucket_name, steam_key)) for user in userlist]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def get_game(user, bucket_name, steam_key):
    '''
    user = user_id
    bucket = something like a file object that could be passed onto json.dump function
    '''
    access_key = os.environ['AWS_ACCESS_KEY']
    access_secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
    url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key='+\
    steam_key + '&steamid=' + user + '&include_appinfo=1&include_played'+\
    '_free_games=1&format=json'
    try:
        url = urlopen(url)
    except urllib2.URLError:
        time.sleep(5)
        url = urlopen(url)
    user_id = {'userid':user}
    user_gamelist = json.loads(url.read())
    user_gamelist.update(user_id)
    json_str = str(user_gamelist)

    conn = boto.connect_s3(access_key, access_secret_key)
    if conn.lookup(bucket_name) is None:
        bucket = conn.create_bucket(bucket_name, policy='public-read', region = 'us-east-1')
    else:
        bucket = conn.get_bucket(bucket_name)

    k = Key(bucket)
    filename = 'user_'+ user +'_games.json'
    k.key = 'Data/JV/'+filename
    result = k.set_contents_from_string(json_str)

if __name__ == '__main__':
    users_1 = read_10_users(41,50)
    num_users = len(users_1)
    # Make 1000 threads
    step_size = 400
    steam_keys = [os.environ['STEAM_API_KEY'], os.environ['STEAM_API_KEY_BK'], \
                 os.environ['STEAM_API_KEY_ZR'], os.environ['STEAM_API_KEY_TN'], \
                 os.environ['STEAM_API_KEY_JV'], os.environ['STEAM_API_KEY_RK'], \
                 os.environ['STEAM_API_KEY_CC']]
    start = datetime.now()
    print start
    for index in xrange(0, num_users+1, step_size):
        parallelize_task(users_1[:index+400], 'steam-recommender', steam_keys[4])
    print 'Time taken: ' + (datetime.now()-start)
