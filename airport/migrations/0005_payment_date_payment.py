# Generated by Django 4.2.3 on 2023-07-22 09:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("airport", "0004_payment"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="date_payment",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]