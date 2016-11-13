import os
import logging
import httplib2
import json

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

DATA_SET = "1370475368000000000-1571080168000000000"

@login_required
def index(request):
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
        print json_string
        #logging.info(activitylist)
        return render(request, 'plus/welcome.html', {
                    'activitylist': json_string,
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
    return HttpResponseRedirect("/")
