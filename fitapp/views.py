import json
import os
import datetime
#from datetime import date, timedelta

# added
from django.contrib import auth

from django.db import models
from blog.models import Profile
#import fitbit
from dateutil import parser
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from six import string_types

from fitbit.exceptions import (HTTPUnauthorized, HTTPForbidden, HTTPConflict,
                               HTTPServerError)

from . import forms
# for the extraction step
from extract_daily_step import extract_daily_step
from . import utils
from .models import UserFitbit, TimeSeriesData, TimeSeriesDataType
from .tasks import get_time_series_data, subscribe, unsubscribe


@login_required
def login(request):
    """
    Begins the OAuth authentication process by obtaining a Request Token from
    Fitbit and redirecting the user to the Fitbit site for authorization.

    When the user has finished at the Fitbit site, they will be redirected
    to the :py:func:`fitapp.views.complete` view.

    If 'next' is provided in the GET data, it is saved in the session so the
    :py:func:`fitapp.views.complete` view can redirect the user to that URL
    upon successful authentication.

    URL name:
        `fitbit-login`
    """
    next_url = request.GET.get('next', None)
    # check the url
    print "next_url : ",next_url
    # userless
    """
    if next_url:
        request.session['fitbit_next'] = next_url
    else:
        request.session.pop('fitbit_next', None)
    """

    #callback_uri = request.build_absolute_uri(reverse('fitbit-complete'))
    callback_uri = "http://fityou.xyz/fitapp/complete/"
    fb = utils.create_fitbit(callback_uri=callback_uri)
    token_url, code = fb.client.authorize_token_url(redirect_uri=callback_uri)
    
    #complete
    if (callback_uri == "http://www.fityou.xyz/fitapp/complete/"):
        callback_uri = "http://fityou.xyz/fitapp/complete/"
        print "modified_callback_uri : ",callback_uri
    #print "token_url : ",token_url
    
    print "redirect"
    return redirect(token_url)


@login_required
def complete(request):
    """
    After the user authorizes us, Fitbit sends a callback to this URL to
    complete authentication.

    If there was an error, the user is redirected again to the `error` view.

    If the authorization was successful, the credentials are stored for us to
    use later, and the user is redirected. If 'next_url' is in the request
    session, the user is redirected to that URL. Otherwise, they are
    redirected to the URL specified by the setting
    :ref:`FITAPP_LOGIN_REDIRECT`.

    If :ref:`FITAPP_SUBSCRIBE` is set to True, add a subscription to user
    data at this time.

    URL name:
        `fitbit-complete`
    """
    try:
        code = request.GET['code']
        print "code : ",code
    except KeyError:
        print "KeyError",KeyError
        return redirect(reverse('fitbit-error'))

    callback_uri = request.build_absolute_uri(reverse('fitbit-complete'))
    fb = utils.create_fitbit(callback_uri=callback_uri)
    print "callback_uri : ",callback_uri
    try:
        token = fb.client.fetch_access_token(code, callback_uri)
        print token
        access_token = token['access_token']
        fitbit_user = token['user_id']
        print "access_token : ",access_token
        print "fitbit_user : ",fitbit_user
    except KeyError:
        print "fitbit-error"
        return redirect(reverse('fitbit-error'))

    if UserFitbit.objects.filter(fitbit_user=fitbit_user).exists():
        # if exist update
        UserFitbit.objects.filter(fitbit_user=fitbit_user).update(access_token = access_token)
        print "fitbit-exist"
        return redirect(reverse('fitbit-today-steps'))

    fbuser, _ = UserFitbit.objects.get_or_create(user=request.user)
    fbuser.access_token = access_token
    fbuser.fitbit_user = fitbit_user
    fbuser.refresh_token = token['refresh_token']
    fbuser.save()
    
    print "check!"

    # Add the Fitbit user info to the session
    request.session['fitbit_profile'] = fb.user_profile_get()
    if utils.get_setting('FITAPP_SUBSCRIBE'):
        try:
            SUBSCRIBER_ID = utils.get_setting('FITAPP_SUBSCRIBER_ID')
        except ImproperlyConfigured:
            return redirect(reverse('fitbit-error'))
        subscribe.apply_async((fbuser.fitbit_user, SUBSCRIBER_ID), countdown=5)
        # Create tasks for all data in all data types
        for i, _type in enumerate(TimeSeriesDataType.objects.all()):
            # Delay execution for a few seconds to speed up response
            # Offset each call by 2 seconds so they don't bog down the server
            get_time_series_data.apply_async(
                (fbuser.fitbit_user, _type.category, _type.resource,),
                countdown=10 + (i * 5))

    next_url = request.session.pop('fitbit_next', None) or utils.get_setting(
        'FITAPP_LOGIN_REDIRECT')
    return redirect(next_url)


@receiver(user_logged_in)
def create_fitbit_session(sender, request, user, **kwargs):
    """ If the user is a fitbit user, update the profile in the session. """

    if user.is_authenticated() and utils.is_integrated(user) and \
            user.is_active:
        fbuser = UserFitbit.objects.filter(user=user)
        if fbuser.exists():
            fb = utils.create_fitbit(**fbuser[0].get_user_data())
            try:
                request.session['fitbit_profile'] = fb.user_profile_get()
            except:
                pass

