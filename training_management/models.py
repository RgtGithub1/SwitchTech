from django.db import models

# Create your models here.
class MeetingTraining(models.Model):
    MEETING_TYPES = (
        ('custom', 'Custom'),
        ('recurring', 'Recurring'),
    )

    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPES)
    title = models.CharField(max_length=200)
    training_name = models.CharField(max_length=200, blank=True, null=True)
    select_training = models.CharField(max_length=100, blank=True, null=True)
    year = models.CharField(max_length=4, blank=True, null=True)
    trainer_name = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title