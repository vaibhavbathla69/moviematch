# Generated by Django 5.2 on 2025-04-30 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0004_alter_movie_movie_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='movie_id',
            field=models.IntegerField(default=1, unique=True),
        ),
    ]
