import json
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
from ast import literal_eval
import os
from glob2 import glob, iglob
from math import ceil

'''
INPUT: Filepath contain all json files to be converted
OUTPUT: Pandas Dataframe containing all games owned by a user, as well as time
        (in minutes) played
'''
def conv_json_to_df(filepath):
    json_pattern = os.path.join(filepath) + '*.json'
    fileslist = glob(json_pattern)
    i = 0
    num_json = len(fileslist)
    df = pd.DataFrame()
    user_ids = []
    all_games = pd.read_csv('Data/game_data/gameslist_v2.csv')
    all_games = all_games['Game ID'].tolist()

    for files in fileslist:
        if i % 10000 == 0 and i != 0:
            print str(i) +' records has been processed!'
        with open(files) as f:
            data = literal_eval(f.read())
            i += 1
            if 'games' not in data['response']:
                continue
            user_ids.append(data['userid'])
            df_temp = json_normalize(data['response'], 'games')
            try:
                df_temp['playtime_2weeks'].fillna(0, inplace=True)
            except KeyError:
                df_temp['playtime_2weeks'] = 0

            df_temp['userid'] = data['userid']
            df_temp.rename(columns={'playtime_forever' : 'total_mins'}, \
                           inplace=True)
            df_temp.rename(columns={'playtime_2weeks' : 'total_mins_2weeks'}, \
                           inplace=True)
            df_temp = df_temp[df_temp['appid'].isin(all_games)]
            df_temp = df_temp[['userid','appid','total_mins', 'total_mins_2weeks']]

            if df.empty:
                df = pd.DataFrame(columns = df_temp.columns)
                df['userid'].astype('str')
                df['appid'].astype('str')
            df = df.append(df_temp)
        if i % 10000 == 0 or i == num_json:
            df.to_csv(filepath + 'users_owned_games_{}.csv' \
                      .format(int(ceil(i/10000.0))), index=False)
            df = df[0:0]
    if i == num_json:
        with open('Data/user_data/all_users.txt','w') as f:
            for item in user_ids:
                f.write(item)
                f.write('\n')
    return df

'''
INPUT: A filepath to read all CSV files and a df to pivot the results
OUTPUT: A pivoted dataframe with list of games as columns
'''
def combine_csv(filepath):
    json_pattern = os.path.join(filepath) + '*.csv'
    fileslist = glob(json_pattern)
    df = pd.DataFrame()
    for files in fileslist:
        df_temp = pd.read_csv(files, dtype={'userid':str,'appid':str})
        if df.empty:
            df = pd.DataFrame(columns = df_temp.columns)
        df = df.append(df_temp)

    df['userid'] = df['userid'].astype('str')
    df['appid'] = df['appid'].astype('int').astype('str')

    df['total_owners'] = 1
    df2 = df[['appid','total_owners', 'total_mins']]
    df2.rename(columns={'total_mins' : 'total_min_played_all'}, inplace=True)
    df.drop('total_owners', axis=1, inplace=True)
    df2 = df2.groupby('appid').sum().reset_index()
    df = pd.merge(df, df2, how='left', left_on='appid', right_on = 'appid')
    df['threshold'] = df['total_min_played_all']* 1.0 / df['total_owners']* 1.0

    df = df[['userid','appid','total_mins','total_mins_2weeks', 'total_owners',\
             'total_min_played_all', 'threshold']]
    return df

if __name__ == '__main__':
    df = conv_json_to_df('Data/json_batch_files/')
    df_T.to_csv('Data/user_item_rating_model.csv', index=False)
