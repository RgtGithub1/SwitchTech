# Generated by Django 4.1.6 on 2023-08-08 06:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_feedback'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedback',
            name='exp_anythingelse_about_STS',
        ),
        migrations.RemoveField(
            model_name='feedback',
            name='exp_in_navigation_finding_features',
        ),
        migrations.RemoveField(
            model_name='feedback',
            name='mylearningpage_layout_presentation',
        ),
        migrations.RemoveField(
            model_name='feedback',
            name='quiz_engaging_and_interactive',
        ),
        migrations.RemoveField(
            model_name='feedback',
            name='quiz_evaluation_of_tech_accuration',
        ),
    ]