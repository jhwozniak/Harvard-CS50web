# Generated by Django 3.2.12 on 2024-05-06 07:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0007_auto_20240506_0703'),
    ]

    operations = [
        migrations.RenameField(
            model_name='following',
            old_name='follower',
            new_name='follower_id',
        ),
        migrations.RenameField(
            model_name='following',
            old_name='following',
            new_name='following_id',
        ),
    ]