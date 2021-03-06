import requests
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from geopy import distance

from distance.models import Place
from foodcartapp.models import Order, Product, Restaurant


class Login(forms.Form):
    username = forms.CharField(
        label='Логин',
        max_length=75,
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Укажите имя пользователя'}
        ),
    )
    password = forms.CharField(
        label='Пароль',
        max_length=75,
        required=True,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}
        ),
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, 'templates/login.html', context={'form': form})

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect('restaurateur:RestaurantView')
                return redirect('start_page')

        return render(
            request,
            'templates/login.html',
            context={
                'form': form,
                'ivalid': True,
            },
        )


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url,
        params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        },
    )
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_place_coordinates(address):
    geocoder_token = settings.YANDEX_GEOCODER_KEY
    place, created = Place.objects.get_or_create(address=address)

    if not created:
        return place.lon, place.lat

    place_coords = fetch_coordinates(geocoder_token, address)
    if not place_coords:
        place.delete()
        return None

    lon, lat = place_coords
    place.lon = lon
    place.lat = lat
    place.save()
    return place_coords


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{
                item.restaurant_id: item.availability
                for item in product.menu_items.all()
            },
        }
        orderer_availability = [
            availability[restaurant.id] for restaurant in restaurants
        ]

        products_with_restaurants.append((product, orderer_availability))

    return render(
        request,
        template_name="templates/products_list.html",
        context={
            'products_with_restaurants': products_with_restaurants,
            'restaurants': restaurants,
        },
    )


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(
        request,
        template_name="templates/restaurants_list.html",
        context={
            'restaurants': Restaurant.objects.all(),
        },
    )


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.with_prices().fetch_restaurants()

    for order in orders:
        customer_coords = get_place_coordinates(order.address)
        if not customer_coords:
            order.restaurant_distances.append(('-', 'адрес не распознан'))
            continue
        for restaurant in order.restaurants:
            rest_coords = get_place_coordinates(restaurant.address)
            rest_distance = distance.distance(customer_coords, rest_coords).km
            order.restaurant_distances.append(
                (restaurant.name, round(rest_distance, 2))
            )
        order.restaurant_distances = sorted(
            order.restaurant_distances, key=lambda rest_dist: rest_dist[1]
        )

    return render(
        request,
        template_name='templates/order_items.html',
        context={
            'order_items': orders,
        },
    )
