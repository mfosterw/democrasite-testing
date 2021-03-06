# Generated by Django 3.2 on 2021-05-04 22:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('elections', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bill',
            name='active',
        ),
        migrations.AddField(
            model_name='bill',
            name='state',
            field=models.CharField(choices=[('o', 'Open'), ('a', 'Approved'), ('r', 'Rejected'), ('f', 'Not Enough Votes'), ('c', 'PR Closed')], default='o', max_length=1),
        ),
        migrations.AlterField(
            model_name='bill',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
