# Generated by Django 4.2.11 on 2024-04-18 14:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bincol_pro', '0008_alter_bin_status_binemptyingactivity'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BinEmptyingActivity',
        ),
    ]