from django.db import models
from django.utils import timezone


class Place(models.Model):
    address = models.CharField(
        'адрес',
        max_length=100,
        unique=True,
    )
    lat = models.DecimalField(
        'широта', decimal_places=2, max_digits=9, null=True, blank=True
    )
    lon = models.DecimalField(
        'долгота', decimal_places=2, max_digits=9, null=True, blank=True
    )
    updated_at = models.DateTimeField(
        'дата/время обновления',
        default=timezone.now
    )

    class Meta:
        verbose_name = 'место'
        verbose_name_plural = 'места'

    def __str__(self):
        return f'{self.address} :: {self.updated_at} шт.'
