from django.shortcuts import render
from django.template.response import TemplateResponse

# Auth
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

# register
from forms import MyRegistrationForm
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

# fityou fitpoint
from blog.models import Profile
from operator import itemgetter

# wirte post
from blog.models import DjangoBoard
from django.utils import timezone
from blog.pagingHelper import pagingHelper
rowsPerPage = 2

# Create your views here.
def home(request):
    return render(request, 'blog/admin_home.html', {})

def fit_board(request):
    return render(request, 'blog/board.html', {})

def show_write_form(request):
    return render(request, 'blog/writeBoard.html', {})
#    return render_to_response('blog/writeBoard.html')

'''
def login(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('blog/login.html',c)

def register(request):
    if request.method == 'POST':
        form = MyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('register_success')

    args = {}
    args.update(csrf(request))

    args['form'] = MyRegistrationForm()

    return render_to_response('blog/register.html',args)
'''

def fitcraft(request):
    return render(request, 'blog/fitcraft/fitcraft.html', {})

def xiaomi(request):
    return render(request, 'blog/fitcraft/xiaomi.html', {})

def item(request):
    return render(request, 'blog/fitcraft/item.html', {})

def howToPlay(request):
    return render(request, 'blog/fitcraft/howToPlay.html', {})

def tool(request):
    return render(request, 'blog/fitcraft/tool.html', {})

def vi_python(request):
    return render(request, 'blog/fitcraft/vi_python.html', {})

def sync(request):
    return render(request, 'blog/fitcraft/sync.html', {})

def logs(request):
    return render(request, 'blog/fitcraft/stats.html', {})

def note(request):
    return render(request, 'blog/fitcraft/note.html', {})

def DoWriteBoard(request):
    br = DjangoBoard (subject = request.POST['subject'],
                      name = request.POST['name'],
                      mail = request.POST['email'],
                      memo = request.POST['memo'],
                      created_date = timezone.now(),
                      hits = 0
                     )
    br.save()

    # show again
    url = 'listSpecificPageWork?current_page=1'
    return HttpResponseRedirect(url)

def listSpecificPageWork(request):
    current_page = request.GET['current_page']
    totalCnt = DjangoBoard.objects.all().count()

    print 'current_page=', current_page

    # select
    boardList = DjangoBoard.objects.raw('SELECT * FROM blog_djangoboard ORDER BY id DESC')

    #print 'boardList=',boardList, 'count()=', totalCnt

    # send whole page
    pagingHelperIns = pagingHelper();
    totalPageList = pagingHelperIns.getTotalPageList( totalCnt, rowsPerPage)

    print 'totalPageList', totalPageList

    return render_to_response('blog/listSpecificPage.html', {'boardList': boardList, 'totalCnt': totalCnt,'current_page':int(current_page) ,'totalPageList':totalPageList} )

def get_rank(request):
    idData = []
    pointData = []
    sleepData = []
    heartData = []
    idList = User.objects.all()
    pointList = Profile.objects.all()
    rangeList = range(User.objects.all().count())
    print rangeList
    ranking = {}
    for i in range(User.objects.all().count()):
        ranking[idList[i].username] = pointList[i].fitPoint
        idData.append(idList[i].username)
        pointData.append(pointList[i].fitPoint)
        sleepData.append(pointList[i].fitSleep)
        heartData.append(pointList[i].fitHeart)
        #print idData , pointData
    ranking = sorted(ranking.iteritems(), key=itemgetter(1), reverse=True)
    # init list
    idData = []
    pointData = []

    for sep in ranking:
        idData.append(sep[0])
        pointData.append(sep[1])
    print ranking
    pointList = Profile.objects.raw('SELECT fitPoint FROM blog_profile ')
    return render_to_response('blog/rank.html', {'idList': idData, 'pointList': pointData, 'sleepList': sleepData, 'heartList':heartData} )
   
def get_heartRank(request):
    idData = []
    sleepData = []
    idList = User.objects.all()
    heartList = Profile.objects.all()
    rangeList = range(User.objects.all().count())
    #print "idList",idList
    ranking = {}
    for i in range(User.objects.all().count()):
        ranking[idList[i].username] = heartList[i].fitHeart
        idData.append(idList[i].username)
        sleepData.append(heartList[i].fitHeart)
        #print idData , pointData
    ranking = sorted(ranking.iteritems(), key=itemgetter(1), reverse=True)
    print ranking
    # init list
    idData = []
    heartData = []
    for sep in ranking:
        idData.append(sep[0])
        heartData.append(sep[1])
    print ranking
    heartList = Profile.objects.raw('SELECT fitHeart FROM blog_profile ')
    return render_to_response('blog/heartRank.html', {'idList': idData, 'heartList': heartData} )


def get_sleepRank(request):
    idData = []
    sleepData = []
    idList = User.objects.all()
    sleepList = Profile.objects.all()
    rangeList = range(User.objects.all().count())
    print "idList",idList
    ranking = {}
    for i in range(User.objects.all().count()):
        ranking[idList[i].username] = sleepList[i].fitSleep
        idData.append(idList[i].username)
        sleepData.append(sleepList[i].fitSleep)
        #print idData , pointData
    ranking = sorted(ranking.iteritems(), key=itemgetter(1), reverse=True)
    print ranking
    # init list
    idData = []
    sleepData = []
    for sep in ranking:
        idData.append(sep[0])
        sleepData.append(sep[1])
    print ranking
    sleepList = Profile.objects.raw('SELECT fitSleep FROM blog_profile ')
    return render_to_response('blog/sleepRank.html', {'idList': idData, 'sleepList': sleepData} )



 

def viewWork(request):
    pk= request.GET['memo_id']
    boardData = DjangoBoard.objects.get(id=pk)

    # raise hit
    DjangoBoard.objects.filter(id=pk).update(hits = boardData.hits + 1)

    return render_to_response('blog/viewMemo.html', {'memo_id': request.GET['memo_id'],
                                                'current_page':request.GET['current_page'],
                                                'searchStr': request.GET['searchStr'],
                                                'boardData': boardData } )

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
        return HttpResponseRedirect('/fitcraft')
    else :
        return HttpResponseRedirect('/login',{'login_flag':"fail"})

def loggedin(request):
    return render_to_response('blog/loggedin.html',{'full_name':request.user.username})

def invalid_login(request):
    return render_to_response('blog/invalid_login.html')

def logout(request):
    auth.logout(request)
    return render(request,'blog/logout.html',{})


def register(request):
    if request.method == 'POST':
        form = MyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('register_success')
    
    args = {}
    args.update(csrf(request))

    args['form'] = MyRegistrationForm()
    return render_to_response('blog/register.html',args)

def register_success(request):
    return render_to_response('blog/register_success.html')

def analysis(request):
    return render(request, 'blog/analysis/index.html', {})
