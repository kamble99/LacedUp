from .models import Cart, CartItem
from .views import cart_id

def counter(request):
    cart_count = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.filter(cart_id=cart_id(request)).first()
            if cart:
                cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            else:
                cart_items = []
        for cart_item in cart_items:
            cart_count += cart_item.quantity
    except:
        cart_count = 0

    return dict(cart_count=cart_count)
