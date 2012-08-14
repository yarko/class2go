from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import Context, loader
from django.template import RequestContext
from django.contrib.auth.models import User,Group
from courses.common_page_data import get_common_page_data

from c2g.models import *
from random import randrange
from datetime import datetime

def switch_mode(request):
    common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    if common_page_data['can_switch_mode']:
        request.session['course_mode'] = request.POST.get('to_mode')
    return redirect(request.META['HTTP_REFERER'])
    
def add_section(request):
    course_prefix = request.POST.get("course_prefix")
    course_suffix = request.POST.get("course_suffix")
    common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    
    index = len(ContentSection.objects.filter(course=common_page_data['course']))
    
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.view', course_prefix, course_suffix)
    
    staging_section = ContentSection(course=common_page_data['staging_course'], title=request.POST.get("title"), index=index, mode='staging')
    staging_section.save()
    
    staging_section.create_production_instance()
    
    return redirect(request.META['HTTP_REFERER'])
    
def commit(request):
    ids = request.POST.get("commit_ids").split(",")
    for id in ids:
        parts = id.split('_')
        if parts[0] == 'video':
            Video.objects.get(id=parts[1]).commit()
        elif parts[0] == 'problemset':
            ProblemSet.objects.get(id=parts[1]).commit()
        elif parts[0] == 'additionalpage':
            AdditionalPage.objects.get(id=parts[1]).commit()
    return redirect(request.META['HTTP_REFERER'])
    
def revert(request):
    ids = request.POST.get("revert_ids").split(",")
    for id in ids:
        parts = id.split('_')
        if parts[0] == 'video':
            Video.objects.get(id=parts[1]).revert()
        elif parts[0] == 'problemset':
            ProblemSet.objects.get(id=parts[1]).revert()
        elif parts[0] == 'additionalpage':
            AdditionalPage.objects.get(id=parts[1]).revert()
    return redirect(request.META['HTTP_REFERER'])
    
def change_live_datetime(request):
    ids = request.POST.get("change_live_datetime_ids").split(",")
    
    if request.POST.get("live_datetime_option") == 'now':
        new_live_datetime = datetime.now()
    else:
        live_date_parts = request.POST.get("live_date").split("-")
        year = int(live_date_parts[2])
        month = int(live_date_parts[0])
        day = int(live_date_parts[1])
        if request.POST.get("live_hours") == '':
            hour = 0
        else:
            hour = int(request.POST.get("live_hours"))
            
        if request.POST.get("live_minutes") == '':
            minute = 0
        else:
            minute = int(request.POST.get("live_minutes"))
        
        new_live_datetime = datetime(year,month,day,hour,minute)
    
    for id in ids:
        parts = id.split('_')
        if parts[0] == 'video':
            image = Video.objects.get(id=parts[1]).image
            image.live_datetime = new_live_datetime
            image.save()
        elif parts[0] == 'problemset':
            image = ProblemSet.objects.get(id=parts[1]).image
            image.live_datetime = new_live_datetime
            image.save()
        elif parts[0] == 'additionalpage':
            image = AdditionalPage.objects.get(id=parts[1]).image
            image.live_datetime = new_live_datetime
            image.save()
            
    return redirect(request.META['HTTP_REFERER'])

