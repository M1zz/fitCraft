# read daily step all user
import os
import datetime
import json

start_day = "2017-01-13"
start_day = datetime.datetime.strptime(start_day, "%Y-%m-%d")

end_day = "2017-01-31"
end_day = datetime.datetime.strptime(end_day, "%Y-%m-%d")

temp_day = start_day
print start_day,end_day

total_step = 0
user_count = 0
step_list = []
user_mount = []
date_list = []

while temp_day != end_day:
    for name in os.listdir("./"):
        try:
            filenames = os.listdir("./"+name)
            #print "**"+name+"**"
            for filename in filenames:
                if str(temp_day)[:10]+"_steps.json" == filename:
                    path = "./"+name+"/"+filename
                    
                    # open json file 
                    f = open(path,'r')
                    js = json.loads(f.read())
                    
                    step = int(js['objects'][0]['value'])
                    print js['objects'][0]['value']
                    if step > 5000:
                        total_step += step
                        user_count += 1
                    #print filename,path
        except:
            pass
    print "total_step : ",total_step
    step_list.append(total_step)
    user_mount.append(user_count)
    date_list.append(str(temp_day)[:10])
    total_step = 0
    user_count = 0    
    temp_day = temp_day + datetime.timedelta(days=1)
    print str(temp_day)[:10]

print step_list
print user_mount

average_list = []
for i in range(len(step_list)):
    if user_mount[i] != 0:
        average_list.append(step_list[i]/user_mount[i])

print average_list
print date_list
# count member
# get daily average

