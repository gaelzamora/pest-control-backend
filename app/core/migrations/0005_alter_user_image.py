# Generated by Django 3.2.25 on 2024-12-01 19:54

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_rename_sucursal_user_branch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.user_image_file_path),
        ),
    ]
