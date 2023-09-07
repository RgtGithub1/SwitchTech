from django.urls import path
from . import views

app_name = 'home'
urlpatterns = [
    path('validate/dashboard/index/', views.index, name='index'),
    path('get_quiz/', views.get_quiz, name='get_quiz'),
    path('calculate_results/',
         views.calculate_results, name='calculate_results'),
    path('skipquiz/', views.skip_quiz, name='skipquiz'),
    path('save_time', views.save_time, name='save_time'),
    path('final/', views.final, name='final'),

]