@login_required
def exist(request):
    return render(request, 'fitapp/exist.html', {}) 

def home(request):
    return render(request, 'fitapp/home_admin.html', {})

def howto(request):
    return render(request, 'fitapp/howto.html', {})

def fitbit(request):
    return render(request, 'fitapp/fitbit.html', {})

def xiaomi(request):
    return render(request, 'fitapp/xiaomi.html', {})

def googlefit(request):
    return render(request, 'fitapp/googlefit.html', {})

def item(request):
    return render(request, 'fitapp/item.html', {})

def worklog(request):
    return render(request, 'fitapp/work_log.html', {})

@login_required
def error(request):
    """
    The user is redirected to this view if we encounter an error acquiring
    their Fitbit credentials. It renders the template defined in the setting
    :ref:`FITAPP_ERROR_TEMPLATE`. The default template, located at
    *fitapp/error.html*, simply informs the user of the error::

        <html>
            <head>
                <title>Fitbit Authentication Error</title>
            </head>
            <body>
                <h1>Fitbit Authentication Error</h1>

                <p>We encontered an error while attempting to authenticate you
                through Fitbit.</p>
            </body>
        </html>

    URL name:
        `fitbit-error`
    """
    return render(request, utils.get_setting('FITAPP_ERROR_TEMPLATE'), {})


@login_required
def logout(request):
    """Forget this user's Fitbit credentials.

    If the request has a `next` parameter, the user is redirected to that URL.
    Otherwise, they're redirected to the URL defined in the setting
    :ref:`FITAPP_LOGOUT_REDIRECT`.

    URL name:
        `fitbit-logout`
    """
    user = request.user
    try:
        fbuser = user.userfitbit
    except UserFitbit.DoesNotExist:
        pass
    else:
        if utils.get_setting('FITAPP_SUBSCRIBE'):
            try:
                SUBSCRIBER_ID = utils.get_setting('FITAPP_SUBSCRIBER_ID')
            except ImproperlyConfigured:
                return redirect(reverse('fitbit-error'))
            unsubscribe.apply_async(kwargs=fbuser.get_user_data(), countdown=5)
        fbuser.delete()
    next_url = request.GET.get('next', None) or utils.get_setting(
        'FITAPP_LOGOUT_REDIRECT')
    return redirect(next_url)


@csrf_exempt
def update(request):
    """Receive notification from Fitbit or verify subscriber endpoint.

    Loop through the updates and create celery tasks to get the data.
    More information here:
    https://wiki.fitbit.com/display/API/Fitbit+Subscriptions+API

    For verification, we expect two GET requests:
    1. Contains a verify query param containing the verification code we
       have specified in the ``FITAPP_VERIFICATION_CODE`` setting. We should
       respond with a HTTP 204 code.
    2. Contains a verify query param containing a purposefully invalid
       verification code. We should respond with a 404
    More information here:
    https://dev.fitbit.com/docs/subscriptions/#verify-a-subscriber

    URL name:
        `fitbit-update`
    """

    # The updates can come in two ways:
    # 1. A json body in a POST request
    # 2. A json file in a form POST
    print "Update user data!"
    if request.method == 'POST':
        try:
            body = request.body
            if request.FILES and 'updates' in request.FILES:
                body = request.FILES['updates'].read()
            updates = json.loads(body.decode('utf8'))
        except json.JSONDecodeError:
            raise Http404

        try:
            # Create a celery task for each data type in the update
            for update in updates:
                cat = getattr(TimeSeriesDataType, update['collectionType'])
                resources = TimeSeriesDataType.objects.filter(category=cat)
                for i, _type in enumerate(resources):
                    # Offset each call by 2 seconds so they don't bog down the
                    # server
                    get_time_series_data.apply_async(
                        (update['ownerId'], _type.category, _type.resource,),
                        {'date': parser.parse(update['date'])},
                        countdown=(2 * i))
        except (KeyError, ValueError, OverflowError):
            raise Http404

        return HttpResponse(status=204)
    elif request.method == 'GET':
        # Verify fitbit subscriber endpoints
        verification_code = utils.get_setting('FITAPP_VERIFICATION_CODE')
        verify = request.GET.get('verify', None)
        if verify and verify == verification_code:
            return HttpResponse(status=204)

    # if someone enters the url into the browser, raise a 404
    raise Http404


def make_response(code=None, objects=[]):
    """AJAX helper method to generate a response"""

    data = {
        'meta': {'total_count': len(objects), 'status_code': code},
        'objects': objects,
    }
    return HttpResponse(json.dumps(data))


