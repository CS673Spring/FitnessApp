# Generated by Django 4.0.2 on 2022-04-06 22:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0025_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='trainer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.trainer'),
        ),
    ]
