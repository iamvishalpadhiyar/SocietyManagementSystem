# Generated by Django 4.0 on 2022-01-01 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_alter_secuser_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='secuser',
            name='pic',
            field=models.FileField(default='avatar.jpg', upload_to='profile'),
        ),
    ]
