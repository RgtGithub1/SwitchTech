# Generated by Django 4.1.6 on 2023-07-11 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0014_alter_playeractivity_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playeractivity',
            name='category',
            field=models.CharField(default='', max_length=50),
        ),
    ]