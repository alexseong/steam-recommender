import requests
from bs4 import BeautifulSoup
from urllib2 import urlopen
import re
import time
import pandas as pd

'''
Reads the game IDs of all Steam games and outputs it onto a list
'''
def read_games():
    games = []
    with open('Data/game_data/games.txt', 'r') as f:
        for line in f:
            games.append(line.split('\n')[0])
    return games

'''
Get the top 5 community rated tags for each game
INPUT: List of games IDs
OUTPUT: List of games with a list of community rated tags in CSV format
'''
def scrape_tags(game_listing):
    cookies = {"birthtime": "568022401"}
    df = pd.DataFrame(columns = ['Game ID','Game Tags'])
    i = 0
    df['Game ID'] = game_listing
    game_tags = []

    for game in game_listing:
        if i % 200 == 0 and i != 0:
            print str(i) + ' games have been scraped!'
            time.sleep(300)
        try:
            all_tags = []
            url = 'http://store.steampowered.com/app/' + str(game)
            html = requests.get(url, cookies=cookies).text
            soup = BeautifulSoup(html, 'html.parser')
            tags = list(soup.find_all(lambda tag: tag.name == 'a' and \
                   tag.get('class') == ['app_tag']))
            for tag in tags:
                tag = re.sub('<[^>]*>', '', str(tag))
                tag = re.sub('[\n\r\t]', '', tag)
                all_tags.append(tag)
            if len(all_tags) > 5:
                all_tags = all_tags[:5]
            game_tags.append(all_tags)

        except (IndexError, KeyError, ConnectionError, ValueError):
            game_tags.append([])

        i += 1

    df['Game Tags'] = game_tags
    df.to_csv('Data/game_data/game_tags.csv', index=False)

if __name__ == '__main__':
    gameslist = read_games()
    scrape_tags(gameslist)