def normalize_date_range(request, fitbit_data):
    """Prepare a fitbit date range for django database access. """

    result = {}
    base_date = fitbit_data['base_date']
    if base_date == 'today':
        now = timezone.now()
        if 'fitbit_profile' in request.session.keys():
            tz = request.session['fitbit_profile']['user']['timezone']
            now = timezone.pytz.timezone(tz).normalize(timezone.now())
        base_date = now.date().strftime('%Y-%m-%d')
    result['date__gte'] = base_date

    if 'end_date' in fitbit_data.keys():
        result['date__lte'] = fitbit_data['end_date']
    else:
        period = fitbit_data['period']
        if period != 'max':
            if isinstance(base_date, string_types):
                start = parser.parse(base_date)
            else:
                start = base_date
            if 'y' in period:
                kwargs = {'years': int(period.replace('y', ''))}
            elif 'm' in period:
                kwargs = {'months': int(period.replace('m', ''))}
            elif 'w' in period:
                kwargs = {'weeks': int(period.replace('w', ''))}
            elif 'd' in period:
                kwargs = {'days': int(period.replace('d', ''))}
            end_date = start + relativedelta(**kwargs)
            result['date__lte'] = end_date.strftime('%Y-%m-%d')

    return result


@require_GET
def get_steps(request):
    """An AJAX view that retrieves this user's step data from Fitbit.

    This view has been deprecated. Use `get_data` instead.

    URL name:
        `fitbit-steps`
    """
    # save step data
    user = str(request.user)
    directory = "./fitapp/static/data/"+user
    if not os.path.exists(directory):
        os.makedirs(directory)

    base_date = request.GET.get('base_date', None)
    print "base_date : ",base_date
    period = request.GET.get('period', None)
    print "period : ",period
    end_date = request.GET.get('end_date', None)
    print "end_date : ",end_date

    health_step = get_data(request, 'activities', 'steps')
    #print "asdfdasf",str(health_step).split('\n')[2]i
    health_step = str(health_step).split('\n')[2]
    name = directory+"/"+user+"_"+str(base_date)+"_"+str(end_date)+".json"
    f = open(name, 'w')
    f.write(health_step)
    f.close()

    # directory , read_filename
    extract_daily_step(directory, name)
    return get_data(request, 'activities', 'steps')

@require_GET
def all_get_today_steps(request):
    
    update_total_step = 0
    update_total_fitPoint = 0    
    #print "object : ",Profile._meta.get_all_field_names()
    #print Profile.objects.values('id') , len(Profile.objects.values('id'))
    #print Profile.objects.values('id')[0]
    

    print "object : ",UserFitbit._meta.get_all_field_names()
    #print UserFitbit.objects.values('id')
    #print UserFitbit.objects.values('user')
    #print UserFitbit.objects.values('user_id')
    #print UserFitbit.objects.values('fitbit_user')
    #print UserFitbit.objects.values('user_id')[0].values()
    #print UserFitbit.objects.get(user_id = fit_user_id)
  
    user_list = UserFitbit.objects.values('user_id')
    user_id = []
    #for name in 

    print user_list
 
    for user in user_list:
        user_id.append(user.values()[0])

    print "name : ",user_id

    for user in user_id:
        print user

        #TODO set the User and Id
        fit_user_id = user
        user = UserFitbit.objects.get(user_id = fit_user_id)
        fitbit_id = UserFitbit.objects.values('fitbit_user')[0].values()[0]
        print "update all id : ",user,fit_user_id

        #TODO set the date
        # Search from database
        old_fitPoint = 0
        fit_profile = Profile.objects.get(user_id = fit_user_id)
        old_fitPoint = fit_profile.fitPoint
        old_sync_date = fit_profile.last_sync_date
        print "old_fitPoint : ",old_fitPoint,old_sync_date
    
        # calculate and set yesterday
        today       = datetime.date.today()
        yesterday   = today - datetime.timedelta(1)
        yesterday   = yesterday.strftime('%Y-%m-%d')

        # setting the searching date
        base_date   = old_sync_date
        period      = request.GET.get('period', None)
        end_date    = yesterday
        print "base_date : ",base_date
        print "yesterday : ",yesterday
        # last sycn , yesterday to sync all data from last sync date

        fbuser = UserFitbit.objects.get(user=fit_user_id)
        fitbit_user = fbuser.fitbit_user
        access_token = fbuser.access_token
        print "fitbit_user_id : ",fitbit_user

        if UserFitbit.objects.filter(fitbit_user=fitbit_user).exists():
            # if exist update
            UserFitbit.objects.filter(fitbit_user=fitbit_user).update(access_token = access_token)
            print "fitbit-exist"

        #TODO set the storage directory
        directory = "./fitapp/static/data/"+str(user)
        if not os.path.exists(directory):
            os.makedirs(directory)


        #TODO set the resource and get the data
        while str(base_date) != str(yesterday)+" 00:00:00+00:00":
