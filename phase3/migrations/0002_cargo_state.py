# Generated by Django 4.0.1 on 2022-01-20 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phase3', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cargo',
            name='state',
            field=models.CharField(default='mert', max_length=100),
            preserve_default=False,
        ),
    ]
