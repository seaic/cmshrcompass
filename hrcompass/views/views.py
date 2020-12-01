################################################
#
# These views handle everything that has to do 
# with the main Part of the application
# (CRUD: Create, Read, Update, Delete)
#
################################################

from django.shortcuts import render, redirect
from hrcompass.forms import ClientForm, TaskForm
from hrcompass.models import Client, Task, Status, Kind, AuthUser, Taskname
from django_otp.decorators import otp_required
from collections import defaultdict
import datetime
from django.contrib import messages

# Create your views here.
@otp_required
def addclient(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        #print(form)
        if form.is_valid():
            #print(form.is_valid)
            try:
                #print(form.save)
                form.save(commit=True)
                #print("true")
                if 'stanother' in request.POST:
                    return redirect('/addclient')
                else:
                    return redirect('/show')
            except OSError as err:
                print(err)
                pass
    else:
        form = ClientForm()
    return render(request,'addclient.html',{'form':form})

@otp_required
def addtask(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        today = datetime.datetime.now()
        duedate = request.POST.get('duedate').replace('-', '')
        startdate = request.POST.get('startdate').replace('-', '')
        #if duedate >= today.strftime('%Y%m%d'):
        if duedate >= startdate:
            #print(form)
            if form.is_valid():
                #print(form.is_valid)
                try:
                    #print(form.save)
                    form.save(commit=True)
                    #print("true")
                    if 'stanother' in request.POST:
                        return redirect('/addtask')
                    else:
                        return redirect('/show')
                except OSError as err:
                    print(err)
                    pass
        else:
            #print("Error: Duedate before Startdate")
            messages.error(request,"Error: Duedate is before Startdate")
        #else:
            #print("Error: Duedate is in the past")
            #messages.error(request,"Error: Duedate is in the past")
    else:
        form = TaskForm()
    return render(request,'addtask.html',{'form':form})

# AJAX
@otp_required
def load_taskname(request):
    kind_id = request.GET.get('task_kind')
    tasknames = Taskname.objects.filter(task_kind_id=kind_id).all()
    return render(request, 'taskname_dropdown_list_options.html', {'tasknames': tasknames})

@otp_required
def show(request):
    #print("true")
    try:
        result=int(request.GET["clientList"])
    except:
        result=0
    try:
        statresult=int(request.GET["statusList"])
    except:
        statresult=0
    try:
        taskresult=int(request.GET["kindList"])
    except:
        taskresult=0
    try:
        userresult=int(request.GET["empList"])
    except:
        userresult=0
    clien = Client.objects.all()
    status = Status.objects.all()
    users = AuthUser.objects.all()
    kinds = Kind.objects.all()
    tasks = Task.objects.select_related('client', 'task_status', 'task_name').prefetch_related('members')
    task_list = []
    for task in tasks:
        if result == task.client.id or result == 0:
            if statresult == task.task_status.id or statresult == 0:
                user_list = list(task.members.values_list('id', flat=True))
                if userresult in user_list or userresult == 0:
                    if taskresult == task.task_name.task_kind.id or taskresult == 0:
                        task_list += [task]
    task_list.sort(key=lambda x: (x.task_name.task_kind.kind, x.duedate.strftime("%Y%m%d")))
    groups = defaultdict(list)

    for obj in task_list:
        groups[obj.task_name.task_kind.kind].append(obj)

    newlist = groups.values()
    #print(newlist)
    kindlist = []
    return render(request,"show.html",{'tasks': tasks, 'clien': clien, 'result': result,
     'statresult': statresult, 'status': status, 'taskresult': taskresult, 'users': users,
     'userresult': userresult, 'kinds': kinds, 'task_list': newlist})

@otp_required
def edit(request, id):   
    task = Task.objects.get(id=id)
    form = TaskForm(request.POST or None, instance = task)
    return render(request,'edit.html', {'task': task, 'form': form})
@otp_required
def update(request, id):
    task = Task.objects.get(id=id)
    form = TaskForm(request.POST, instance = task)
    today = datetime.datetime.now()
    duedate = request.POST.get('duedate').replace('-', '')
    startdate = request.POST.get('startdate').replace('-', '')
    #if duedate >= today.strftime('%Y%m%d'):
    if duedate >= startdate:
        #print(form)
        if form.is_valid():
            #print("valid")
            try:
                #print(form.save)
                form.save(commit=True)
                return redirect('/show')
            except OSError as err:
                print(err)
                pass
    else:
        messages.error(request,"Error: Duedate is before Startdate")
    #else:
        #messages.error(request,"Error: Duedate is in the past")
    return render(request, 'edit.html', {'task': task, 'form': form})
@otp_required
def destroy(request, id):
    task = Task.objects.get(id=id)
    task.delete()
    return redirect("/show")
    
