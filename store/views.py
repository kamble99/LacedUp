from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from cart.models import CartItem
from cart.views import cart_id
from store.models import Product
from category.models import Category
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q

def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator=Paginator(products,6)
        page=request.GET.get('page')
        paged_product=paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator=Paginator(products,4)
        page=request.GET.get('page')
        paged_product=paginator.get_page(page)
        product_count = products.count()

    return render(request, 'store/store.html', {'products': paged_product, 'product_count': product_count, 'categories': categories})

def product_detail(request,category_slug,product_slug):
    # categoey = Category.object.all()
    try:
        single_product=Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart=CartItem.objects.filter(cart__cart_id=cart_id(request),product=single_product).exists()
    except Exception as e:
        raise e
    context={
        'single_product':single_product,
        'in_cart':in_cart,
        # 'category':categoey
    }
    return render(request,'store/product_detail.html',context)

def search(request):
    if 'search' in request.GET:
        search=request.GET['search']
        if search:
            products=Product.objects.order_by('created_date').filter(Q(description__icontains=search , product_name__icontains=search))
            product_count = products.count()

        

    return render(request, 'store/store.html',{'products':products,'product_count':product_count})