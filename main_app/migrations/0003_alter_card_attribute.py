# Generated by Django 3.2.18 on 2023-05-09 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_auto_20230508_1958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='attribute',
            field=models.CharField(default='', max_length=6),
        ),
    ]
