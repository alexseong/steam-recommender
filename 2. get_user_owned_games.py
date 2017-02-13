from bs4 import BeautifulSoup
from urllib2 import urlopen, URLError, HTTPError
import json
import boto
from boto.s3.key import Key
import os
import time

'''
Reads a text file containing unique Steam User IDs and return it as a list
INPUT: Textfile containing 100,000 Steam User IDs
OUTPUT: List of Steam User IDs
'''
def read_users(start):
    userlist = []
    for i in xrange(start,start+1):
        link = 'Data/user_data/user_ids_{}.txt'.format(i)
        with open(link, 'r') as f:
            for line in f:
                userlist.append(line.split('\n')[0])
    return userlist

'''
Make a Steam API call to get a list of owned games for each Steam User ID given.
It will store this information as a JSON file inside a specified AWS S3 bucket

INPUT: List of Steam user IDs, AWS S3 bucket name to store json files, and a
       Steam API Key
'''
def get_game(userlist, bucket_name, steam_key):
    access_key = os.environ['AWS_ACCESS_KEY']
    access_secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
    i = 0
    for user in userlist:
        if i % 200 == 0 and i != 0:
            print str(i) + "files have been downloaded"
            time.sleep(300)

        url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key='+\
        steam_key + '&steamid=' + user + '&include_appinfo=1&include_played'+\
        '_free_games=1&format=json'

        user_id = {'userid':user}
        user_gamelist = json.loads(urlopen(url).read())
        user_gamelist.update(user_id)
        json_str = str(user_gamelist)

        conn = boto.connect_s3(access_key, access_secret_key)
        if conn.lookup(bucket_name) is None:
            bucket = conn.create_bucket(bucket_name, policy='public-read')
        else:
            bucket = conn.get_bucket(bucket_name)
        k = Key(bucket)
        filename = user+'.json'
        k.key = 'Data/json_batch_files/' + filename
        result = k.set_contents_from_string(json_str)
        i += 1

if __name__ == '__main__':
    users_1 = read_users(1)
    steam_key = os.environ['STEAM_API_KEY']
    get_game(users_1, 'steam-recommender', steam_key)
