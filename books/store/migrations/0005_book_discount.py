# Generated by Django 3.2.10 on 2023-01-06 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_auto_20230105_1215'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='discount',
            field=models.IntegerField(null=True),
        ),
    ]
