# Generated by Django 3.2 on 2022-04-23 03:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=100, unique=True, verbose_name='адрес')),
                ('lat', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True, verbose_name='широта')),
                ('lon', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True, verbose_name='долгота')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='дата/время обновления')),
            ],
            options={
                'verbose_name': 'место',
                'verbose_name_plural': 'места',
            },
        ),
    ]
