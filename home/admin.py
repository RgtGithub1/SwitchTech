from django.contrib import admin
from .models import Question, QuizAttempt, QuizUserScore, Otp, Answer
from .models import PlayerActivity, CourseSuggession, Category, Video

admin.site.register(Category)


class AnswerAdmin(admin.StackedInline):
    model = Answer


class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerAdmin]
    list_filter=['category']


admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(PlayerActivity)


@admin.register(QuizUserScore)
class QuizScore(admin.ModelAdmin):
    list_display = ['user', 'quiz_domain', 'created_at', 'score']


@admin.register(CourseSuggession)
class CourseSuggession(admin.ModelAdmin):
    list_filter = ['technology']
    list_display = ['technology', 'difficulty',
                    'course_name', 'course_duration']


@admin.register(Video)
class Video(admin.ModelAdmin):
    list_filter = ['technology_v']
    list_display = ['technology_v', 'title', 'difficulty']


@admin.register(Otp)
class Otp(admin.ModelAdmin):
    list_display = ['user', 'mail', 'otp', 'count', 'assigned_to']


@admin.register(QuizAttempt)
class QuizAttempt(admin.ModelAdmin):
    list_display = ['user', 'timer', 'domain']
