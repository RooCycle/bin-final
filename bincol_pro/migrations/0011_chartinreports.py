# Generated by Django 4.2.11 on 2024-05-04 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bincol_pro', '0010_aboutus_contactus'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChartInReports',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('html_content', models.TextField()),
            ],
        ),
    ]
