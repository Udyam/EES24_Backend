# Generated by Django 5.0 on 2024-01-10 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0005_remove_user_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.IntegerField(default=-1, max_length=10),
            preserve_default=False,
        ),
    ]
