# Generated by Django 4.2.16 on 2024-09-12 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Visitor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("email", models.EmailField(blank=True, max_length=254, null=True)),
                ("phone", models.CharField(blank=True, max_length=20, null=True)),
                ("purpose", models.CharField(max_length=255)),
                ("arrival_time", models.DateTimeField(auto_now_add=True)),
                ("departure_time", models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
