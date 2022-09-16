from django.urls import path
from . import views

urlpatterns = [
    path('place_order',views.place_order,name='place_order'),
    path('payments/',views.payments,name='payments'),
    path('cod/',views.cod,name='cod'),
    path('order_complete/',views.order_complete,name='order_complete'),
    path('my_orders',views.my_orders,name="my_orders"),
]
