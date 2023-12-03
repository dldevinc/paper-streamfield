# Generated by Django 4.2.7 on 2023-12-03 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_page_epigraph'),
    ]

    operations = [
        migrations.CreateModel(
            name='Advantage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(verbose_name='title')),
                ('description', models.TextField(verbose_name='description')),
            ],
            options={
                'verbose_name': 'advantage',
            },
        ),
    ]
