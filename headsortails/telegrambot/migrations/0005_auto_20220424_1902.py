# Generated by Django 3.2.13 on 2022-04-24 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegrambot', '0004_alter_profile_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='external_id',
            field=models.PositiveIntegerField(verbose_name='Telegram User ID'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='username',
            field=models.CharField(max_length=32, verbose_name='Username'),
        ),
    ]
