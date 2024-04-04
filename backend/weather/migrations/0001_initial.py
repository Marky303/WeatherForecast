# Generated by Django 5.0.3 on 2024-04-04 13:25

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(null=True)),
                ('temp', models.DecimalField(decimal_places=1, default=-1, max_digits=6)),
                ('dwpt', models.DecimalField(decimal_places=1, default=-1, max_digits=6)),
                ('rhum', models.DecimalField(decimal_places=1, default=-1, max_digits=6)),
                ('wdir', models.DecimalField(decimal_places=1, default=-1, max_digits=6)),
                ('wspd', models.DecimalField(decimal_places=1, default=-1, max_digits=6)),
                ('pres', models.DecimalField(decimal_places=1, default=-1, max_digits=6)),
                ('coco', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(27)])),
            ],
        ),
        migrations.CreateModel(
            name='Prediction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prediction_time', models.DateTimeField(null=True)),
                ('accuracy_temp', models.DecimalField(decimal_places=1, default=-1, max_digits=6)),
                ('accuracy_dwpt', models.DecimalField(decimal_places=1, default=-1, max_digits=6)),
                ('accuracy_rhum', models.DecimalField(decimal_places=1, default=-1, max_digits=6)),
                ('accuracy_wdir', models.DecimalField(decimal_places=1, default=-1, max_digits=6)),
                ('accuracy_wspd', models.DecimalField(decimal_places=1, default=-1, max_digits=6)),
                ('accuracy_pres', models.DecimalField(decimal_places=1, default=-1, max_digits=6)),
                ('accuracy', models.DecimalField(decimal_places=1, default=-1, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='Predicted_Entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(null=True)),
                ('temp', models.DecimalField(decimal_places=1, default=-1, max_digits=6)),
                ('dwpt', models.DecimalField(decimal_places=1, default=-1, max_digits=6)),
                ('rhum', models.DecimalField(decimal_places=1, default=-1, max_digits=6)),
                ('wdir', models.DecimalField(decimal_places=1, default=-1, max_digits=6)),
                ('wspd', models.DecimalField(decimal_places=1, default=-1, max_digits=6)),
                ('pres', models.DecimalField(decimal_places=1, default=-1, max_digits=6)),
                ('coco', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(27)])),
                ('prediction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='weather.prediction')),
            ],
        ),
    ]