####
            # Load old data
            fit_profile = Profile.objects.get(user_id = fit_user_id)
            old_fitPoint = fit_profile.fitPoint
            old_fitHeart = fit_profile.fitHeart
            old_fitSleep = fit_profile.fitSleep


            print "what? : ",user 
            # get step data ################
            health_step = get_today_data_auto(fit_user_id, 'activities', 'steps',base_date)
            health_step = str(health_step).split('\n')[2]
            today_step_data = json.loads(health_step)

            # store the step_data ex) 2016-11-22_steps.json
            name = directory+"/"+str(base_date)[:10]+"_"+"steps"+".json"
            f = open(name, 'w')
            f.write(health_step)
            f.close()

            # get heart data ################
            health_heart = get_today_data_auto(fit_user_id, 'activities', 'heart',base_date)
            health_heart = str(health_heart).split('\n')[2]
            today_heart_data = json.loads(health_heart)

            # store the step_data ex) 2016-11-22_heart.json
            name = directory+"/"+str(base_date)[:10]+"_"+"heart"+".json"
            f = open(name, 'w')
            f.write(health_heart)
            f.close()

            # store the sleep_data
            health_sleep = get_today_data_auto(fit_user_id, 'activities', 'sleep',base_date)
            health_sleep = str(health_sleep).split('\n')[2]
            today_sleep_data = json.loads(health_sleep)
            print today_sleep_data

            # store the sleep_data ex) 2016-11-22_sleep.json
            name = directory+"/"+str(base_date)[:10]+"_"+"sleep"+".json"
            f = open(name, 'w')
            f.write(health_sleep)
            f.close()

            # Get Step and check null point exception
            try:
                result = today_step_data['objects']['activities-steps'][0]['value']
                print "result : ",result
            except:
                #return render(request,'fitapp/need_to_sync.html',{})
                result = 0
                pass

            # Get Heart and check null point exception
            try:
                heartResult = today_heart_data['objects']['activities-heart'][0]['value']['heartRateZones'][1]['minutes']
                print "fitHeart : ",heartResult
            except:
                heartResult = 0
                pass

            # Get Sleep and check null point exception
            try:
                sleepResult = today_sleep_data['objects']['sleep'][0]['timeInBed']
                print "fitSleep : ",sleepResult
            except:
                sleepResult = 0
                pass

            # total step
            update_total_step = int(result) + update_total_step

            # Calculate fitpoint  
            fitPoint = int(result)/500
            update_total_fitPoint += fitPoint

            # Calculate fitHeart
            fitHeart = int(heartResult)/15

            # Calculate fitSleep
            fitSleep = int(sleepResult)/15

            Profile.objects.filter(user_id=fit_user_id).update(last_sync_date = base_date)
            Profile.objects.filter(user_id=fit_user_id).update(fitPoint = old_fitPoint + fitPoint)
            Profile.objects.filter(user_id=fit_user_id).update(fitSleep = old_fitSleep + fitSleep)
            Profile.objects.filter(user_id=fit_user_id).update(fitHeart = old_fitHeart + fitPoint)
            # increase a day
            base_date = base_date + datetime.timedelta(days=1)
            print "inceased date : ",base_date
        Profile.objects.filter(user_id=fit_user_id).update(last_sync_date = yesterday)
####
    return render(request, 'fitapp/sync_done.html', {'fitpoint':update_total_fitPoint})

    #TODO if token is expired refresh

    #TODO save the data



