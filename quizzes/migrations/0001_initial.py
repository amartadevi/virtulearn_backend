# Generated by Django 5.1.1 on 2024-09-08 13:09

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField()),
                ('option_a', models.TextField(blank=True, null=True)),
                ('option_b', models.TextField(blank=True, null=True)),
                ('option_c', models.TextField(blank=True, null=True)),
                ('option_d', models.TextField(blank=True, null=True)),
                ('correct_answer', models.CharField(blank=True, max_length=1, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(default='no description given')),
                ('quiz_type', models.CharField(choices=[('assignment', 'Assignment'), ('practice', 'Practice Quiz'), ('graded', 'Graded Quiz')], default='practice', max_length=20)),
                ('category', models.CharField(choices=[('QNA', 'Question and Answer'), ('MCQ', 'Multiple Choice Question')], default='QNA', max_length=10)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('quiz_duration', models.PositiveIntegerField(default=15, help_text='Duration of the quiz in minutes')),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.DecimalField(decimal_places=2, max_digits=5)),
                ('date_taken', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='StudentAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selected_option', models.CharField(blank=True, max_length=1, null=True)),
                ('answer_text', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
