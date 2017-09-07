import pandas as pd
from pandas import DataFrame, Series
import os, os.path
import json

#TODO:Get daily sleep data

path = './static/data/'

total = 0

dataframe = DataFrame()
userIdList = [folderId for folderId in os.listdir(path) if os.path.isdir(path+folderId)]

for userId in userIdList:
    objectFileList = [filename for filename in os.listdir(path+userId)
                      if filename.endswith('sleep.json')]
    print userId, total
    total = 0 
    for dailyFileName in objectFileList:
        entireFile = pd.read_json(path+userId+'/'+dailyFileName, typ = 'Series')
        userPath = path+userId+'/'
        if "errors" in entireFile:
            continue
        #TODO:Calculate
        
        try:
            json_data=open(userPath + dailyFileName).read()
            data = json.loads(json_data)
        
            total += int(data['objects']['sleep'][0]['timeInBed'])
        except:
            #print "No data"
            pass
     
    print userId, total 
