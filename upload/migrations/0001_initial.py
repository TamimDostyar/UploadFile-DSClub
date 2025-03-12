# Generated by Django 5.1.7 on 2025-03-12 02:41

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to='uploads/')),
                ('uploaded_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
