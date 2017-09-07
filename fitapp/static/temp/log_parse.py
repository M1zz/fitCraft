# -*- coding: utf8 -*-
import csv
import pandas as pd
from pandas import Series, DataFrame
# Read log

# parse log

# hyunsoo = 0
# hyunho = 1
# hyunkyu = 2
# hyunsik = 3
# woosik = 4
# jonghyun = 5

#work_log_dataframe = pd.read_csv('test.csv')
#print work_log_dataframe['DATE'][0]
#print str(work_log_dataframe['DATE'])[16:18]
#print work_log_dataframe['WORKER']
log_user = []
log_hour = []
log_value = []

for user in range(1,7):
    for hour in range(1,25):
        log_user.append(user)
        log_hour.append(hour)
        log_value.append(0)

raw_data = {'day': log_user,
            'hour': log_hour,
            'value': log_value}

csv_data = (DataFrame(raw_data))

hour = []
user = []
name = []

work_log_dataframe = pd.read_csv('test.csv',sep=',',header=None)
print work_log_dataframe
work_log_dataframe.columns = ["DATE", "WORKER"]

#print csv_data
print work_log_dataframe

for date in work_log_dataframe['DATE']:
    hour.append(str(date)[11:13])
#print hour
for w_user in work_log_dataframe['WORKER']:
    name = str(w_user).translate(None,",'{}")
    user.append(name)

#print user[1]

for data in range(len(hour)):
    member = user[data].split()
    log_hour = int(hour[data])-1
    for number in range(len(member)):
        if member[number] == "문현수":
            csv_data['value'][24*0+log_hour] += 1
        if member[number] == "이현호":
            csv_data['value'][24*1+log_hour] += 1
        if member[number] == "남현규":
            csv_data['value'][24*2+log_hour] += 1
        if member[number] == "유현식":
            csv_data['value'][24*3+log_hour] += 1
        if member[number] == "정우식":
            csv_data['value'][24*4+log_hour] += 1
        if member[number] == "박종현":
            csv_data['value'][24*5+log_hour] += 1


# make tsv

analyzed_data = csv_data.columns[0] +"\t"+csv_data.columns[1]+"\t"+csv_data.columns[2]+"\n"

print len(csv_data.values)

for value in range(len(csv_data.values)):
    print (csv_data.values[value])
    for number in range(len(csv_data.values[value])):
        analyzed_data = analyzed_data + str(csv_data.values[value][number])
        if int(number - 2) == 0 :
            analyzed_data = analyzed_data + "\n"
        else :
            analyzed_data = analyzed_data + "\t"

print analyzed_data

f = open('data.tsv', 'w')
#csv_data = DataFrame.to_csv(csv_data,sep='\t', na_rep='NaN')
f.write(str(analyzed_data))

f.close()

