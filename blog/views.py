from django.shortcuts import render
from django.template.response import TemplateResponse

# Auth
from django.contrib import auth
from django.http import HttpResponseRedirect

# register
from django.shortcuts import render_to_response
from django.contrib.auth.forms import UserCreationForm
from django.core.context_processors import csrf

# Create your views here.
def home(request):
    return render(request, 'blog/admin_home.html', {})

def login(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('blog/login.html',c)

def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    print username, password
    user = auth.authenticate(username=username, password=password)
    
    print user

    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect('blog/loggedin')
    else :
        return HttpResponseRedirect('blog/invalid')

def loggedin(request):
    return render_to_response('blog/loggedin.html',{'full_name':request.user.username})

def invalid_login(request):
    return render_to_response('blog/invalid_login.html')

def logout(request):
    auth.logout(request)
    return render(request,'blog/logout.html',{})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('register_success')
    
    args = {}
    args.update(csrf(request))

    args['form'] = UserCreationForm()
    
    return render_to_response('blog/register.html',args)

def register_success(request):
    return render_to_response('blog/register_success.html')
