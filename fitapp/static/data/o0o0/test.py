import json
from pprint import pprint

with open('2017-01-22_steps.json') as data_file:    
    data = json.load(data_file)

print data['objects']['activities-steps'][0]['value']
