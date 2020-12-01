from django.test import TestCase
import datetime
import pytz
from hrcompass.models import Client, Task, Taskuser, AuthUser, Taskname, Kind
from django.contrib.auth.models import User
from hrcompass.views import views, dashboard
from mixer.backend.django import mixer
from django.shortcuts import render, redirect
from django.urls import reverse
from django.test import RequestFactory

# Comment out the @otp_required
# Create your tests here.
class TaskModelTest(TestCase):
    def setUp(self):
        Client.objects.create(client_name="Test AG", project_number="P100516")
        AuthUser.objects.create(username="testuser", password="ABC.1234", first_name="test", 
        last_name="user", email="test@user.ch", date_joined=datetime.datetime.now(pytz.utc))
        Kind.objects.create(id=1, kind="admin", active="True")
        Taskname.objects.create(name="Test Task", task_kind=Kind.objects.all()[0])

    def test_dashboard(self):
        req = RequestFactory().get(reverse("dashboard"))
        resp = dashboard.dashboard(req)
        assert resp.status_code == 200, "Should redirect to success url"
        #assert resp.url == "/dashboard"

    def test_postclient(self):
        """
        Dont work with @opt_required to do add authentification test above
        Testing the addclient view. Create a auth user and
        a client and fill up the clientuser many to many relation table
        """
        #assert False is Client.objects.all().exists()
        data = {
            "client_name": "Test Old AG",
            "project_number": "P100516",
            "consultants": 2
        }
        req = RequestFactory().post(reverse("addclient"), data=data)
        resp = views.addclient(req)
        assert Client.objects.all().exists()
        assert Client.objects.all()[0].client_name == "Test Old AG"
        assert resp.status_code == 302, "Should redirect to success url"
        assert resp.url == "/show"
    
    def test_posttask(self):
        """
        Dont work with @opt_required to do add authentification test above
        Testing the addtask view. Create a task and fill up relations.
        """
        assert False is Task.objects.all().exists()
        duedate = str(datetime.datetime.now())
        startdate = str(datetime.datetime.now() - datetime.timedelta(days=1))
        data = {
            "startdate": startdate,
            "duedate": duedate,
            "kind": Kind.objects.all()[0].id,
            "task_name": Taskname.objects.all()[0].id,
            "task_status": mixer.blend("hrcompass.Status").pk,
            "client": 4,
            "members": mixer.blend("hrcompass.AuthUser").pk,
        }
        req = RequestFactory().post(reverse("addtask"), data=data)
        resp = views.addtask(req)
        assert Task.objects.all().exists()
        assert Task.objects.all()[0].client.client_name == "Test AG"
        assert resp.status_code == 302, "Should redirect to success url"
        assert resp.url == "/show"
        self.edittask()
        self.updatetask()
        self.deletetask()
       
    def test_show(self):
        req = RequestFactory().get(reverse("show"))
        resp = views.show(req)
        assert resp.status_code == 200, "Should redirect to success url"
        #assert resp.url == "/show

    def edittask(self):
        req = RequestFactory().get(redirect("edit/1"))
        resp = views.edit(req, id=1)
        assert resp.status_code == 200, "Should redirect to success url"
        #assert resp.url == "/show

    def updatetask(self):
        duedate = str(datetime.datetime.now(pytz.utc))
        startdate = str(datetime.datetime.now() - datetime.timedelta(days=1))
        newdata = {
            "startdate": startdate,
            "duedate": duedate,
            "kind": Kind.objects.all()[0].id,
            "task_name": Taskname.objects.all()[0].id,
            "task_status": mixer.blend("hrcompass.Status").pk,
            "client": 4,
            "members": mixer.blend("hrcompass.AuthUser").pk,
        }
        req = RequestFactory().post(redirect("update/1"), data=newdata)
        resp = views.update(req, id=1)
        assert Task.objects.all().exists()
        assert str(Task.objects.all()[0].duedate) == duedate, "Task was not updated"
        assert len(Task.objects.all()) == 1, "Should be no new objects"
        assert resp.status_code == 302, "Should redirect to success url"
        assert resp.url == "/show"

    def deletetask(self):
        req = RequestFactory().post(redirect("destroy/1"))
        resp = views.destroy(req, id=1)
        assert False is Task.objects.all().exists(), "Task was not deleted"
        assert len(Task.objects.all()) == 0, "Should be no objects"
        assert resp.status_code == 302, "Should redirect to success url"
        assert resp.url == "/show"