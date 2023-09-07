from django.urls import path
from . import views

app_name = 'reassessment'
urlpatterns = [
    path('trainingquiz/', views.reassessment_questions, name='trainingquiz'),
    path('reassessmentquiz/',
         views.validate_reassessment,
         name='validate_reassessment'),
    path('reassessment_result/',
         views.validate_reassessment,
         name='validate_reassessment'),

]
