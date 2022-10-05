from multiprocessing import context
from django.shortcuts import render,redirect,get_object_or_404

from store.models import Product,Variation
from .models import Wishlist,WishlistItem

# Create your views here.
def _wishlist_id(request):
    wishlist=request.session.session_key
    if not wishlist:
        wishlist=request.session.create()
    return wishlist

def wishlist(request):     
    
    wishlist_items=WishlistItem.objects.filter(user=request.user)   
    context={
        'wishlist_items': wishlist_items
    }
    return render(request,"store/wish_list.html",context)
def add_wishlist(request, product_id):
    current_user = request.user
    product=Product.objects.get(id=product_id)

#if the user is not authenticated or logged in 

    if current_user.is_authenticated:
        product_variation = []
        if request.method =='POST':
            for item in request.POST:
                key = item
                value=request.POST[key]

                try:
                    variation=Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
#wishlistItem
        is_wishlist_item_exists=WishlistItem.objects.filter(product=product,user=current_user).exists()
        if is_wishlist_item_exists:
            pass
        else:
            cart_item=WishlistItem.objects.create(
                product     =product,
                
                user        =current_user
            )
            cart_item.save()
        return redirect('wishlist')
#if the user is not authenticated 
    else:

        product_variation = []
        if request.method =='POST':
            for item in request.POST:
                key = item
                value=request.POST[key]

                try:
                    variation=Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
#wishlist

        try:
            wishlist=Wishlist.objects.get(wishlist_id=_wishlist_id(request))
        
        except Wishlist.DoesNotExist:
            wishlist=Wishlist.objects.create(
                wishlist_id=_wishlist_id(request)
            )
        wishlist.save()
#WishlistItem
        is_wishlist_item_exists=WishlistItem.objects.filter(product=product,wishlist=wishlist).exists()
        if is_wishlist_item_exists:
            wishlist_item=WishlistItem.objects.filter(product=product,wishlist=wishlist)
        #item id
            ex_var_list=[]
            id=[]
            for item in wishlist_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            if product_variation in ex_var_list:
                index=ex_var_list.index(product_variation)
                item_id=id[index]
                item=WishlistItem.objects.get(product=product,id=item_id)
                item.save()
            else:
                item=WishlistItem.objects.create(product=product,quantity=1,wishlist=wishlist)
                if len(product_variation) > 0 :
                    item.variations.clear()
                    item.variations.add(*product_variation)    
                item.save()
        else:

            wishlist_item=WishlistItem.objects.create(
                product     =product,
                quantity    =1,
                wishlist    =wishlist
            )
            if len(product_variation) >0 :
                wishlist_item.variations.clear()
                for item in product_variation:
                    wishlist_item.variations.add(*product_variation)
            wishlist_item.save()
        return redirect('wishlist')

def remove_wishlist_item(request,product_id,wishlist_item_id):
    
    product=get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated:
        wishlist_item=WishlistItem.objects.get(product=product,user=request.user,id=wishlist_item_id)
    else:
        wishlist=Wishlist.objects.get(wishlist_id=_wishlist_id(request))
        wishlist_item=WishlistItem.objects.get(product=product,wishlist=wishlist,id=wishlist_item_id)
    wishlist_item.delete()
    return redirect('wishlist')