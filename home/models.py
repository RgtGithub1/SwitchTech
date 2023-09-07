import random
import uuid
from django.db import models
from django.contrib.auth.models import User
import pytz
from django.utils import timezone


class QuizUserScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz_domain = models.CharField(max_length=50, null=True)
    score = models.IntegerField()
    created_at = models.DateTimeField()
    is_attempted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.localtime(
                timezone.now(), timezone=pytz.timezone('Asia/Kolkata'))
        super().save(*args, **kwargs)


class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateField(auto_now=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    category_name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.category_name

    class Meta:
        verbose_name_plural = "Categories"


class Question(BaseModel):
    category = models.ForeignKey(Category, related_name='category',
                                 on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    marks = models.IntegerField(default=10)

    def __str__(self) -> str:
        return self.question

    def get_answers(self):
        answer_objs = list(Answer.objects.filter(question=self))
        random.shuffle(answer_objs)
        data = []
        for answer_obj in answer_objs:
            data.append({
                'answer': answer_obj.answer,
                'is_correct': answer_obj.is_correct
            })
        return data


class Answer(BaseModel):
    question = models.ForeignKey(
        Question, related_name='question_answer', on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.answer


class CourseSuggession(models.Model):
    DIFFICULTY_LEVEL = (
        ("BG", "Beginner"),
        ("IN", "Intermediate"),
        ("AD", "Advanced"),
    )
    technology = models.ForeignKey(
        Category, related_name='suggesstion', on_delete=models.CASCADE)
    course_url = models.URLField(max_length=1000)
    difficulty = models.CharField(
        max_length=2, choices=DIFFICULTY_LEVEL, default='BG')
    course_name = models.CharField(max_length=100, default=' ')
    course_instructor = models.CharField(max_length=50, default=' ')
    ratings = models.FloatField(default=4.0)
    course_duration = models.FloatField(null=True)

    class Meta:
        db_table = 'course_suggestion'
        verbose_name_plural = "Course Suggestion"

    def __str__(self) -> str:
        return self.course_url


class Otp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mail = models.CharField(max_length=50)
    otp = models.CharField(max_length=50)
    count = models.IntegerField(default=0)
    assigned_to = models.CharField(max_length=100, default=None, null=True)


class Video(models.Model):
    DIFFICULTY_LEVEL = (
        ("BG", "Begginer"),
        ("IN", "Intermediate"),
        ("AD", "Advanced"),
    )
    title = models.CharField(max_length=100)
    difficulty = models.CharField(
        max_length=2, choices=DIFFICULTY_LEVEL, default='BG')
    video_id = models.CharField(max_length=50)
    duration = models.DurationField()  # Duration as a timedelta object
    created_at = models.DateTimeField(auto_now_add=True)
    technology_v = models.ForeignKey(
        Category, related_name='tech', on_delete=models.CASCADE)


class PlayerActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    current_time = models.FloatField()
    youtube_id = models.CharField(max_length=25)
    percentage = models.FloatField(default=0.0)
    category = models.CharField(max_length=50)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"PlayerActivity - youtube_id: {self.youtube_id}, " \
               f"current_time: {self.current_time}, " \
               f"percentage: {self.percentage}, " \
               f"is_completed: {self.is_completed}"


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    overall_exp_with_STS = models.CharField(max_length=50)
    expectation_in_assisting_tech_transition = models.CharField(max_length=50)
    udm_yt_recom_helpful = models.CharField(max_length=50)
    cs_align_withur_curt_knowledge_levl = models.CharField(max_length=50)
    conveniency_accessing_recom_yt_cs = models.CharField(max_length=50)
    valueof_progs_tracking_feature_on_dashboard = \
        models.CharField(max_length=50)
    motivate_to_complete_course = models.CharField(max_length=50)
    specific_feature_you_feel_missing = models.CharField(max_length=1000)
    how_app_enhanced = models.CharField(max_length=1000)
    technical_prob_performance_issue = models.CharField(max_length=1000)
