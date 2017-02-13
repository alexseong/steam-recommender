import graphlab as gl

model_train = gl.SFrame.read_csv('Modelling/model_v1/model_train.csv')
random_train = gl.SFrame.read_csv('Modelling/model_v2/random_train.csv')

'''Model 1 - Ratings based on percentage of time spent'''
model1 = gl.ranking_factorization_recommender.create(observation_data=model_train,
                                                    num_factors=10,
                                                    user_id='userid',
                                                    item_id='appid',
                                                    target='rating_model1',
                                                    solver='sgd',
                                                    verbose=True)

'''Model 2 - Ratings are randomly imputed'''
model2 = gl.ranking_factorization_recommender.create(observation_data=random_train,
                                                     num_factors=10,
                                                     user_id='userid',
                                                     item_id='appid',
                                                     target='rating_model2',
                                                     solver='sgd',
                                                     verbose=True)


model1.save('rankfactor_rec_model')
model2.save('rankfactor_rec_random')
