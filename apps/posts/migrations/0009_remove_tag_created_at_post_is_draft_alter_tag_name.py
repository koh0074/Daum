# Generated by Django 5.1.3 on 2024-11-21 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_tag_created_at_alter_tag_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='created_at',
        ),
        migrations.AddField(
            model_name='post',
            name='is_draft',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=20, unique=True, verbose_name='태그명'),
        ),
    ]