# Now Use This
@require_GET
def get_today_steps(request):
    """An AJAX view that retrieves this user's step data from Fitbit.

    This view has been deprecated. Use `get_data` instead.

    URL name:
        `fitbit-steps`
    """

    # Check the directory is exist 
    user = str(request.user)
    print "user!!! : ",user,type(user)
    directory = "./fitapp/static/data/"+user
    if not os.path.exists(directory):
        os.makedirs(directory)

    # setting user id
    fit_user_id = request.user.id
    print "user!!! : ",fit_user_id,type(fit_user_id)

    # Search from database
    old_fitPoint = 0
    fit_profile = Profile.objects.get(user_id = fit_user_id)
    old_fitPoint = fit_profile.fitPoint
    old_sync_date = fit_profile.last_sync_date

    # calculate and set yesterday
    today 	= datetime.date.today()
    yesterday 	= today - datetime.timedelta(1)
    # for the Demo
    yesterday   = today + datetime.timedelta(1)
    yesterday	= yesterday.strftime('%Y-%m-%d')

    # for debug 
    # print "old_fitPoint : ",old_fitPoint
    # print "old_sync_date : ",old_sync_date
    # print "Compare_data : ",str(yesterday)+" 00:00:00+00:00"   
 
    # setting the searching date
    base_date 	= old_sync_date
    period 	= request.GET.get('period', None)
    end_date 	= yesterday
    # print "base_date : ",base_date
    
    # last sycn , yesterday to sync all data from last sync date
    
    update_total_step = 0
    total_step = 0
    update_total_fitPoint = 0
    total_sleep = 0
    total_heart = 0
    result_total = 0

    # for debug
    #print "DEBUG START POINT1"
    #fbuser = UserFitbit.objects.get(user=user)
    
    #print "Debug print"
    #health_step = get_today_data(request, 'activities', 'steps',base_date)
    #health_heart = get_today_data(request, 'activities', 'heart',base_date)
    #health_sleep = get_today_data(request, 'activities', 'sleep',base_date)

    #health_step = str(health_step).split('\n')[2]
    #print "DEBUG-health_step1 : ",health_step

    #health_heart = str(health_heart).split('\n')[2]
    #print "DEBUG-health_heart1 : ",health_heart 

    #health_sleep = str(health_sleep).split('\n')[2]
    #print "DEBUG-health_sleep1 : ",health_sleep

    # compare and sync
    print "basedate: ",str(base_date),"yesterday : ",str(yesterday)+" 00:00:00+00:00"
    while str(base_date) != str(yesterday)+" 00:00:00+00:00":
 
        # Load old data
        fit_profile = Profile.objects.get(user_id = fit_user_id)
        old_fitPoint = fit_profile.fitPoint
        old_fitHeart = fit_profile.fitHeart
        old_fitSleep = fit_profile.fitSleep

        # get step data ################
        health_step = get_today_data(request, 'activities', 'steps',base_date)
        health_step = str(health_step).split('\n')[2]
        today_step_data = json.loads(health_step)

        # store the step_data ex) 2016-11-22_steps.json
        name = directory+"/"+str(base_date)[:10]+"_"+"steps"+".json"
        f = open(name, 'w')
        f.write(health_step)
        f.close()
 
        # get heart data ################
        health_heart = get_today_data(request, 'activities', 'heart',base_date)
        health_heart = str(health_heart).split('\n')[2]
        today_heart_data = json.loads(health_heart)

        # store the step_data ex) 2016-11-22_heart.json
        name = directory+"/"+str(base_date)[:10]+"_"+"heart"+".json"
        f = open(name, 'w')
        f.write(health_heart)
        f.close()
        
        # store the sleep_data
        health_sleep = get_today_data(request, 'activities', 'sleep',base_date) 
        health_sleep = str(health_sleep).split('\n')[2]
        today_sleep_data = json.loads(health_sleep)
        print today_sleep_data

        # store the sleep_data ex) 2016-11-22_sleep.json
        name = directory+"/"+str(base_date)[:10]+"_"+"sleep"+".json"
        f = open(name, 'w')
        f.write(health_sleep)
        f.close()
        
         
        # Get Step and check null point exception
        try:
            result = today_step_data['objects']['activities-steps'][0]['value']
            print "result : ",result
        except:
            #return render(request,'fitapp/need_to_sync.html',{})
            result = 0
            pass

	# Get Heart and check null point exception
        try:
            heartResult = today_heart_data['objects']['activities-heart'][0]['value']['heartRateZones'][1]['minutes']
            print "fitHeart : ",heartResult
        except:
            heartResult = 0
            pass

	# Get Sleep and check null point exception
        try:
            sleepResult = today_sleep_data['objects']['sleep'][0]['timeInBed']
            print "fitSleep : ",sleepResult
        except:
            sleepResult = 0
            pass
 
        # total step
        update_total_step = int(result) + update_total_step
        total_step += int(result)
        # Calculate fitpoint  
        fitPoint = int(result)/500
        update_total_fitPoint += fitPoint
        
	# Calculate fitHeart
        fitHeart = int(heartResult)/15
        total_heart = fitHeart + total_heart
	# Calculate fitSleep
        fitSleep = int(sleepResult)/15
        total_sleep = fitSleep + total_sleep

        Profile.objects.filter(user_id=fit_user_id).update(last_sync_date = base_date)
        Profile.objects.filter(user_id=fit_user_id).update(fitPoint = old_fitPoint + fitPoint)
        Profile.objects.filter(user_id=fit_user_id).update(fitSleep = old_fitSleep + fitSleep)
        Profile.objects.filter(user_id=fit_user_id).update(fitHeart = old_fitHeart + fitPoint)
        # increase a day
        base_date = base_date + datetime.timedelta(days=1)
        print "inceased date : ",base_date

    # print "Sync done!"
    """
##############
    temp_date = "2017-01-13 00:00:00+00:00"
    temp_date = datetime.datetime.strptime(temp_date, "%Y-%m-%d %H:%M:%S+%f:00")
    basic_date = "2017-02-04 00:00:00+00:00"
    basic_date = datetime.datetime.strptime(basic_date, "%Y-%m-%d %H:%M:%S+%f:00")

    while str(basic_date) != str(temp_date):
        print "temp_date updated! : ",temp_date
        # get step data ################
        # print "get data!"
        # get activities steps

           
        health_step = get_today_data(request, 'activities', 'steps',temp_date)
        health_step = str(health_step).split('\n')[2]
        today_step_data = json.loads(health_step)
        print "today_step_data : ",today_step_data
        
        # store the step_data
        name = directory+"/"+str(temp_date)[:10]+"_"+"steps"+".json"
        f = open(name, 'w')
        f.write(health_step)
        f.close()
        
        
        # get heart data ################
        # print "get data!"
        # get activities steps
        health_heart = get_today_data(request, 'activities', 'heart',temp_date)
        health_heart = str(health_heart).split('\n')[2]
        today_heart_data = json.loads(health_heart)

        name = directory+"/"+str(temp_date)[:10]+"_"+"heart"+".json"
        f = open(name, 'w')
        f.write(health_heart)
        f.close()
        
        
        
        # store the sleep_data
        health_sleep = get_today_data(request, 'activities', 'sleep',temp_date)
        health_sleep = str(health_sleep).split('\n')[2]
        today_sleep_data = json.loads(health_sleep)

        name = directory+"/"+str(temp_date)[:10]+"_"+"sleep"+".json"
        f = open(name, 'w')
        f.close()
        
        temp_date = temp_date + datetime.timedelta(days=1)

##############
    """
    print "THIS IS WORKING!",yesterday
    if update_total_step == 0:
        print "nothing to sync!"
        return render(request,'fitapp/sync_nodata.html',{})
    print "************* start update ***************"
    print "Step Point : ",update_total_fitPoint
    print "Sleep Point : ",total_sleep
    print "Heart point : ",total_heart
    Profile.objects.filter(user_id=fit_user_id).update(last_sync_date = yesterday)
    #Profile.objects.filter(user_id=fit_user_id).update(fitPoint = old_fitPoint + update_total_fitPoint)

    return render(request, 'fitapp/sync_done.html', {'fitpoint':update_total_fitPoint,'step':total_step})

