
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'dashboard'
urlpatterns = [
    path('', views.loginPage, name='login'),
    path('validate/', views.validate, name='validate'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    path('validate/dashboard/', views.dashboard, name='dashboard'),
    path('history/', views.history, name='history'),
    path('mylearning/', views.my_learning, name='mylearning'),
    path('feedback/', views.feedback, name='feedback'),
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
    path('refeedback/', views.resendfeedback, name='resendfeedback'),
    path('logout/', views.user_logout, name='logout'),
]


admin.site.site_header = "Switch Tech System Admin"
admin.site.site_title = "Switch Tech System Admin Portal"
admin.site.index_title = "Welcome to Admin Portal"
