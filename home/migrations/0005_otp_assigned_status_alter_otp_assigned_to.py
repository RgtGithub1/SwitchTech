# Generated by Django 4.1.6 on 2023-08-02 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='otp',
            name='assigned_status',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='otp',
            name='assigned_to',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
    ]
