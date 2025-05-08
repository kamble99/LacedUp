import razorpay
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from LacedUp import settings
from .models import Order, OrderProduct, Payment
from cart.models import CartItem
import datetime
from django.core.mail import send_mail


def place_order(request):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    if cart_items.count() <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        grand_total += (cart_item.product.price * cart_item.quantity)
    tax = (2 * grand_total) / 100  # Assuming tax is 2%
    total = grand_total + tax

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        order_note = request.POST.get('order_note')
        
        # Save order
        order = Order()
        order.user = current_user
        order.first_name = first_name
        order.last_name = last_name
        order.phone = phone
        order.email = email
        order.address_line_1 = address_line_1
        order.address_line_2 = address_line_2
        order.country = country
        order.state = state
        order.city = city
        order.order_note = order_note
        order.order_total = grand_total
        order.tax = tax
        order.ip = request.META.get('REMOTE_ADDR')
        order.save()

        # Generate order number (e.g., date + id)
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr, mt, dt)
        current_date = d.strftime("%Y%m%d")  # example: 20250428
        order_number = current_date + str(order.id)
        order.order_number = order_number
        order.save()

        # Save ordered products
        ordered_products = []
        for item in cart_items:
            ordered_product = OrderProduct.objects.create(
                order=order,
                user=current_user,
                product=item.product,
                quantity=item.quantity,
                product_price=item.product.price,
                ordered=True,
            )
            ordered_product.variations.set(item.variations.all())
            ordered_product.save()
            ordered_products.append(ordered_product)

        # Clear the cart
        cart_items.delete()

        context = {
            'order': order,
            'ordered_products': ordered_products,   # <-- passed to template
            'total': grand_total,
            'tax': tax,
            'grand_total': total,
        }
        return render(request, 'payment.html', context)
    
    else:
        return redirect('checkout')



@csrf_exempt
def payment(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return redirect('store')

    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Create a Razorpay order
    razorpay_order = client.order.create({
        "amount": int(order.order_total * 100),  # Razorpay uses paise (₹1 = 100 paise)
        "currency": "INR",
        "payment_capture": "1"
    })

    order.razorpay_order_id = razorpay_order['id']
    order.save()

    context = {
        'order': order,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
        'amount': order.order_total,
        'currency': 'INR',
    }
    return render(request, 'payment_page.html', context)

def payment_success(request, order_id, payment_id):
    try:
        order = Order.objects.get(id=order_id)
        payment, created = Payment.objects.get_or_create(payment_id=payment_id)

        order.payment = payment
        order.status = 'Completed'
        order.is_ordered = True
        order.save()

        ordered_products = OrderProduct.objects.filter(order=order)

        # Calculate totals
        total = sum(item.product_price * item.quantity for item in ordered_products)
        tax = order.tax
        grand_total = total + tax

        return render(request, 'payment_success.html', {
            'order': order,
            'ordered_products': ordered_products,
            'total': total,
            'tax': tax,
            'grand_total': grand_total,
        })

    except Order.DoesNotExist:
        return render(request, 'error.html', {'message': 'Order not found'})

