
from multiprocessing import context
from sre_constants import CATEGORY
from tkinter import E
from django.shortcuts import render,get_object_or_404
from store.models import Product
from category.models import Category
from django.core.paginator import Paginator
from django.db.models import Q
from wishlists.models import Wishlist,WishlistItem

from store.models import ProductGallery

# Create your views here.
def store(request, category_slug=None):
    
    categories = None
    products = None
    

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        for single_product in products:
            product1=[]
        for single_product in products:
            
            product1.append({
                'id': single_product.id,
                'product_name': single_product.product_name,  
                'slug': single_product.slug,         
                'descrbtion' :single_product.descrbtion,    
                'price'  : single_product.price,       
                'image'  :single_product.image,       
                'stock'  : single_product.stock,       
                'is_available' : single_product.is_available, 
                'category'   :single_product.category,   
                'created_date' :single_product.created_date, 
                'modified_date':single_product.modified_date,
                'offer': (single_product.price-(single_product.category.offer * single_product.price)/100),
                 })
        paginator = Paginator(product1, 8)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        product1=[]
        for single_product in products:
            
            product1.append({
                'id': single_product.id,
                'product_name': single_product.product_name,  
                'slug': single_product.slug,         
                'descrbtion' :single_product.descrbtion,    
                'price'  : single_product.price,       
                'image'  :single_product.image,       
                'stock'  : single_product.stock,       
                'is_available' : single_product.is_available, 
                'category'   :single_product.category,   
                'created_date' :single_product.created_date, 
                'modified_date':single_product.modified_date,
                'offer': (single_product.price-(single_product.category.offer * single_product.price)/100),
                 })
        paginator = Paginator(product1, 8)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    
    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)

def product_detail(request,product_slug,category_slug):
    try:
        single_product=Product.objects.get(category__slug=category_slug,slug=product_slug)
        #get the product gallery
        product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
        

    except Exception as e:
        raise e
    product_offer = single_product.price-((single_product.category.offer*single_product.price)/100 )   
    wishlist = WishlistItem.objects.all()
    context={
        'single_product':single_product,
        'product_offer':product_offer,
        'product_gallery' :product_gallery,
        'wishlist':wishlist,
    }
    return render(request,'store/product_detail.html',context)



#search function

def search(request):
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            products=Product.objects.order_by("-created_date").filter(Q(descrbtion__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count=products.count()
            product1=[]
        for single_product in products:
            
            product1.append({
                'id': single_product.id,
                'product_name': single_product.product_name,  
                'slug': single_product.slug,         
                'descrbtion' :single_product.descrbtion,    
                'price'  : single_product.price,       
                'image'  :single_product.image,       
                'stock'  : single_product.stock,       
                'is_available' : single_product.is_available, 
                'category'   :single_product.category,   
                'created_date' :single_product.created_date, 
                'modified_date':single_product.modified_date,
                'offer': (single_product.price-(single_product.category.offer * single_product.price)/100),
                 })
            context={
                'products':product1,
                'product_count' : product_count,
            }

    return render(request,'store/store.html',context)
