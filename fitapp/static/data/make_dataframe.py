import os
import datetime
import json
from pandas import Series, DataFrame
import pandas as pd

start_day = "2017-01-13"
start_day = datetime.datetime.strptime(start_day, "%Y-%m-%d")

end_day = "2017-02-01"
end_day = datetime.datetime.strptime(end_day, "%Y-%m-%d")

temp_day = start_day

# initialize
username_list = []
date_list = []

temp_list = []

integrate_data = DataFrame(columns=('user','date','step','playtime'))
# example form of dataframe
#integrate_data.loc[0] = ['mizz','2017-01-01',2341,231]
#print integrate_data

# get all nick name from directory
for name in os.listdir("./"):
    if str(name)[-3:] != ".py" and str(name)[-4:] != ".swp":
        username_list.append(str(name))
print username_list,len(username_list)


# search in all day
while temp_day != end_day:
    date_list.append(temp_day.strftime("%Y-%m-%d"))
    temp_day = temp_day + datetime.timedelta(days=1)
print date_list , len(date_list)


count = 0
# create dataframe
for name in username_list:
    for date in date_list:
        try:
            filenames = os.listdir("./"+name)
            # read only that day
            for filename in filenames:
                if filename == date+"_steps.json":
                    path = "./"+name+"/"+filename
                    #print path
                    f = open(path,'r')
                    js = json.loads(f.read())
                    
                    step = int(js['objects']['activities-steps'][0]['value'])
                    #print step
                    f.close()

                    print name, date, step, count
                    temp_list.append(name)
                    temp_list.append(date)
                    temp_list.append(step)
                    
                    #print "***",temp_list,"\n"

                    integrate_data.loc[count] = temp_list
                    count = count + 1
                    temp_list = []
          
            for :
            temp_list.append(name)
            temp_list.append(date)
            temp_list.append(step)
                    
            #print "***",temp_list,"\n"

            integrate_data.loc[count] = temp_list
            count = count + 1
            temp_list = []
 
                    
        except:
            pass
print integrate_data 
# get each data from health data

# get each data from game log
