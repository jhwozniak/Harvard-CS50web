# Generated by Django 3.2.12 on 2024-05-06 07:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0008_auto_20240506_0743'),
    ]

    operations = [
        migrations.RenameField(
            model_name='following',
            old_name='follower_id',
            new_name='follower',
        ),
        migrations.RenameField(
            model_name='following',
            old_name='following_id',
            new_name='following',
        ),
    ]