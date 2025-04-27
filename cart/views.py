from multiprocessing import context
from urllib import request
from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from account.views import login
from cart.models import Cart, CartItem
from store.models import Product, Variation

def cart_id(request):
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart


def addcart(request, product_id):
    product = Product.objects.get(id=product_id)
    variation_product = []
    
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                variation_product.append(variation)
            except:
                pass
    
    try:
        cart = Cart.objects.get(cart_id=cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=cart_id(request)
        )
        print(f"Created new cart: {cart.cart_id}")
    cart.save()
    
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(product=product, user=request.user)
    else:
        cart_items = CartItem.objects.filter(product=product, cart=cart)
    
    if cart_items.exists():
        cart_item = cart_items.first()
        cart_item.quantity += 1
        cart_item.save()
    else:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
                user=request.user,
            )
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
        if variation_product:
            cart_item.variations.set(variation_product)
        cart_item.save()

    return redirect('cart')


def removecart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id=cart_id(request))

    # Safely get the first matching CartItem
    cart_items = CartItem.objects.filter(product=product, cart=cart)

    if cart_items.exists():
        cart_item = cart_items.first()
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    return redirect('cart')


def removecartitem(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id=cart_id(request))

    # Safely get the first matching CartItem
    cart_items = CartItem.objects.filter(product=product, cart=cart)

    if cart_items.exists():
        cart_items.first().delete()

    return redirect('cart')


def cart(request, total=0, quantity=0, cart_item=None):
    grand_total = 0  # Initialize grand_total
    tax = 0  # Initialize tax
    cart_items = []  # Initialize cart_items

    try:
        cart = Cart.objects.get(cart_id=cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity  # Corrected to cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax  # Now this will always be set

    except Cart.DoesNotExist:
        # Handle case where cart does not exist
        cart_items = []  # Ensure cart_items is defined
    except Exception as e:
        # Optionally log the exception or handle it
        print(f"An error occurred: {e}")

    context = {
        'total': total,  # Removed leading space in key
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_item=None):
    grand_total = 0  # Initialize grand_total
    tax = 0  # Initialize tax
    cart_items = []  # Initialize cart_items

    try:
        cart = Cart.objects.get(cart_id=cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity  # Corrected to cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax  # Now this will always be set

    except Cart.DoesNotExist:
        # Handle case where cart does not exist
        cart_items = []  # Ensure cart_items is defined
    except Exception as e:
        # Optionally log the exception or handle it
        print(f"An error occurred: {e}")

    context = {
        'total': total,  # Removed leading space in key
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context)
