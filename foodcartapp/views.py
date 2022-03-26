import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


from .models import Product, Order


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    order_data = request.data
    err_msg = ''

    if 'products' not in order_data:
        err_msg = 'Обязательное поле.'
    elif order_data['products'] is None:
        err_msg = 'Это поле не может быть пустым.'
    elif not isinstance(order_data['products'], list):
        err_msg = 'Ожидался list со значениями, но был получен "str".'
    elif len(order_data['products']) == 0:
        err_msg = 'Этот список не может быть пустым.'

    if err_msg:
        return Response({'products': err_msg}, status=status.HTTP_400_BAD_REQUEST)

    new_order = Order.objects.create(
        firstname=order_data["firstname"],
        lastname=order_data["lastname"],
        phone=order_data["phonenumber"],
        address=order_data["address"]
    )
    for order_product in order_data["products"]:
        product = Product.objects.get(id=order_product["product"])
        new_order.items.add(product, through_defaults={'qty': order_product["quantity"]})
    return Response({})
