# Create your models here.
# Create your models here.
from django.db import models
from home.models import Category
from django.contrib.auth.models import User


class QuizQuestion(models.Model):
    DIFFICULTY_LEVEL = (
        ("BG", "Beginner"),
        ("IN", "Intermediate"),
        ("AD", "Advanced"),
    )
    Technology = models.ForeignKey(Category,
                                   related_name='domain',
                                   default='',
                                   on_delete=models.CASCADE)
    difficulty = models.CharField(
        max_length=2, choices=DIFFICULTY_LEVEL, default='')
    question = models.CharField(max_length=500)
    # New field for code snippet
    code_snippet = models.TextField(blank=True, null=True)
    option_a = models.CharField(max_length=100)
    option_b = models.CharField(max_length=100)
    option_c = models.CharField(max_length=100)
    option_d = models.CharField(max_length=100)
    correct_answer = models.CharField(max_length=1, choices=[('a', 'a'),
                                                             ('b', 'b'),
                                                             ('c', 'c'),
                                                             ('d', 'd')])
    marks = models.IntegerField(default=10)

    def __str__(self):
        return self.question


class FinalQuizAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz_domain = models.CharField(max_length=50, null=True)
    score = models.IntegerField()
    created_at = models.DateTimeField()
