import pandas as pd
import numpy as np
from collections import OrderedDict
import graphlab as gl

'''
INPUT: DataFrame including info on time spent per game per user
OUTPUT: Dataframe with ratings associated with percentage time spent on one game
        (base model), and ratings that are randomly generated (random model)
'''
def fill_ratings(path):

    df = pd.read_csv(path, index_col=False)
    ratinglist = []

    user_dict = df.set_index('userid')['games_per_user'].to_dict()
    user_dict = OrderedDict(sorted(user_dict.items()))
    users, num_games = zip(*user_dict.items())

    df = df.sort_values(by = ['userid','appid'], ascending=[True,True])

    i = 0
    while i < len(num_games):
        ratinglist.extend((np.random.dirichlet(np.ones(num_games[i]),size=1)))
        i +=1
    ratinglist = [item for sublist in ratinglist for item in sublist]

    # Model 1 - Ratings are dependent on percentage of total time played
    df.rename(columns={'percentage_played' : 'rating_model1'}, inplace=True)

    # Model 2 - Ratings are randomly computed
    df['rating_model2'] = ratinglist

    df = df[['userid','appid','rating_model1','rating_model2']]
    return df


'''
Splits the Graphlab SFrame into train and test sets
'''
def train_test_split(dataframe):
    dataframe = gl.SFrame(dataframe)
    train, test = gl.recommender.util.random_split_by_user(dataframe, 'userid',\
                  'appid', max_num_users=150000)
    return train, test

if __name__ == '__main__':
    df = fill_ratings('Data/model_data/model_v1/all_model_data.csv')
    train, test = train_test_split(df)
    model_train = train[['userid','appid','rating_model1']]
    random_train = train[['userid','appid','rating_model2']]
    model_test = test[['userid','appid','rating_model1']]
    random_test = test[['userid','appid','rating_model2']]
    model_train.export_csv('Modelling/model_v1/model_train.csv')
    model_test.export_csv('Modelling/model_v1/model_test.csv')
    random_train.export_csv('Modelling/model_v2/random_train.csv')
    random_test.export_csv('Modelling/model_v2/random_test.csv')
