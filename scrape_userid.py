import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from urllib2 import urlopen
import re
import os
import time
import datetime
import json
from pymongo import MongoClient
from collections import deque

# Get Steam UserID
# steam_key = os.environ['STEAM_API_KEY']

# In case the network of user ids are exhausted before the target is reached - add a random user id from the following link
def gen_random_users(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    rand_lst = list(soup.find_all(class_ = 'steamurl'))
    rand_lst = [str(x)[-21:-4] for x in rand_lst]
    return rand_lst

# Get all available friends from a user_id, if their profile is public (response = 200)
def get_friends(steam_key, user_id):
    """
    Resets self.uid to a new 17-digit user ID
    Also checks the GetFriendList API for status code 200 (public user)
    or 401 (private user)
    """
    frd_lst = []
    url = "http://api.steampowered.com/ISteamUser/GetFriendList" +\
           "/v0001/?key=" + steam_key + "&steamid=" + user_id +\
          "&relationship=all"
    try:
        response = requests.get(url)
    except requests.ConnectionError:
        time.sleep(5)
        response = requests.get(url)

    if response.status_code == 200:
        url = urlopen(url)
        data = json.loads(url.read())
        for i in xrange(len(data.get('friendslist').get('friends'))):
            uid = str(data.get('friendslist').get('friends')[i].values()[0])
            frd_lst.append(uid)
    return frd_lst

# Generate a set of unique Steam user IDs, iterating through the get_friends function until a certain user count is reached
def gen_user_ids(user_id):

    checked = set()
    num_checked = 1   # My own user id
    randlst = gen_random_users("http://steamrep.com/list/D")

    Q = deque()
    Q.append(user_id)
    for user in randlst:
        Q.append(str(user))

    # Local Machine
    # file_name = '/Users/lawrence.chim/Desktop/Galvanize/Capstone/Data/user_ids_{}.txt'

    # AWS
    file_name = './Data/user_ids_{}.txt'
    cur_file = file_name.format(int(num_checked/1000) + 1)
    f = open(cur_file, 'w+')
    f.write(user_id)
    f.write('\n')

    while Q:
        if num_checked >= 20000:
            return
        else:
            current = Q.popleft()
            if current in checked:
                continue
            checked.add(current)
            for friend in get_friends(steam_key, current):
                if num_checked % 10000 == 0 and num_checked != 0:
                    f.close()
                    if num_checked == 20000:  # Stop condition
                        break
                    cur_file = file_name.format(int(num_checked/10000) + 1)
                    f = open(cur_file, 'w+')
                Q.append(friend)
                f.write(friend)
                f.write('\n')
                f.flush()
                num_checked += 1

'''
Change unix date to regular date
'''
# unix_to_date = datetime.datetime.fromtimestamp(1482535299).strftime('%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    steam_key = os.environ['STEAM_API_KEY']
    user_id = '76561198092289127'
    gen_user_ids(user_id)
