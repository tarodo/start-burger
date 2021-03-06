from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField("название", max_length=50)
    address = models.CharField(
        "адрес",
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        "контактный телефон",
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = "ресторан"
        verbose_name_plural = "рестораны"

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = RestaurantMenuItem.objects.filter(availability=True).values_list(
            "product"
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField("название", max_length=50)

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("название", max_length=50)
    category = models.ForeignKey(
        ProductCategory,
        verbose_name="категория",
        related_name="products",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        "цена", max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    image = models.ImageField("картинка")
    special_status = models.BooleanField(
        "спец.предложение",
        default=False,
        db_index=True,
    )
    description = models.TextField(
        "описание",
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name="menu_items",
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="menu_items",
        verbose_name="продукт",
    )
    availability = models.BooleanField("в продаже", default=True, db_index=True)

    class Meta:
        verbose_name = "пункт меню ресторана"
        verbose_name_plural = "пункты меню ресторана"
        unique_together = [["restaurant", "product"]]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class PriceQuerySet(models.QuerySet):
    def with_prices(self):
        return self.annotate(
            full_price=Sum(F("order_products__price") * F("order_products__quantity"))
        )

    def fetch_restaurants(self):
        orders = self.filter(status=1).prefetch_related('products')

        restaurant_menu_items = RestaurantMenuItem.objects.filter(
            availability=True
        ).select_related('restaurant', 'product')

        for order in orders:
            order.restaurants = set()
            order.restaurant_distances = []

            for order_item in order.products.all():
                product_restaurants = [
                    rest_item.restaurant
                    for rest_item in restaurant_menu_items
                    if order_item.id == rest_item.product.id
                ]

                if not order.restaurants:
                    order.restaurants = set(product_restaurants)

                order.restaurants &= set(product_restaurants)
        return orders


class Order(models.Model):
    firstname = models.CharField("имя", max_length=50, db_index=True)
    lastname = models.CharField("фамилия", max_length=50, blank=True, db_index=True)
    phonenumber = PhoneNumberField(verbose_name="номер владельца")
    address = models.CharField("адрес", max_length=1000, db_index=True)
    products = models.ManyToManyField(
        Product, related_name="orders", through="OrderProduct"
    )
    payment_method = models.SmallIntegerField(
        choices=[
            (1, "Наличностью"),
            (2, "Электронно"),
        ],
        db_index=True,
        verbose_name="метод оплаты",
    )
    comment = models.TextField(
        "комментарий",
        blank=True,
    )
    status = models.SmallIntegerField(
        choices=[
            (1, "Необработанный"),
            (2, "Подтверждённый"),
        ],
        db_index=True,
        default=1,
        verbose_name="статус",
    )
    registered_at = models.DateTimeField(
        default=timezone.now, verbose_name="дата/время создания", db_index=True
    )
    called_at = models.DateTimeField(
        verbose_name="дата/время звонка", db_index=True, null=True, blank=True
    )
    delivered_at = models.DateTimeField(
        verbose_name="дата/время доставки", db_index=True, null=True, blank=True
    )

    restaurant = models.ForeignKey(
        Restaurant,
        related_name="orders",
        on_delete=models.SET_NULL,
        verbose_name="ресторан",
        null=True,
        blank=True,
    )

    objects = PriceQuerySet.as_manager()

    class Meta:
        verbose_name = "заказ"
        verbose_name_plural = "заказы"

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class OrderProduct(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name="заказ",
        related_name="order_products",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="продукт",
        related_name="order_products",
    )
    quantity = models.PositiveIntegerField(
        verbose_name="количество", validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        "цена", max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = "продукт"
        verbose_name_plural = "состав заказа"

    def __str__(self):
        return f"{self.product} {self.quantity} шт."
