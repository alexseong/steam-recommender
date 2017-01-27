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
    # json_dir_name = "sample_json/"
    # json_dir_name = "s3://steam-recommender/Data/json_batch1"
    json_pattern = os.path.join(filepath) + '*.json'
    fileslist = glob(json_pattern)
    i = 0
    num_json = len(fileslist)
    df = pd.DataFrame()
    for files in fileslist:
        with open(files) as f:
            data = literal_eval(f.read())
            i += 1
            if data['response'] == {}:
                continue
            else:
                df_temp = json_normalize(data['response'], 'games')
                df_temp['userid'] = data['userid']
                df_temp.rename(columns={ 'playtime_forever' : 'play_hrs'}, inplace=True)
                df_temp['play_hrs'] = df_temp['play_hrs'] / 60.0
                df_temp = df_temp[['userid','appid','play_hrs']]
                if df.empty:
                    df = pd.DataFrame(columns = df_temp.columns)
                df = df.append(df_temp)
        if i % 100000 == 0 or i == num_json:
            df.to_csv(filepath + 'users_owned_games_{}.csv'.format(int(ceil(i/100000.0))), \
            index=False, float_format='%0.2f')
            df = df[0:0]
    return df

'''
INPUT: A filepath to read all CSV files and a df to pivot the results
OUTPUT: A pivoted dataframe with list of games as columns
'''
def pivot_data(filepath, df):
    # json_pattern = os.path.join(filepath) + '*. csv'
    # fileslist = glob(json_pattern)
    # df = pd.DataFrame()
    # for files in fileslist:
    #     df_temp = df.read_csv(files)
    #     if df.empty:
    #         df = pd.DataFrame(columns = df_temp.columns)
    #     df = df.append(df_temp)
    #
    # df['has_'] = 1
    # df = df[['userid', 'appid','has_','']
    # df.pivot
    pass

if __name__ == '__main__':
    df = conv_json_to_df('sample_json/')
    # df_T = binarize_data('sample_json/', df)
