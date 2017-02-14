import pandas as pd
import graphlab as gl
import os
import requests
import time
import json
from ast import literal_eval

'''
Gets top 100 recommendations for both ranking matrix factorization models
INPUT: A path to text file containing sample user IDs
OUTPUT: List of sample user IDs, list of sample user IDs and their top 100
        recommendations provided by the model
'''
def get_top_recs(samp_path, model_path):

    model = gl.load_model(model_path)
    model.recommend()

    sample = []
    with open(samp_path) as f:
        for samp in f.read().splitlines():
            sample.append(samp)

    rec_list = []
    for s in sample:
        recs = model.get_similar_users([int(s)], 100)
        rec_list.append({s:list(recs['similar'])})
    return sample, rec_list

'''
Make requests to the Steam API to get a list of friends for each user
INPUT: A path to text file containing sample user IDs
OUTPUT: List of sample user IDs, list of sample user IDs and friends on Steam
'''
def get_friends(samp_path, steam_key):
    i = 0

    sample = []
    with open(samp_path) as f:
        for samp in f.read().splitlines():
            sample.append(samp)

    samp_list = []
    for s in sample:
        if i % 200 == 0 and i != 0:
            time.sleep(300)
        i += 1

        url = "http://api.steampowered.com/ISteamUser/GetFriendList" +\
              "/v0001/?key=" + steam_key + "&steamid=" + str(s) +\
              "&relationship=all"
        try:
            response = requests.get(url)
        except requests.ConnectionError:
            time.sleep(5)
            response = requests.get(url)

        if response.status_code == 200:
            url = urlopen(url)
            data = json.loads(url.read())
            frd_lst = []
            for i in xrange(len(data.get('friendslist').get('friends'))):
                uid = str(data.get('friendslist').get('friends')[i].values()[0])
                frd_lst.append(int(uid))
            if not frd_lst:
                samp_list.append({s: list()})
            else:
                samp_list.append({s: frd_lst})
        else:
            samp_list.append({s: list()})

    print "Length of sample" + str(len(sample))
    print "Length of friendlist" + str(len(samp_list))

    return sample, samp_list


'''
Evaluate the performance of the base rating model and the random rating model
INPUT: A DataFrame with recommendations made by both models, and ther
       actual friends each user has
OUTPUT: Scores each user to see if the top 100 users recommended by both models
        matches actual experience
'''
def score(df):

    ids = df['Sample ID'].tolist()
    model1 = df['model1'].tolist()
    model1 = [literal_eval(x) for x in model1]
    model2 = df['model2'].tolist()
    model2 = [literal_eval(x) for x in model2]
    actual = df['friend'].tolist()
    actual = [literal_eval(x) for x in actual]
    length = [1 if len(l) >= 10 else 0 for l in actual]
    score1 = []
    score2 = []

    for i in xrange(len(actual)):
        for j in xrange(len(actual[i])):
            if j in model1[i].values()[0]:
                score1.append(1)
                continue
        score1.append(0)

    for i in xrange(len(actual)):
        for j in xrange(len(actual[i])):
            if j in model2[i].values()[0]:
                score2.append(1)
                continue
        score2.append(0)

    df['score1'] = score1
    df['score2'] = score2

    return df

if __name__ == '__main__':
    sample1, m1_recs = get_top_recs('Data/user_data/sample_users_evaluation.txt', \
                                    'Modelling/model_v1/rankfactor_rec_model')
    sample2, m2_recs = get_top_recs('Data/user_data/sample.txt', \
                                    'Modelling/model_v2/rankfactor_rec_random')
    df = pd.DataFrame(columns=['Sample ID', 'model1'])
    df['Sample ID'] = sample1
    df['Sample ID'] = df['Sample ID'].astype('str')
    df['model1'] = m1_recs
    df2 = pd.DataFrame(columns=['Sample ID', 'model2'])
    df2['Sample ID'] = sample2
    df2['Sample ID'] = df2['Sample ID'].astype('str')
    df2['model2'] = m2_recs
    df = pd.merge(df, df2, how='left', left_on='Sample ID', right_on='Sample ID')

    sample3, friends = get_friends('Data/user_data/sample.txt', \
                                    os.environ['STEAM_API_KEY'])
    df3 = pd.DataFrame(columns=['Sample ID', 'Friends List'])
    df3['Sample ID'] = sample3
    df3['Sample ID'] = df3['Sample ID'].astype('str')
    df3['Friends List'] = friends
    df = pd.merge(df, df3, how='left', left_on='Sample ID', right_on ='Sample ID')

    df_final = score(df)
    df_final.to_csv('final_evaluation.csv', index=0)
