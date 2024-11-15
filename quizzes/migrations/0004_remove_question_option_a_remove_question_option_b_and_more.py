# Generated by Django 5.1.3 on 2024-11-06 15:34

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0003_quiz_content_quiz_note_alter_quiz_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='option_a',
        ),
        migrations.RemoveField(
            model_name='question',
            name='option_b',
        ),
        migrations.RemoveField(
            model_name='question',
            name='option_c',
        ),
        migrations.RemoveField(
            model_name='question',
            name='option_d',
        ),
        migrations.AddField(
            model_name='question',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='question',
            name='options',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='question',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='quiz',
            name='is_ai_generated',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='question',
            name='correct_answer',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='category',
            field=models.CharField(choices=[('QNA', 'Question and Answer'), ('MCQ', 'Multiple Choice Question')], default='MCQ', max_length=10),
        ),
    ]
