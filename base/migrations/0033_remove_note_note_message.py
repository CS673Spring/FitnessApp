# Generated by Django 4.0.2 on 2022-04-11 14:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0032_alter_file_trainer_alter_payment_trainer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='note',
            name='note_message',
        ),
    ]
