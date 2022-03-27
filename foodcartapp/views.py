import json

import phonenumbers
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

    # firstname
    if 'firstname' not in order_data:
        err_msg = 'Обязательное поле.'
    elif not isinstance(order_data['firstname'], str):
        err_msg = 'Not a valid string.'
    elif not order_data['firstname']:
        err_msg = 'Это поле не может быть пустым.'
    if err_msg:
        return Response({'firstname': err_msg}, status=status.HTTP_400_BAD_REQUEST)

    # lastname
    if 'lastname' not in order_data:
        err_msg = 'Обязательное поле.'
    elif not isinstance(order_data['lastname'], str):
        err_msg = 'Not a valid string.'
    elif not order_data['lastname']:
        err_msg = 'Это поле не может быть пустым.'
    if err_msg:
        return Response({'lastname': err_msg}, status=status.HTTP_400_BAD_REQUEST)

    # address
    if 'address' not in order_data:
        err_msg = 'Обязательное поле.'
    elif not isinstance(order_data['address'], str):
        err_msg = 'Not a valid string.'
    elif not order_data['address']:
        err_msg = 'Это поле не может быть пустым.'
    if err_msg:
        return Response({'address': err_msg}, status=status.HTTP_400_BAD_REQUEST)

    # phonenumber
    if 'phonenumber' not in order_data:
        err_msg = 'Обязательное поле.'
    elif not isinstance(order_data['phonenumber'], str):
        err_msg = 'Not a valid string.'
    elif not order_data['phonenumber']:
        err_msg = 'Это поле не может быть пустым.'
    if err_msg:
        return Response({'phonenumber': err_msg}, status=status.HTTP_400_BAD_REQUEST)
    try:
        parsed_number = phonenumbers.parse(order_data['phonenumber'], "RU")
        if phonenumbers.is_valid_number(parsed_number):
            order_data['phonenumber'] = f"+{parsed_number.country_code}{parsed_number.national_number}"
        else:
            err_msg = 'Введен некорректный номер телефона.'
    except phonenumbers.phonenumberutil.NumberParseException:
        err_msg = 'Введен некорректный номер телефона.'
    if err_msg:
        return Response({'phonenumber': err_msg}, status=status.HTTP_400_BAD_REQUEST)

    # products
    if 'products' not in order_data:
        err_msg = 'Обязательное поле.'
    elif not order_data['products']:
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
        try:
            product = Product.objects.get(id=order_product["product"])
        except Product.DoesNotExist:
            new_order.delete()
            return Response({'products': 'Недопустимый первичный ключ "9999"'}, status=status.HTTP_400_BAD_REQUEST)

        new_order.items.add(product, through_defaults={'qty': order_product["quantity"]})
    return Response({})
