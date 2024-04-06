# Generated by Django 4.2.11 on 2024-04-06 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bincol_pro', '0005_bin_assigned_driver'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaint',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Resolved', 'Resolved'), ('Rejected', 'Rejected'), ('In Progress', 'In Progress')], default='Pending', max_length=20),
        ),
    ]
