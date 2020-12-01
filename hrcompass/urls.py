"""hrcompass URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from hrcompass.views import views, dashboard, excelexport, authuser
from two_factor.urls import urlpatterns as tf_urls
from django.contrib.auth.views import LogoutView

#admin.site.__class__ = AdminSiteOTPRequired

from hrcompass.views.authuser import (
    RegistrationCompleteView, RegistrationView, ProfileView,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(tf_urls)),
    path('addclient', views.addclient, name="addclient"),
    path('addtask', views.addtask, name="addtask"),
    path('show', views.show, name="show"),
    path('edit/<int:id>', views.edit),
    path('update/<int:id>', views.update, name="update"),
    path('delete/<int:id>', views.destroy),
    path('changepassword/<int:id>', authuser.changepassword),
    path('exceldownload', excelexport.writetoexcel),
    path('ajax/load-taskname/', views.load_taskname, name='ajax_load_taskname'), # AJAX
    path('', authuser.profile, name='profile'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('accounts/profile/', authuser.logincomplete),
    path('dashboard', dashboard.dashboard, name='dashboard'),
    path(
        'account/register/',
        RegistrationView.as_view(),
        name='registration',
    ),
    path(
        'account/register/done/',
        RegistrationCompleteView.as_view(),
        name='registration_complete',
    ),
    path(
        'account/logout/',
        LogoutView.as_view(),
        name='logout',
    ),
]
