# Generated by Django 4.2.7 on 2024-03-07 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_temporaryuser_unique_code'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='temporaryuser',
            options={},
        ),
        migrations.AlterField(
            model_name='temporaryuser',
            name='unique_code',
            field=models.CharField(max_length=6),
        ),
        migrations.AlterModelTable(
            name='temporaryuser',
            table=None,
        ),
    ]
