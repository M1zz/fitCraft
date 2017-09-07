import json
import datetime
from datetime import timedelta

user = "mizzzzzz"
def convert(year,month,day,resource, user):
    base_date = str(year)+"-"+str(month)+"-"+str(day)
    # file open
    directory = "./fitapp/static/data/"+user
    filename = directory+"/"+base_date+"_"+"steps_xiaomi.json"
    f = open(filename,'r')
    # read json
    health_data = json.loads(f.read())
    print "count of object : ",len(health_data['point'])
    count = len(health_data['point'])
    total_step = 0
    timecheck = []
    interval_check = []
    value_check = []
    for i in range(count):
        start_timestamp = int(str(health_data['point'][i]['startTimeNanos'])[:-9])+32400
        datetimeobj_start = datetime.datetime.fromtimestamp(start_timestamp)
        
        end_timestamp = int(str(health_data['point'][i]['endTimeNanos'])[:-9])+32400
        datetimeobj_end = datetime.datetime.fromtimestamp(end_timestamp)
        start_datetime = str(datetimeobj_start)[11:17]+"00"
        #print "start time : ",start_datetime
        end_datetime = str(datetimeobj_end)[11:17]+"00"
        #print "end time : ",end_datetime
        
        timecheck.append(start_datetime)
        #timecheck.append(end_datetime)     

        result = datetimeobj_end - datetimeobj_start
        interval = (result.seconds/60)
        interval_check.append(interval)
        #print "interval : ",interval

        value = int(health_data['point'][i]['value'][0]['intVal'])
        value_check.append(value)
        #print i,"value : ",value,"\n"

        total_step += value

    print "total_step : ",total_step
    if (len(timecheck) > 0):
        timecheck[0] = "00:00:00"
    print "timecheck : ",timecheck,len(timecheck)
    print "interval_check :",interval_check,len(interval_check)
    print "value_check :",value_check,len(value_check)
    timestamp_start = datetime.datetime(int(year), int(month), int(day), 0, 0, 0)
 
    print "timestamp_start",timestamp_start
    
    # convert to fitbit form
    header = "{\"meta\": {\"total_count\": 2, \"status_code\": 100}, \"objects\": {\"activities-steps-intraday\": {\"datasetType\": \"minute\", \"datasetInterval\": 1, \"dataset\": ["
    match = -1
    body = ""
    # {"value": 0, "time": "23:58:00"}, {"value": 0, "time": "23:59:00"}
    for i in range(1439):
        # conver data
        if timecheck.count(str(timestamp_start)[11:]) != 0:
            match += 1
            #print "match : ",match
        body += "{\"value\":"+str(int(value_check[match]/interval_check[match]))+", \"time\":\""+str(timestamp_start)[11:]+"\"},"
        #print body 
        # increase time
        timestamp_start += datetime.timedelta(minutes=1)
        #print str(timestamp_start)[11:]

    footer = "]}, \"activities-steps\": [{\"value\": \""+str(total_step)+"\", \"dateTime\": \""+base_date+"\"}]}}"

    #print header,footer
    # store data
    data = header + body[:-1] + footer
    # save file
    name = directory+"/"+base_date+"_xiomi_steps"+".json"
    f = open(name, 'w')
    f.write(data)
    f.close()
   
    return total_step 
