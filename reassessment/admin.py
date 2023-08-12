from django.contrib import admin
from .models import QuizQuestion

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')
    list_display_links = ('id', 'question')
    search_fields = ('question',)
    list_filter = ['Technology']