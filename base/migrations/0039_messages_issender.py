# Generated by Django 4.0.2 on 2022-04-18 03:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0038_messages'),
    ]

    operations = [
        migrations.AddField(
            model_name='messages',
            name='isSender',
            field=models.BooleanField(default=False),
        ),
    ]