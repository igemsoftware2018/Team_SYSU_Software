# Generated by Django 2.1.1 on 2018-09-08 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('design', '0009_auto_20180907_2006'),
    ]

    operations = [
        migrations.AddField(
            model_name='circuit',
            name='Comment',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='circuit',
            name='Description',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='circuit',
            name='Update_time',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
