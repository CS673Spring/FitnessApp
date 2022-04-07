# Generated by Django 4.0.2 on 2022-04-06 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0024_note'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('existingPath', models.CharField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('eof', models.BooleanField()),
            ],
        ),
    ]
