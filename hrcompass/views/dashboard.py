################################################
#
# These view is for the dashbord with the 
# statistics
#
################################################

from django.shortcuts import render
from hrcompass.models import Client, Task, Status, Kind
from django_otp.decorators import otp_required

#for dashboard
import matplotlib.pyplot as plt
import numpy as np
import io
import urllib, base64

@otp_required
def dashboard(request):
    """
    #plt.plot(range(10))
    #fig = plt.gcf()
    #objects = ('Python', 'C++', 'Java', 'Perl', 'Scala', 'Lisp')
    clients = Client.objects.all()
    objects = []
    for client in clients:
        objects.append(client.client_name)
    tasks = Task.objects.select_related('client')
    clientlist = []
    for task in tasks:
        clientlist.append(task.client.client_name)
    countlist = []
    for clientname in objects:
        count = clientlist.count(clientname)
        countlist.append(count)
    y_pos = np.arange(len(objects))
    #y_pos = [1, 4, 8, 12]
    performance = countlist
    plt.figure(figsize=(15, 5))
    plt.bar(y_pos, performance, width=0.6, bottom=None, align='center', alpha=0.5)
    plt.xticks(y_pos, objects)
    plt.ylabel('Tasks')
    plt.title('Number of Task for each client')
    """
    # Progress Bar Chart #####################################################################
    try:
        result=int(request.GET["clientList"])
    except:
        result=0
    try:
        taskresult=int(request.GET["kindList"])
    except:
        taskresult=0
    kinds = Kind.objects.all()
    client = Client.objects.all()
    status = Status.objects.all()
    tasks = Task.objects.select_related('client', 'task_status', 'task_name')
    statuslist = []
    objects = []
    statuslist = []
    countlist = []
    for task in tasks:
        if result == task.client.id or result == 0:
            if taskresult == task.task_name.task_kind.id or taskresult == 0:
                if task.task_status.status in objects:
                    pass
                else:
                    objects.append(task.task_status.status)
                statuslist.append(task.task_status.status)
    for taskstatus in objects:
        count = statuslist.count(taskstatus)
        countlist.append(count)

    plt.rcdefaults()
    fig, ax = plt.subplots(figsize=(6.5, 2.5))  
    y_pos = np.arange(len(objects))
    #y_pos = [1, 4, 8, 12]
    performance = countlist
    #plt.figure(figsize=(10, 6))
    ax.barh(y_pos, performance, height=0.5,  align='center', color="#1b3960")
    #ax.set_yticks(y_pos)
    #ax.set_yticklabels(objects)
    #ax.invert_yaxis()
    #ax.set_xlabel('Tasks')
    #ax.set_title('Progress Bar', color="#1b3960", fontsize = 14, horizontalalignment="center",)
    plt.gcf().subplots_adjust(right=0.31)
    plt.axis('off')
    for i, v in enumerate(y_pos):
        value = str(performance[v]) + "/" + str(sum(performance)) + " - " + objects[v].upper()
        ax.text(max(performance) + 2, i, value, color="#1b3960", fontweight='bold', fontsize = 7)
    #convert graph into dtring buffer and than we convert 64 bit code into image
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches = 'tight', dpi = 1000, pad_inches=0)
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    # Donut Chart ############################################################################
    try:
        result2=int(request.GET["clientList2"])
        #print("filter")
    except:
        result2=0
        #print("no filter")
    try:
        taskresult2=int(request.GET["kindList2"])
    except:
        taskresult2=0
    plt.cla()
    objects = []
    for task in tasks:
        if result2 == task.client.id or result2 == 0:
            if taskresult2 == task.task_name.task_kind.id or taskresult2 == 0:
                objects.append(task.task_status.status)
    completed = objects.count('completed (100%)')
    length = len(objects)
    notcompleted = length - completed

    size_of_groups=[notcompleted, completed]
    labels = ['', 'closed']
    colors =  ['#fff', '#29ff5c']
    # Create a pieplot
    plt.pie(size_of_groups, colors = colors)
    
    # add a circle at the center
    x = 0
    y = 0   
    my_circle=plt.Circle( (0,0), 0.8, color='white')
    ax.add_patch(my_circle)
    label = ax.annotate(str(completed) + "/" + str(length), xy=(x, y), fontsize=7, ha="center",)# color = "#29ff5c")
    ax.axis('off')
    ax.set_aspect('equal')
    ax.autoscale_view()
    # convert graph into dtring buffer and than we convert 64 bit code into image
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches = 'tight', dpi = 1000, pad_inches=0)
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri2 = urllib.parse.quote(string)
    return render(request, 'dashboard.html', {'data': uri, 'data2': uri2, 'client': client, 'kinds': kinds,
    'result': result, 'taskresult': taskresult, 'result2': result2, 'taskresult2': taskresult2,})# 'plt': plt})