@require_GET
def get_point(request,user_id,password,point):
    #user = request.user
    # 200 - success to get point
    # 400 - fail to get point
    # login
    user = auth.authenticate(username=user_id, password=password)
    print user_id,password,point

    # authed
    if user is not None:
        # give point and modify
        fit_profile = Profile.objects.get(user_id = user)
        old_fitPoint = fit_profile.fitPoint
        update_total_fitPoint = int(old_fitPoint) - int(point)
        if update_total_fitPoint < 0:
            return HttpResponse("400")
        Profile.objects.filter(user_id=user).update(fitPoint = update_total_fitPoint)
    else:
        return HttpResponse("400")

    return HttpResponse("200")

@require_GET
def get_sleep(request,user_id,password,point):
    #user = request.user
    # 200 - success to get point
    # 400 - fail to get point
    # login
    user = auth.authenticate(username=user_id, password=password)
    print user_id,password,point,user

    # authed
    if user is not None:
        # give point and modify
        print "work"
        fit_profile = Profile.objects.get(user_id = user)
        print fit_profile.user_id,fit_profile.fitSleep
        old_fitSleep = fit_profile.fitSleep
        update_total_fitSleep = int(old_fitSleep) - int(point)
        if update_total_fitSleep < 0:
            return HttpResponse("400")
        Profile.objects.filter(user_id=user).update(fitSleep = update_total_fitSleep)
        print old_fitSleep,update_total_fitSleep,point
    else:
        return HttpResponse("400")

    return HttpResponse("200")

@require_GET
def get_heart(request,user_id,password,point):
    #user = request.user
    # 200 - success to get point
    # 400 - fail to get point
    # login
    user = auth.authenticate(username=user_id, password=password)
    print user_id,password,point

    # authed
    if user is not None:
        # give point and modify
        fit_profile = Profile.objects.get(user_id = user)
        old_fitHeart = fit_profile.fitHeart
        update_total_fitHeart = int(old_fitHeart) - int(point)
        if update_total_fitHeart < 0:
            return HttpResponse("400")
        Profile.objects.filter(user_id=user).update(fitHeart = update_total_fitHeart)
    else:
        return HttpResponse("400")

    return HttpResponse("200")

def get_today_data_auto(user, category, resource, base_date):
    # Manually check that user is logged in and integrated with Fitbit.
    # 1. insert user
    print "name : ",user,"get_date : ",base_date, "category : ",category+"/"+resource
    
    # 2. calculate present time
    today       = datetime.date.today()
    yesterday   = today - datetime.timedelta(1)
    yesterday   = yesterday.strftime('%Y-%m-%d')
    print "TimeSeriesDataType : ",TimeSeriesDataType
    try:
        print "resource_type : ",category,resource
        if resource == "sleep":
            resource_type = resource
        else:
            resource_type = category+"/"+resource
        #resource_type = TimeSeriesDataType.objects.get(
        #    category=getattr(TimeSeriesDataType, category), resource=resource)
    except:
        return make_response(104)
    print "\n"
    fitapp_subscribe = utils.get_setting('FITAPP_SUBSCRIBE')

    # auth option
    #if not user.is_authenticated() or not user.is_active:
    #    return make_response(101)

    #### coution! you have to recover
    #if not fitapp_subscribe and not utils.is_integrated(user):
    #    return make_response(102)
    ####


    #base_date = request.GET.get('base_date', None)

    #base_date = yesterday
    period = "None"
    #end_date = yesterday
    end_date = base_date
    print "base_date : ",base_date,"period : ",period,"end_date : ",end_date

    if period and not end_date:
        form = forms.PeriodForm({'base_date': base_date, 'period': period})
    elif end_date and period == "None":
        form = forms.RangeForm({'base_date': base_date, 'end_date': end_date})
        print "check today!"
    else:
        # Either end_date or period, but not both, must be specified.
        print "no fitbit data!"
        return make_response(104)

    fitbit_data = form.get_fitbit_data()
    print "fitbit_data : ",fitbit_data
    if not fitbit_data:
        print "no fitbit data!"
        return make_response(104)
    if fitapp_subscribe:
        # Get the data directly from the database.
        print "user",user,type(user),resource_type,type(resource_type)
        date_range = 0
        existing_data = TimeSeriesData.objects.filter(
            user=user, resource_type=resource_type, **date_range)
        print "**result** : ",existing_data
        simplified_data = [{'value': d.value, 'dateTime': d.string_date()}
                           for d in existing_data]
        return make_response(100, fitbit_data)

    # Request data through the API and handle related errors.
    print "check user :" ,user
    try:
        fbuser = UserFitbit.objects.get(user=user)
        data = utils.get_fitbit_data(fbuser, resource_type, **fitbit_data)
        # for debug
        # print "data : ",data
    except (HTTPUnauthorized, HTTPForbidden):
        # Delete invalid credentials.
        fbuser.delete()
        pass
        return make_response(103)
    except HTTPConflict:
        pass
        return make_response(105)
    except HTTPServerError:
        pass
        return make_response(106)
    except:
        # Other documented exceptions include TypeError, ValueError,
        # HTTPNotFound, and HTTPBadRequest. But they shouldn't occur, so we'll
        # send a 500 and check it out.
        pass
        raise
    #print "return data : ",data
    return make_response(100, data)


