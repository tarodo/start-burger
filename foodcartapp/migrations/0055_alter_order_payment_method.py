# Generated by Django 3.2 on 2022-04-29 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0054_auto_20220429_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.SmallIntegerField(choices=[(1, 'Наличностью'), (2, 'Электронно')], db_index=True, verbose_name='метод оплаты'),
        ),
    ]
