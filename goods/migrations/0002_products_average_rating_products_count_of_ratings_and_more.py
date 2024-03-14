# Generated by Django 4.2.7 on 2024-03-13 16:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='average_rating',
            field=models.FloatField(default=0, verbose_name='Средний рейтинг'),
        ),
        migrations.AddField(
            model_name='products',
            name='count_of_ratings',
            field=models.IntegerField(default=0, verbose_name='Количество оценок'),
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField()),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='goods.products')),
            ],
        ),
    ]