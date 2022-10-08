
from django.shortcuts import render,redirect
from accounts.models import Account
from django.contrib import messages,auth
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from store.models import Product,Variation
from django.db.models import Q
from category.models import Category
from .forms import CategoryEditForm,ItemCreateForm,VariationForm
from orders.models import Order,OrderProduct,Payment,Coupons
from .forms import OrderForm,DiscountCouponForm
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate
from django.utils import timezone
import datetime
from django.core.paginator import Paginator


# Create your views here.
a=Account.objects.filter(is_superadmin=True)


#admin tabs
def admin_tab(request):
    customer_count = Account.objects.filter(is_superadmin=False).count()
    item_count = Product.objects.all().count()
    product = Product.objects.all()
    order = OrderProduct.objects.all()
    order_count =OrderProduct.objects.all().count()
    context = {
        'customer_count':customer_count,
        'item_count':item_count,
        'product':product,
        'order':order,
        'order_count':order_count
    }
    return render(request, 'admins/tables.html',context)

#manage user


@user_passes_test(lambda u: u in a, login_url='admin_login')
def manage_user(request):
    if 'q' in request.GET:
        q = request.GET['q']
        if q:
            users = Account.objects.order_by('-id').filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) |  Q(email__icontains=q) )
            for single_product in users:
                product1=[]
            for single_product in users:
                product1.append({
                    "first_name":single_product.first_name,
                    "last_name" :single_product.last_name,
                    "username"  :single_product.username,
                    "email"     :single_product.email,
                    "phone_number":single_product.phone_number,
                    "date_joined":single_product.date_joined,
                    "last_login":single_product.last_login,
                    "is_active":single_product.is_active,

                }) 
            # users_count = users.count()
            if not users.exists():
                messages.error(request, 'No Matching Datas')
                return render(request,'admins/manage_user.html')
        else:           
            return redirect('manage_user')
    else:
        users = Account.objects.filter(is_superadmin=False).order_by('-id')
        for single_product in users:
                product1=[]
        for single_product in users:
            product1.append({
                "id"        :single_product.id,
                "first_name":single_product.first_name,
                "last_name" :single_product.last_name,
                "username"  :single_product.username,
                "email"     :single_product.email,
                "phone_number":single_product.phone_number,
                "date_joined":single_product.date_joined,
                "last_login":single_product.last_login,
                "is_active":single_product.is_active,
                })

        paginator = Paginator(product1, 10)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
    context = {
        'users' : paged_products,
    }
    return render(request, 'admins/manage_user.html',context)

#end manage_user

#blockuser

@user_passes_test(lambda u: u in a, login_url='admin_login')
def block_user(request,id):
    account = Account.objects.get(id=id)

    if account.is_active:
        account.is_active = False
        account.save()
    else:
        account.is_active = True
        account.save()
    return redirect('manage_user')

#blockuser end

#manage category

@user_passes_test(lambda u: u in a, login_url='admin_login')
def manage_category(request):
    if 'q' in request.GET:
        q = request.GET['q']
        if q:
            category = Category.objects.order_by('-id').filter(Q(title__icontains=q) )   
            # users_count = users.count()
            if not category.exists():
                messages.error(request, 'No Matching Datas Found')
                return render(request,'admins/categories.html')
        else:           
            return redirect('manage_category')
    else:
        category = Category.objects.all()
   
    context = {
        'category' : category,
    }
    return render(request, 'admins/categories.html',context)

#end manage category

#delete_category

@user_passes_test(lambda u: u in a, login_url='admin_login')
def delete_category(request,id):
    category = Category.objects.get(id=id)
    category.delete()
    return redirect('manage_category')

#end delete_category

#edit category
@user_passes_test(lambda u: u in a, login_url='admin_login')
def edit_category(request,id):
    category = Category.objects.get(id=id)
    form = CategoryEditForm(instance=category)
    try:
        if request.method == 'POST':
            form=CategoryEditForm(request.POST,instance=category)
            if form.is_valid():
                form.save()           
                return redirect('manage_category')
    except:
        messages.error(request, "Slug already exists.")
        print("slug exists")
        return redirect('edit_category')

    context={
        'form':form
        }    
    return render (request,'admins/edit_category.html',context)

#end edit category

#add_category

@user_passes_test(lambda u: u in a, login_url='admin_login')
def add_category(request):
    try:
        if request.method == 'POST':
            title = request.POST['title']
            slug = request.POST['slug']
            category = Category.objects.create(title=title, slug=slug)
            category.save()
            return redirect('manage_category')
        return render(request, 'admins/add_category.html')
    except:
        messages.error(request, "Slug already exists.")
        return redirect('add_category')

#end add category

