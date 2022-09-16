from itertools import product
from django.shortcuts import render
from store.models import Product
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator

@never_cache
def home(request):
    products=Product.objects.all().filter(is_available=True)
    paginator = Paginator(products, 4)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    context={
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request,'home.html',context)
