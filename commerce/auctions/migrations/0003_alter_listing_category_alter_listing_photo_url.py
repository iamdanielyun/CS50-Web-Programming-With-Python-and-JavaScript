# Generated by Django 4.0.1 on 2022-02-15 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_listing_comment_bid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='listing',
            name='photo_url',
            field=models.URLField(blank=True),
        ),
    ]