@require_GET
def get_today_data(request, category, resource, base_date):
    # Manually check that user is logged in and integrated with Fitbit.
    # 1. insert user
    user = request.user
    print "user : ",user,"get_date : ",base_date, "category : ",category+"/"+resource

    # 2. calculate present time
    today 	= datetime.date.today()
    yesterday   = today - datetime.timedelta(1)
    yesterday   = yesterday.strftime('%Y-%m-%d')
    print "TimeSeriesDataType : ",TimeSeriesDataType
    try:
        print "resource_type : ",category,resource
        if resource == "sleep":
            resource_type = resource
        else:
            resource_type = category+"/"+resource
        #resource_type = TimeSeriesDataType.objects.get(
        #    category=getattr(TimeSeriesDataType, category), resource=resource)
    except:
        return make_response(104)
    print "\n"
    fitapp_subscribe = utils.get_setting('FITAPP_SUBSCRIBE')
    
    # auth option
    #if not user.is_authenticated() or not user.is_active:
    #    return make_response(101)
    
    #### coution! you have to recover
    #if not fitapp_subscribe and not utils.is_integrated(user):
    #    return make_response(102)
    ####


    #base_date = request.GET.get('base_date', None)
    
    #base_date = yesterday
    period = request.GET.get('period', None)
    print "period : ",period
    #end_date = yesterday
    end_date = base_date
    #end_date = request.GET.get('end_date', None)
    print "base_date : ",base_date,"period : ",period,"end_date : ",end_date

    if period and not end_date:
        form = forms.PeriodForm({'base_date': base_date, 'period': period})
    elif end_date and not period:
        form = forms.RangeForm({'base_date': base_date, 'end_date': end_date})
        print "check today!"
    else:
        # Either end_date or period, but not both, must be specified.
        print "no fitbit data!"
        return make_response(104)

    fitbit_data = form.get_fitbit_data()
    print "fitbit_data : ",fitbit_data
    if not fitbit_data:
        print "no fitbit data!"
        return make_response(104)
    if fitapp_subscribe:
        # Get the data directly from the database.
        print "user",user,type(user),resource_type,type(resource_type)
        date_range = normalize_date_range(request, fitbit_data)
        print "data_range : ",data_range
        existing_data = TimeSeriesData.objects.filter(
            user=user, resource_type=resource_type, **date_range)
        print "**result** : ",existing_data
        #simplified_data = [{'value': d.value, 'dateTime': d.string_date()}
                           #for d in existing_data]
        return make_response(100, fitbit_data)

    # Request data through the API and handle related errors.
    print "point : ",user
    fbuser = UserFitbit.objects.get(user=user)
    print "fitbit_user_id : ",fbuser.fitbit_user
    try:
        data = utils.get_fitbit_data(fbuser, resource_type, **fitbit_data)
        # for debug
        # print "data : ",data
    except (HTTPUnauthorized, HTTPForbidden):
        # Delete invalid credentials.
        fbuser.delete()
        return make_response(103)
    except HTTPConflict:
        return make_response(105)
    except HTTPServerError:
        return make_response(106)
    except:
        # Other documented exceptions include TypeError, ValueError,
        # HTTPNotFound, and HTTPBadRequest. But they shouldn't occur, so we'll
        # send a 500 and check it out.
        raise
    #print "return data : ",data
    return make_response(100, data)


