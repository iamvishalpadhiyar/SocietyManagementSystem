# Generated by Django 4.0 on 2022-03-24 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0022_alter_pay_payid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pay',
            name='pamount',
            field=models.CharField(max_length=50),
        ),
    ]