import json
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
from ast import literal_eval
import os
from glob import glob


'''
This program will convert json files to a pandas df row
'''
def json_to_df(filepath):
    contents = []
    json_dir_name = "sample_json/"
    # json_dir_name = "s3://steam-recommender/Data/json_batch1"
    json_pattern = os.path.join(json_dir_name) + '*.json'
    fileslist = glob(json_pattern)
    i = 0
    for files in fileslist:
        with open(files) as f:
            data = literal_eval(f.read())
            j = json.dumps(data)
            if j.get('response') = {}:
                continue
            else:
                df = pd.read_json(j)

            i +=1
