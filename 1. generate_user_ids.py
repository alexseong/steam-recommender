import requests
from bs4 import BeautifulSoup
from urllib2 import urlopen
import os
import time
import json
from collections import deque

'''
Get all available friends from a user_id, if their profile is publicly visible
INPUT: Steam API Key, a Steam User ID
OUTPUT: A list of friends corresponding to the User ID provided
'''
def get_friends(steam_key, user_id):
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

'''
Adds an additional 539 unique Steam User IDs to the queue in case the below
program stops before reaching 1,000,000 Steam User IDs
INPUT: URL containing these extra 539 Steam User IDs
OUTPUT: list of 539 Steam User IDs to be added onto the queue
'''
def gen_random_users(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    rand_lst = list(soup.find_all(class_ = 'steamurl'))
    rand_lst = [str(x)[-21:-4] for x in rand_lst]
    return rand_lst

'''
Using an iterative approach, generate a list of 1,000,000 unique Steam User IDs
INPUT: One sample Steam User ID to begin the program
OUTPUT: Ten text files of length 100,000 containing unique Steam User IDs
'''
def gen_user_ids(user_id):

    checked = set()
    num_requests = 0
    randlst = gen_random_users("http://steamrep.com/list/D")

    Q = deque()
    Q.append(user_id)
    for user in randlst:
        Q.append(str(user))

    while Q:
        if len(checked) >= 1000000:
            break
        if num_requests % 200 == 0 and num_requests != 0:
            print str(num_requests) + ' requests has been made, \
                                        will sleep for 5 minutes!'
            print str(len(checked)) + ' number of users scraped'
            time.sleep(300)
        current = Q.popleft()

        for friend in get_friends(steam_key, current):
            if friend in checked:
                continue
            Q.append(friend)
            checked.add(friend)
        num_requests +=1

    check_list = list(checked)
    file_name = './Data/user_ids_{}.txt'
    cur_file = file_name.format(1)
    f = open(cur_file, 'w+')
    count_files = 0

    for item in check_list:
        f.write(item)
        f.write('\n')
        count_files += 1
        if count_files % 100000 == 0:
            f.close()
            cur_file = file_name.format(int(count_files/100000) + 1)
            f = open(cur_file, 'w+')


if __name__ == '__main__':
    steam_key = os.environ['STEAM_API_KEY']
    user_id = 'XXXXXXXXXXXXXXXXX'
    gen_user_ids(user_id)
