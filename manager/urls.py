from django.urls import path
from . import views
# from .middlewares.auth import auth_middleware


app_name = 'manager'
urlpatterns = [
    path('teammember/', views.team, name='teammember'),
    path('notification/', views.notification, name='notification'),
    path('userlist/', views.userlist, name='userlist'),
    path('userdashboard/', views.userdashboard, name='userdashboard'),
    ]