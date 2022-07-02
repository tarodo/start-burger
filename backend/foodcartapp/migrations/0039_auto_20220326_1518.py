# Generated by Django 3.2 on 2022-03-26 12:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_auto_20220326_0645'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'заказ', 'verbose_name_plural': 'заказы'},
        ),
        migrations.AlterModelOptions(
            name='orderproduct',
            options={'verbose_name': 'продукт', 'verbose_name_plural': 'состав заказа'},
        ),
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.CharField(db_index=True, max_length=1000, verbose_name='адрес'),
        ),
        migrations.AlterField(
            model_name='order',
            name='firstname',
            field=models.CharField(db_index=True, max_length=50, verbose_name='имя'),
        ),
        migrations.AlterField(
            model_name='order',
            name='lastname',
            field=models.CharField(db_index=True, max_length=50, verbose_name='фамилия'),
        ),
        migrations.AlterField(
            model_name='orderproduct',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foodcartapp.order', verbose_name='заказ'),
        ),
        migrations.AlterField(
            model_name='orderproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foodcartapp.product', verbose_name='продукт'),
        ),
    ]