@require_GET
def get_data(request, category, resource):
    """An AJAX view that retrieves this user's data from Fitbit.

    This view may only be retrieved through a GET request. The view can
    retrieve data from either a range of dates, with specific start and end
    days, or from a time period ending on a specific date.

    The two parameters, category and resource, determine which type of data
    to retrieve. The category parameter can be one of: foods, activities,
    sleep, and body. It's the first part of the path in the items listed at
    https://wiki.fitbit.com/display/API/API-Get-Time-Series
    The resource parameter should be the rest of the path.

    To retrieve a specific time period, two GET parameters are used:

        :period: A string describing the time period, ending on *base_date*,
            for which to retrieve data - one of '1d', '7d', '30d', '1w', '1m',
            '3m', '6m', '1y', or 'max.
        :base_date: The last date (in the format 'yyyy-mm-dd') of the
            requested period. If not provided, then *base_date* is
            assumed to be today.

    To retrieve a range of dates, two GET parameters are used:

        :base_date: The first day of the range, in the format 'yyyy-mm-dd'.
        :end_date: The final day of the range, in the format 'yyyy-mm-dd'.

    The response body contains a JSON-encoded map with two items:

        :objects: an ordered list (from oldest to newest) of daily data
            for the requested period. Each day is of the format::

               {'dateTime': 'yyyy-mm-dd', 'value': 123}

           where the user has *value* on *dateTime*.
        :meta: a map containing two things: the *total_count* of objects, and
            the *status_code* of the response.

    When everything goes well, the *status_code* is 100 and the requested data
    is included. However, there are a number of things that can 'go wrong'
    with this call. For each type of error, we return an empty data list with
    a *status_code* to describe what went wrong on our end:

        :100: OK - Response contains JSON data.
        :101: User is not logged in.
        :102: User is not integrated with Fitbit.
        :103: Fitbit authentication credentials are invalid and have been
            removed.
        :104: Invalid input parameters. Either *period* or *end_date*, but not
            both, must be supplied. *period* should be one of [1d, 7d, 30d,
            1w, 1m, 3m, 6m, 1y, max], and dates should be of the format
            'yyyy-mm-dd'.
        :105: User exceeded the Fitbit limit of 150 calls/hour.
        :106: Fitbit error - please try again soon.

    See also the `Fitbit API doc for Get Time Series
    <https://wiki.fitbit.com/display/API/API-Get-Time-Series>`_.

    URL name:
        `fitbit-data`

    example form
	step:  '/1/user/'+fitbit_id+'/activities/steps/date/2016-04-'+day+'/1d/1min.json'
	heart: '/1/user/'+fitbit_id+'/activities/heart/date/2016-05-'+day+'/1d.json'
	sleep: '/1/user/'+fitbit_id+'/sleep/date/2016-04-'+day+'.json'
    """

    # Manually check that user is logged in and integrated with Fitbit.
    # 1. insert user
    user = request.user
    print "user : ",user
    try:
        resource_type = TimeSeriesDataType.objects.get(
            category=getattr(TimeSeriesDataType, category), resource=resource)
        print "resource_type : ",resource_type
    except:
        return make_response(104)

    fitapp_subscribe = utils.get_setting('FITAPP_SUBSCRIBE')
    if not user.is_authenticated() or not user.is_active:
        return make_response(101)
    if not fitapp_subscribe and not utils.is_integrated(user):
        return make_response(102)

    base_date = request.GET.get('base_date', None)
    print "base_date : ",base_date
    period = request.GET.get('period', None)
    print "period : ",period
    end_date = request.GET.get('end_date', None)
    print "end_date : ",end_date
    if period and not end_date:
        form = forms.PeriodForm({'base_date': base_date, 'period': period})
    elif end_date and not period:
        form = forms.RangeForm({'base_date': base_date, 'end_date': end_date})
    else:
        # Either end_date or period, but not both, must be specified.
        return make_response(104)

    fitbit_data = form.get_fitbit_data()
    if not fitbit_data:
        print "no fitbit data!"
        return make_response(104)

    if fitapp_subscribe:
        # Get the data directly from the database.
        date_range = normalize_date_range(request, fitbit_data)
        existing_data = TimeSeriesData.objects.filter(
            user=user, resource_type=resource_type, **date_range)
        simplified_data = [{'value': d.value, 'dateTime': d.string_date()}
                           for d in existing_data]
        return make_response(100, simplified_data)

    # Request data through the API and handle related errors.
    fbuser = UserFitbit.objects.get(user=user)
    try:
        data = utils.get_fitbit_data(fbuser, resource_type, **fitbit_data)
    except (HTTPUnauthorized, HTTPForbidden):
        # Delete invalid credentials.
        fbuser.delete()
        return make_response(103)
    except HTTPConflict:
        return make_response(105)
    except HTTPServerError:
        return make_response(106)
    except:
        # Other documented exceptions include TypeError, ValueError,
        # HTTPNotFound, and HTTPBadRequest. But they shouldn't occur, so we'll
        # send a 500 and check it out.
        raise

    return make_response(100, data)

# visualization
def graph_sleep(request):
    return render(request, 'fitapp/graph_sleep.html', {})

def graph_step(request):
    return render(request, 'fitapp/graph_step.html', {})

def status(request):
    return render(request, 'fitapp/radar/index.html', {})

