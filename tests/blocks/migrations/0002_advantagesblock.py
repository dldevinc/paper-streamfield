# Generated by Django 4.2.7 on 2023-12-03 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blocks', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdvantagesBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header', models.TextField(verbose_name='header')),
            ],
            options={
                'verbose_name': 'Advantages',
            },
        ),
    ]