#manage product
@user_passes_test(lambda u: u in a, login_url='admin_login')
def manage_product(request):
    if 'q' in request.GET:
        q = request.GET['q']
        if q:
            product = Product.objects.order_by('-id').filter(Q(category__title__icontains=q) | Q(subcategory__name__icontains=q) |Q(gender__icontains=q) | Q(brand__brand_name__icontains=q) |  Q(name__icontains=q))   
            for single_product in product:
                product1=[]
        for single_product in product:
            
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
        if not product.exists():
            messages.error(request, 'No Matching Datas Found')
            return render(request,'admins/product.html')
        else:           
            return redirect('manage_product')
    else:
        product = Product.objects.all().order_by('-id')
        for single_product in product:
                product1=[]
        for single_product in product:
            
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

    context = {
        'product' : paged_products,
    }
    return render(request, 'admins/product.html',context)


#end manage product

#add_product

@user_passes_test(lambda u: u in a, login_url='admin_login')
def add_product(request):
    form = ItemCreateForm
    try:
        if request.method == 'POST':
            form = ItemCreateForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('manage_product')
           
        return render(request, 'admins/add_product.html',{'form':form})
    except:
        messages.error(request, "Slug already exists.")
        return redirect('manage_product')

#end add_product

#delete_product
@user_passes_test(lambda u: u in a, login_url='admin_login')
def delete_product(request,id):
    item = Product.objects.get(id=id)
    item.delete()
    return redirect('manage_product')

#end delete product

#edit product

@user_passes_test(lambda u: u in a, login_url='admin_login')

def edit_product(request,id):
    if request.user.is_authenticated:
        item = Product.objects.get(id=id)
        form = ItemCreateForm(instance=item)
        try:
            if request.method == 'POST':
                form=ItemCreateForm(request.POST,request.FILES, instance=item)
                if form.is_valid():
                    form.save()           
                    return redirect('manage_product')
        except:
            messages.error(request, "Slug already exists.")
            return redirect('edit_product')

        context={
            'form':form
            }    
        return render (request,'admins/add_product.html',context)


#end edit product
#variation management
@user_passes_test(lambda u: u in a, login_url='admin_login')
def manage_variation(request):
    if 'q' in request.GET:
        q = request.GET['q']
        if q:
            variation = Variation.objects.order_by('-id').filter(Q(product__name__icontains=q) | Q(variation_category__icontains=q) |Q(variation_value__icontains=q) )   
            # users_count = users.count()
            if not variation.exists():
                messages.error(request, 'No Matching Datas Found')
                return render(request,'admins/variation.html')
        else:           
            return redirect('manage_variation')
    else:   
        variation = Variation.objects.all().order_by('-product')

    context = {

        'variation' : variation,
    }
    return render(request, 'admins/variation.html',context)

@user_passes_test(lambda u: u in a, login_url='admin_login')
def add_variation(request):
    form = VariationForm

    if request.method == 'POST':
        form = VariationForm(request.POST, request.FILES)
        if form.is_valid():            
            form.save()
            return redirect('manage_variation')
        
    return render(request, 'admins/add_variation.html',{'form':form})

@user_passes_test(lambda u: u in a, login_url='admin_login')
def edit_variation(request,id):
    variation = Variation.objects.get(id=id)
    form = VariationForm(instance=variation)
  
    if request.method == 'POST':
        form=VariationForm(request.POST,instance=variation)
        if form.is_valid():
            form.save()           
            return redirect('manage_variation')
   
    context={
        'form':form
        }    
    return render (request,'admins/add_variation.html',context)

@user_passes_test(lambda u: u in a, login_url='admin_login')
def delete_variation(request,id):
    variation = Variation.objects.get(id=id)
    variation.delete()
    return redirect('manage_variation')


#end variation management

@never_cache
def admin_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
     
        user = auth.authenticate(email=email, password=password)
        
        if user is not None:
         
            if user.is_superadmin:
                auth.login(request,user)
                return redirect('admin_tab')          
         
            auth.login(request, user)       


        else:
            messages.error(request,'Invalid login Credentials!!')
            return redirect('admin_login')
   
    return render (request, 'admins/admin_login.html')

@user_passes_test(lambda u: u in a, login_url='admin_login')
def admin_logout(request):
    auth.logout(request)
    messages.success(request,'You were logged out')
    return redirect('admin_login')




#manage order by admin
@user_passes_test(lambda u: u in a, login_url='admin_login')
def manage_order(request):
    if 'q' in request.GET:
        q = request.GET['q']
        if q:
            order = Order.objects.order_by('-id').filter(Q(user__first_name__icontains=q) | Q(order_number__icontains=q))  
            order_product = OrderProduct.objects.all()
            # users_count = users.count()
            if not order.exists():
             
                return render(request,'admins/order.html')
        else:           
            return redirect('manage_order')
    else:
        order = Order.objects.all().order_by('-id')
        order_product = OrderProduct.objects.all()
    context = {
        'order' : order,
        'order_product' :  order_product,
    }
    return render(request, 'admins/order.html',context)



