# Generated by Django 5.1.5 on 2025-02-24 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0008_chargecode_and_usage_restructure"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chargecode",
            name="code",
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
