# Generated by Django 4.0.2 on 2022-04-11 20:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0034_remove_chat_isaccepted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chat',
            name='chat_message',
        ),
    ]
