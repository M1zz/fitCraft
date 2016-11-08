#from django import forms
#from . import utils
import json

def extract_daily_step(directory, filename):
    step = "letter"+'\t'+"frequency"+'\n'
    print directory,filename
    
    f = open(filename, 'r')
    js = json.loads(f.read())
    f.close()

    daily_step  = js['objects']
    for token in daily_step:
        step = step + str(token['dateTime'])[8:10]
        step = step + '\t'
        step = step + str(token['value']) + '\n'
    #print step
    extract_filename = str(token['dateTime'])[0:7]+".tsv"
    f = open(directory+"/"+extract_filename, 'w')
    f.write(step)
    f.close()

