# Generated by Django 5.1.3 on 2024-11-08 07:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0004_remove_question_option_a_remove_question_option_b_and_more'),
        ('results', '0004_rename_quiz_quizresult_quiz_id'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='answers',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='result',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='result',
            unique_together={('quiz', 'student')},
        ),
    ]
