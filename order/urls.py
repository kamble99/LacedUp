from django.urls import path
from . import views
urlpatterns=[
    path('place_order/',views.place_order,name='place_order'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('place_order/payment_success/<int:order_id>/<str:payment_id>/', views.payment_success, name='payment_success'),

]