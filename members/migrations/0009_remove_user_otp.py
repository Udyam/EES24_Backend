# Generated by Django 5.0 on 2024-01-12 11:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0008_user_is_verified'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='otp',
        ),
    ]
