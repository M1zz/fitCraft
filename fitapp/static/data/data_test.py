import json
import os

json_data=open("2017-04-08_sleep.json").read()
#json_data_heart=open("2017-03-29_heart.json").read()
data = json.loads(json_data)

#print data['objects']['activities-heart'][0]['value']['heartRateZones'][1]['minutes']
print data['objects']['sleep'][0]['timeInBed']

objectFileList = [filename for filename in os.listdir('./') if filename.endswith('steps.json')]
print objectFileList


step = 0
total = 0
for filename in objectFileList:
    json_data=open(filename).read()
    data = json.loads(json_data)
    step = data['objects']['activities-steps'][0]['value']
    total += int(step)
print total/500
