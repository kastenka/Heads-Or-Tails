# Generated by Django 3.2.13 on 2022-04-24 18:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('telegrambot', '0003_alter_profile_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='profile',
            unique_together=set(),
        ),
    ]