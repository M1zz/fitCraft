import os
import logging
import httplib2
import json
import time
import datetime

from blog.models import Profile
from converter import convert
from googleapiclient.discovery import build
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import CredentialsModel
#from django_sample import settings
from oauth2client.contrib import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.contrib.django_orm import Storage

from django.conf import settings

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), '.', 'client_secrets.json')

FLOW = flow_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/fitness.activity.read',
    #scope='https://www.googleapis.com/auth/plus.me',
    redirect_uri='http://fityou.xyz/google/oauth2callback')

#DATA_SOURCE = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
DATA_SOURCE = "raw:com.google.step_count.delta:com.xiaomi.hm.health:"
#DAY_START =
#DAY_END   =
DATA_SET = "1483228800000000000-1514678400000000000"
update_total_fitPoint = 0
@login_required
def index(request):
    print "DATA_SET",DATA_SET
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, request.user)
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build("fitness", "v1", http=http)
        result = service.users().dataSources().datasets().get(userId='me', dataSourceId=DATA_SOURCE, datasetId=DATA_SET).execute()
        #print json.loads(result)
        json_string = json.dumps(result, encoding='utf-8') 
        print json_string,"?"
        #logging.info(activitylist)
        return render(request, 'plus/welcome.html', {
                    'fitpoint': update_total_fitPoint
                    })


@login_required
def auth_return(request):
    print settings.SECRET_KEY,request.GET['state'],request.user
    if not xsrfutil.validate_token(settings.SECRET_KEY, str(request.GET['state']), request.user):
        return  HttpResponseBadRequest()
    credential = FLOW.step2_exchange(request.GET)
    print credential,request.user
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    storage.put(credential)
    return HttpResponseRedirect("/fitcraft")

@login_required
def xiaomi(request):
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, request.user)
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build("fitness", "v1", http=http)
        
        # get today
        today       = datetime.date.today()
        # get yesterday
        yesterday   = today - datetime.timedelta(1)
        # test
        #yesterday   = today - datetime.timedelta(60)
        yesterday   = yesterday.strftime('%Y-%m-%d')
        
        # variable setting
        update_total_step = 0
        update_total_fitPoint = 0
        fitPoint = 0

        # setting user id
        fit_user_id = request.user.id 
        fit_profile = Profile.objects.get(user_id = fit_user_id)
        old_fitPoint = fit_profile.fitPoint
        old_sync_date = fit_profile.last_sync_date

        #base_date   = old_sync_date
        end_date     = yesterday
        base_date    = old_sync_date
        #test
        base_date    = datetime.date.today() - datetime.timedelta(60)
        #base_date    = old_sync_date - datetime.timedelta(days=9)
        json_string  = ""
        # compare and sync
        
        #DATA_SET = "1483491600000000000-1483574399000000000"
        #DATA_SOURCE = "raw:com.google.step_count.delta:com.xiaomi.hm.health:"               
        #result = service.users().dataSources().datasets().get(userId='me', dataSourceId=DATA_SOURCE, datasetId=DATA_SET).execute()            
        #print "result : ",result
        print "cmp date : ",str(base_date),str(yesterday)+" 00:00:00+00:00"
        
        while str(base_date) != str(yesterday)+" 00:00:00+00:00":

            #setting the date
            year = int(str(base_date)[:4])
            month = int(str(base_date)[5:7])
            day = int(str(base_date)[8:10])

            form_year = str(base_date)[:4]
            form_month = str(base_date)[5:7]
            form_day = str(base_date)[8:10]
        

            time_tuple_start = (year, month, day, 0, 0, 0, 0, 0, 0)
            time_tuple_end = (year, month, day, 23, 59, 59, 0, 0, 0)
            timestamp_start = time.mktime(time_tuple_start)
            timestamp_end = time.mktime(time_tuple_end )
            print year,month,day
            DATA_SET = str(timestamp_start)[:-2]+"000000000"+"-"+str(timestamp_end)[:-2]+"000000000"
            #print "DATA_SET",DATA_SET
            #DATA_SET = "1483228800000000000-1483315199000000000"

            DATA_SOURCE = "raw:com.google.step_count.delta:com.xiaomi.hm.health:" 
            result = service.users().dataSources().datasets().get(userId='me', dataSourceId=DATA_SOURCE, datasetId=DATA_SET).execute()
            #print "result : ",result
            json_string = json.dumps(result, encoding='utf-8') 
            #print "result : ",json_string[154:165]
            empty_day = json_string[154:165]       
            # Check the directory is exist
            user = str(request.user)
            directory = "./fitapp/static/data/"+user
            if not os.path.exists(directory):
                os.makedirs(directory)

            # save file
            name = directory+"/"+str(base_date)[:10]+"_"+"steps_xiomi"+".json"
            f = open(name, 'w')
            f.write(json_string)
            f.close()

            print "convert"
            # conver data
            #while str(base_date) != str(yesterday)+" 00:00:00+00:00":
            total_step = 0
            print "empty_day",empty_day
            if(empty_day != "\"point\": []"):
               try:
                   total_step = convert(form_year,form_month,form_day,"steps",user)
                   print "total_step",total_step
               except:
                   pass
            fitPoint = int(total_step)/500
            update_total_fitPoint = update_total_fitPoint + fitPoint
            print "convert done!"

            # increase a day
            base_date = base_date + datetime.timedelta(days=1)
        
        print "************* start update ***************"
        Profile.objects.filter(user_id=fit_user_id).update(last_sync_date = base_date)
        Profile.objects.filter(user_id=fit_user_id).update(fitPoint = old_fitPoint + update_total_fitPoint)

        #logging.info(activitylist)
        return render(request, 'plus/welcome.html', {
                    'activitylist': json_string,
                    'fitpoint' : update_total_fitPoint,
                    })

