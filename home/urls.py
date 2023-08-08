from django.urls import path
from . import views

app_name = 'home'
urlpatterns = [
    path('validate/dashboard/index/', views.index, name='index'),
    path('api/get-quiz/', views.get_quiz, name='get_quiz'),
    path('api/result/', views.result, name='result'),
    path('quiz/', views.quiz, name='quiz'),
    path('api/save-remaining-time/', views.save_remaining_time,name='save_remaining_time'),
    path('skipquiz/', views.skip_quiz, name='skipquiz'),
    path('save_time', views.save_time, name='save_time'),
    path('final/', views.final, name='final'),

]


# admin.site.site_header = "Switch Tech System Admin"
# admin.site.site_title = "Switch Tech System Admin Portal"
# admin.site.index_title = "Welcome to Admin Portal"
