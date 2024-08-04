# Generated by Django 5.0.7 on 2024-08-04 08:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('modules', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='modules.module')),
            ],
        ),
    ]
