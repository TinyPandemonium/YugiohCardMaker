# Generated by Django 3.2.18 on 2023-05-10 17:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0004_card_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=200)),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.card')),
            ],
        ),
    ]