@user_passes_test(lambda u: u in a, login_url='admin_login')
def edit_order(request,id):
    order = Order.objects.get(id=id)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        form=OrderForm(request.POST,instance=order)
        
        if form.is_valid():
            form.save()                  
            return redirect('manage_order')

    context={
        'form':form, 
        'order':order      
        }    
    return render (request,'admins/edit_order.html',context)

# Discount coupons

@user_passes_test(lambda u: u in a, login_url='admin_login')
def manage_discount(request):
    if 'q' in request.GET:
        q = request.GET['q']
        if q:
            coupon = Coupons.objects.order_by('-id').filter(Q(coupon_code__icontains=q)  )   
            # users_count = users.count()
            if not coupon.exists():
                messages.error(request, 'No Matching Datas Found')
                return render(request,'admins/coupon.html')
        else:           
            return redirect('manage_discount')
    else:
        coupon = Coupons.objects.all().order_by('-id')

    context = {
        'coupon' : coupon,
    }
    return render(request, 'admins/coupon.html',context)

def add_discount(request):
    form = DiscountCouponForm
   
    if request.method == 'POST':
        form = DiscountCouponForm(request.POST)
        if form.is_valid():
            
            form.save()
            return redirect('manage_discount')
        
    return render(request, 'admins/add_discount.html',{'form':form})

def delete_discount(request,id):
    discount = Coupons.objects.get(id=id)
    discount.delete()
    return redirect('manage_discount')

@user_passes_test(lambda u: u in a, login_url='admin_login')
def edit_discount(request,id):
    discount = Coupons.objects.get(id=id)
    form = DiscountCouponForm(instance=discount)

    if request.method == 'POST':
        form=DiscountCouponForm(request.POST,instance=discount)
        if form.is_valid():
            form.save()           
            return redirect('manage_discount')


    context={
        'form':form
        }    
    return render (request,'admins/add_discount.html',context)
    # sales report

def sales_report(request):
    customer_count = Account.objects.filter(is_superadmin=False).count()
    item_count = Product.objects.all().count()
    product = Product.objects.all()
    order = OrderProduct.objects.all()
    order_count =OrderProduct.objects.all().count()
    ymax = timezone.now()
    ymin = (timezone.now() - datetime.timedelta(days=365))
    yearly = OrderProduct.objects.filter(created_at__lte=ymax, created_at__gte=ymin)
    mmax = timezone.now()
    mmin = (timezone.now() - datetime.timedelta(days=30))
    monthly = OrderProduct.objects.filter(created_at__lte=mmax, created_at__gte=mmin)
    ymax = timezone.now()
    ymin = (timezone.now() - datetime.timedelta(days=7))
    weekly = OrderProduct.objects.filter(created_at__lte=ymax, created_at__gte=ymin)
    month_sale = ["","","","","","","",""]
    subm = timezone.now()


    week_number = 4

    for i in range(4):
        k = 0
        for i in monthly:
            if i.created_at <= subm and i.created_at >= (subm - datetime.timedelta(days=7)):
                k += 1

        month_sale.append({'name': 'week' + str(week_number), 'value': k})
        week_number -= 1
        subm = subm - datetime.timedelta(days=7)

    subw = timezone.now()
    n=7
    week_sale=["","","","",""]
    for i in range(7):
        k = 0
        for i in weekly:
            if i.created_at <= subw and i.created_at>=(subw - datetime.timedelta(days=1)):
                k += 1
        week_sale.append({'name':'day'+str(n), 'value':k})
        n -= 1
        subw = subw - datetime.timedelta(days=1)

    monthly_sales = list(reversed(month_sale))

    suby=timezone.now()
    months=11
    year_sale=[]
    months_available=['january',"February","March","April","May","June","July","August","September","October","November","December"]
    for j in range(12):
        l=0
        for j in yearly:
            if j.created_at <=suby and j.created_at >=(suby - datetime.timedelta(days=30)):
                l +=1
        year_sale.append({"name" : months_available[months],'value':l})
        suby = suby- datetime.timedelta(days=30)
        months -= 1
    yearly_sale = list(reversed(year_sale))
    
    weekly_sales = list(reversed(week_sale))
    context={
      'monthly': monthly, 
    'yearly': yearly, 
    'monthly_sales': monthly_sales,
     'weekly_sales': weekly_sales,
     'customer_count':customer_count,
        'item_count':item_count,
        'product':product,
        'order':order,
        'order_count':order_count,
        # 'packed':zip(weekly_sales,monthly_sales,yearly_sale)
     }

    return render(request, 'admins/salesreport.html',context)
