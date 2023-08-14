
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'reassessment'
urlpatterns = [
    path('trainingquiz/', views.quiz_page, name='trainingquiz'),
    path('reassessmentquiz/', views.reassessmentquiz, name='reassessmentquiz'),
    path('reassessment_result/', views.reassessmentquiz, name='reassessmentquiz'),

]

