import pandas as pd
import json

'''
Apply dimensionality reduction to reduce the subset of games. Based on the
following metric:

    # minutes played for game across all owners / # owners < 30

INPUT: Long form data (user, games, time played) with all games
OUTPUT: Long form data (user, games, time played) with games meeting threshold
'''
def reduce_dim(df):

    num_games_before = len(set(df['appid'].tolist()))
    num_users_before = len(set(df['userid'].tolist()))
    df = df[df['threshold'] > 30]
    num_games_after = len(set(df['appid'].tolist()))
    num_users_after = len(set(df['userid'].tolist()))

    print "Number of users before: " + str(num_users_before)
    print "Number of users after: " + str(num_users_after)
    print str((num_users_before - num_users_after)) + ' users removed'
    print '----'  * 10
    print "Number of apps before: " + str(num_games_before)
    print "Number of apps after: " + str(num_games_after)
    print str((num_games_before - num_games_after)) + ' games removed'

    reduced_games = sorted(list(set(df['appid'].tolist())))

    with open('Data/games_final.txt','w') as f:
        for games in reduced_games:
            f.write('{}'.format(games))
            f.write('\n')

    return df

'''
Eliminate all games where time spent is 0 minutes
'''
def get_pct_time_played(df):

    df = df[['userid', 'appid', 'total_mins', 'total_mins_2weeks']]
    df = df[df['total_mins'] != 0]

    df['userid'] = df['userid'].astype('int').astype('str')
    df['appid'] = df['appid'].astype('int').astype('str')

    df['total_owners'] = 1
    df2 = df[['appid','total_owners', 'total_mins']]
    df2.rename(columns={'total_mins' : 'total_min_played_all'}, inplace=True)
    df.drop('total_owners', axis=1, inplace=True)
    df2 = df2.groupby('appid').sum().reset_index()
    df2['grand_total_min_played'] = (df2.groupby('appid')\
                                    ['total_min_played_all'].sum()).sum()
    df = pd.merge(df, df2, how='left', left_on='appid', right_on = 'appid')

    df['games_per_user'] = 1
    df3 = df[['userid','games_per_user']]
    df.drop('games_per_user', axis=1, inplace=True)
    df3 = df3.groupby('userid').sum().reset_index()
    df = pd.merge(df, df3, how='left', left_on='userid', right_on = 'userid')

    df4 = df[['userid', 'total_mins', 'total_mins_2weeks']]
    df4.rename(columns={'total_mins' : 'total_mins_user'}, inplace=True)
    df4.rename(columns={'total_mins_2weeks' : 'total_mins_2weeks_user'}, \
               inplace=True)
    df4 = df4.groupby('userid').sum().reset_index()
    df = pd.merge(df, df4, how='left', left_on='userid', right_on = 'userid')

    df['percentage_played'] = df['total_mins']*1.0 / df['total_mins_user']*1.0
    tot_mins = df['total_mins_2weeks'].tolist()
    tot_mins_user = df['total_mins_2weeks_user'].tolist()
    ratio = [tot_mins[i]*1.0/tot_mins_user[i]*1.0 if tot_mins_user[i] !=0 \
             else 0 for i in xrange(len(tot_mins))]
    df['percentage_played_2weeks'] = ratio

    df = df[['userid','appid','total_mins','total_mins_2weeks', 'total_owners',\
             'total_min_played_all','games_per_user', 'total_mins_user', \
             'total_mins_2weeks_user', 'percentage_played', \
             'percentage_played_2weeks', 'grand_total_min_played']]

    return df

if __name__ == '__main__':
    df = pd.read_csv('Data/user_item_rating_model.csv')
    df2 = reduce_dim(df)
    df_transformed = get_pct_time_played(df2)
    df_transformed.to_csv('Data/model_data/model_v1/all_model_data.csv', \
                          index=False)
