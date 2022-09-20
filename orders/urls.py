from django.urls import path
from . import views

urlpatterns = [
    path('place_order',views.place_order,name='place_order'),
    path('payments/',views.payments,name='payments'),
    path('payment_status/',views.payment_status,name='payment_status'),
    path('payment/',views.payment,name='payment'),
    path('cod/',views.cod,name='cod'),
    path('order_complete/',views.order_complete,name='order_complete'),
    path('my_orders',views.my_orders,name="my_orders"),
    
]
