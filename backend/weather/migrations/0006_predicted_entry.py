# Generated by Django 5.0.3 on 2024-03-27 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0005_alter_entry_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='predicted_Entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]