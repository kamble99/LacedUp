from django.urls import path
from . import views

urlpatterns=[
    path('',views.cart,name='cart'),
    path('addcart/<int:product_id>/',views.addcart,name='addcart'),
    path('removecart/<int:product_id>/',views.removecart,name='removecart'),
    path('removecartitem/<int:product_id>/',views.removecartitem,name='removecartitem')
    

]