@login_required
def googlefit(request):
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, request.user)
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
 
        # Continue to Google fit process
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build("fitness", "v1", http=http)

        # get today
        today       = datetime.date.today()
        # get yesterday
        yesterday   = today + datetime.timedelta(1)
        yesterday   = yesterday.strftime('%Y-%m-%d')
        #yesterday   = today.strftime('%Y-%m-%d')

        # variable setting
        update_total_step = 0
        update_total_fitPoint = 0
        fitPoint = 0

        # setting user id
        fit_user_id = request.user.id 
        fit_profile = Profile.objects.get(user_id = fit_user_id)
        old_fitPoint = fit_profile.fitPoint
        old_sync_date = fit_profile.last_sync_date

        end_date     = yesterday
        base_date    = old_sync_date
        #base_date    = old_sync_date - datetime.timedelta(days=9)
        json_string = ""

        # compare and sync
        print "cmp date : ",str(base_date),str(yesterday)+" 00:00:00+00:00"
        while(str(base_date) != str(yesterday)+" 00:00:00+00:00"):
            # setting user id
            fit_user_id = request.user.id
            fit_profile = Profile.objects.get(user_id = fit_user_id)
            old_fitPoint = fit_profile.fitPoint
            old_sync_date = fit_profile.last_sync_date

            #setting the date
            year = int(str(base_date)[:4])
            month = int(str(base_date)[5:7])
            day = int(str(base_date)[8:10])

            form_year = str(base_date)[:4]
            form_month = str(base_date)[5:7]
            form_day = str(base_date)[8:10]
        

            time_tuple_start = (year, month, day, 0, 0, 0, 0, 0, 0)
            time_tuple_end = (year, month, day, 23, 59, 59, 0, 0, 0)
            timestamp_start = int(time.mktime(time_tuple_start))
            timestamp_end = int(time.mktime(time_tuple_end ))
            print timestamp_start , timestamp_end 

            body = {
                "aggregateBy": [{
                "dataTypeName": "com.google.step_count.delta",
                "dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
            }],
                "bucketByTime": { "durationMillis": 86400000 },
                "startTimeMillis": str(timestamp_start*1000),
                "endTimeMillis": str(timestamp_end*1000)
            }
            fitData = service.users().dataset().aggregate(userId='me',body=body).execute()
            json_string = json.dumps(fitData, encoding='utf-8')
            data = json.loads(json_string)
            total_step = 0
            try:
                total_step = int(data['bucket'][0]['dataset'][0]['point'][0]['value'][0]['intVal'])
            except:
                total_step = 0
            #empty_day = json_string[154:165]
           
            # Check the directory is exist
            user = str(request.user)
            directory = "./fitapp/static/data/"+user
            if not os.path.exists(directory):
                os.makedirs(directory)

            # save file
            name = directory+"/"+str(base_date)[:10]+"_"+"steps_googlefit"+".json"
            f = open(name, 'w')
            f.write(json_string)
            f.close()
            
            fitPoint = int(total_step)/500
            update_total_fitPoint = update_total_fitPoint + fitPoint
            print fitPoint
            print "************* start update ***************"
            Profile.objects.filter(user_id=fit_user_id).update(last_sync_date = base_date)
            Profile.objects.filter(user_id=fit_user_id).update(fitPoint = old_fitPoint + fitPoint)
            # increase a day
            base_date = base_date + datetime.timedelta(days=1)
            old_fitPoint = 0
    if update_total_fitPoint == 0:
        print "nothing to sync!"
        return render(request,'fitapp/sync_nodata.html',{})
    print "************* last update ***************"
    base_date = base_date - datetime.timedelta(days=1)
    Profile.objects.filter(user_id=fit_user_id).update(last_sync_date = base_date)

        #update_total_fitPoint = 5
    #logging.info(activitylist)
    return render(request, 'plus/welcome.html', {
                'step': json_string,
                'fitpoint' : update_total_fitPoint,
                })  					

