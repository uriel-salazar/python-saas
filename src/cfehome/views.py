from django.http import HttpResponse
import pathlib
from django.shortcuts import render
this_dir = pathlib.Path(__file__).resolve().parent
from visits.models import PageVisit
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings

LOGIN_URL = settings.LOGIN_URL

def home_view(request,*args,**kwargs):
    return about_view(request,*args,**kwargs)

def about_view(request,*args,**kwargs):
    qs = PageVisit.objects.all()
    page_qs = PageVisit.objects.filter(path=request.path)
    try:
        percent =(page_qs.count() * 100.0) /qs.count(),
    except:
        percent  = 0 
    my_title='My page'
    my_context = {
        "page_title":my_title,
        "page_visit_count":page_qs.count(),
        "percent":percent,
        "total_visit_count":qs.count()

    }
    path = request.path
    print("path",path)
    html_template = 'home.html'
    PageVisit.objects.create(path=request.path)
    
    return render(request,html_template,my_context)

VALID_CODE = 'abc123'
def pw_protected_view(request,*args,**kwargs):
    is_allowed = request.session.get('protected_page_allowed') or 0 
    if request.method =='POST':
        user_pw_request = request.POST.get("code") or None
        if user_pw_request == VALID_CODE:
            is_allowed=1
            request.session['protected_page_allowed'] = is_allowed
    if is_allowed:
            return render(request,'protected/view.html',{})
    
    return render(request,'protected/entry.html',{})

@login_required
def user_only_view(request):
    print(request.user.is_staff)
    return render(request,"protected/user_only.html",{})


@staff_member_required(login_url=LOGIN_URL)
def staff_only_view(request):
    
    return render(request,"protected/user_only.html",{})