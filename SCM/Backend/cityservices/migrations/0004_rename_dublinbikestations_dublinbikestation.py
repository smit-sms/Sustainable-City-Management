# Generated by Django 4.2.7 on 2024-02-28 13:51

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("cityservices", "0003_dublinbikestations"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="DublinBikeStations",
            new_name="DublinBikeStation",
        ),
    ]
