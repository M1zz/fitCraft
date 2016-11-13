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

def item(request):
    return render(request, 'blog/fitcraft/item.html', {})

def howToPlay(request):
    print "how to play"
    return render(request, 'blog/fitcraft/howToPlay.html', {})

def sync(request):
    return render(request, 'blog/fitcraft/sync.html', {})

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
    idList = User.objects.all()
    pointList = Profile.objects.all()
    rangeList = range(User.objects.all().count())
    print rangeList
    ranking = {}
    for i in range(User.objects.all().count()):
        ranking[idList[i].username] = pointList[i].fitPoint
        idData.append(idList[i].username)
        pointData.append(pointList[i].fitPoint)
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
    return render_to_response('blog/rank.html', {'idList': idData, 'pointList': pointData} )
    

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
