from django.urls import path
from . import apis

app_name = 'training_management'


urlpatterns = [
    path('add_meeting/', apis.add_meeting, name='add_meeting'),
    path('meeting_list/', apis.meeting_list, name='meeting_list'),
    path('edit_meeting/<int:pk>/', apis.edit_meeting, name='edit_meeting'),
    path('delete_meeting/<int:pk>/', apis.delete_meeting, name='delete_meeting'),
]
