
import datetime
from multiprocessing import context
from django.shortcuts import render,redirect
from carts.models import CartItem
from store.models import Product
from accounts.models import UserProfile
from .models import Order, OrderProduct, Payment, Coupons
from .forms import OrderForm
from category.models import Category
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import razorpay
import json
import urllib
from django.views.decorators.csrf import csrf_exempt
from django.utils.datastructures import MultiValueDictKeyError

# Create your views here.
def payment(request,total=0,quantity=0):
    category = Category.objects.all()

    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    if cart_items :
        grand_total=0
        tax=0

    for cart_item in cart_items:
        total       +=  (cart_item.product.price*cart_item.quantity)
        quantity    +=  cart_item.quantity
    tax=(2 * total)/100
    grand_total=total + tax

        
    # creating razorpay client
    client =  razorpay.Client(auth=(settings.RAZORPAY_ID , settings.RAZORPAY_KEY ))
    
    
    #create order
    amount = int(request.session['grand_total'])*100
    response_payment = client.order.create({'amount' : amount, 'currency' : 'INR','payment_capture' : 0})
    request.session['response_payment']= response_payment
    order_id = response_payment['id']
    payment_status = response_payment['status']

    if payment_status == 'created':       
        paym = Payment(user=current_user,amount_paid = amount, order_id = order_id)    
        paym.save() 
        paym.user=current_user
        
        paym.amount_paid = int(request.session['grand_total'])
        paym.order_id = order_id
        paym.save()
        user = Payment.objects.filter(order_id=order_id).values('user','order_id')
        paisa=int(request.session['grand_total'])*100
        return render(request,'orders/razor.html',
        context={'response_payment':response_payment,'user':request.user,
        'paym' : response_payment,
        'cart_items' : cart_items, 
        'tax' : tax,
        'grand_total':request.session['grand_total'],
        'total' : int(request.session['grand_total']),
        'paisa' :paisa
        })
    
    return render(request, 'orders/razor.html',context) 
@csrf_exempt
def payment_status(request):
    response = request.POST
    params_dict = {
        'razorpay_order_id' : response['razorpay_order_id'],
        'razorpay_payment_id' : response['razorpay_payment_id'],
        'razorpay_signature' : response['razorpay_signature'],
    }
    

    #create client instances
    client = razorpay.Client(auth=("rzp_test_Nf4iy5nJpLvtmt" , "Y2D6cZPsAz452WAVT8VpDTM1" ))

    try:
        status = client.utility.verify_payment_signature(params_dict)
        payment = Payment.objects.get(order_id=response['razorpay_order_id'])
        payment.payment_id = response['razorpay_payment_id']
        payment.paid = True
        payment.status ='Paid'
        payment.payment_method ="Razor pay"
        payment.save()
        order_number = request.session['order_number']      
        order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)
        order.is_ordered = True
        order.status = 'Confirmed'
        order.save()
        cart_items = CartItem.objects.filter(user = request.user)
        
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
      
        for x in cart_items:
        
            data = OrderProduct()
            data.order_id = order.id            
            data.user_id = request.user.id
            data.product_id = x.product_id
            data.quantity = x.quantity
            data.payment = payment          
            data.product_price = x.product.price
            data.ordered = True
         
            # if x.variations:                
            #     data.variation = var
            data.save()
           

            pr = x.product
            product = Product.objects.get(id=pr.id)
            product.stock -= x.quantity
            product.save()
           

        cart_items.delete()  
        context={
            'order_number' : order_number,
            'transID'      : payment.payment_id,
            'payment'      : payment,
            'order'        : order,
            'subtotal'     : int(request.session['grand_total']),
            'ordered_products':ordered_products

        }   

        return render(request, 'orders/order_complete.html' ,context)
    except:
        payment = Payment.objects.get(order_id=response['razorpay_order_id'])
        payment.payment_id = response['razorpay_payment_id']
        payment.paid = False
        payment.save()
        order_number = request.session['order_number']
        order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)
        order.is_ordered = False
        order.status = 'Failed'
        order.save()
        cart_items = CartItem.objects.filter(user = request.user)
    
        for x in cart_items:
        
            data = OrderProduct()
            data.order_id = order.id            
            data.user_id = request.user.id
            data.product_id = x.product_id
            data.quantity = x.quantity
            data.payement = payment          
            data.product_price = x.product.price
            data.ordered = False
         
            # if x.variations:                
            #     data.variation = var
            data.save()
        return render(request, 'order/payment_status.html', {'status':False,})

# razor pay ends here

def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = int(request.session['grand_total']),
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.status = 'Confirmed'
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()


        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
        

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order recieved email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)

def place_order(request,total=0,quantity=0):
    current_user    =   request.user
    

    cart_items      =   CartItem.objects.filter(user=current_user)
    cart_count      =   cart_items.count()
    if cart_count   <=  0:
        return redirect('store')

    
    for cart_item in cart_items:
        total       +=  ((cart_item.product.price-(cart_item.product.category.offer * cart_item.product.price)/100)*cart_item.quantity)
        quantity    +=  cart_item.quantity
    tax=(2 * total)/100
    grand_total=total + tax
    now = timezone.now()
    

    if request.method =='POST':
        try:
            address = request.POST['address']
        except MultiValueDictKeyError:
            messages.error(request, 'Please Select an Address!')
            return redirect('checkout')
        # coupon
        if 'coupon' in request.POST:
                code = request.POST['code']
                try:
                    coup = Coupons.objects.get(coupon_code=code,coupon_start__lt=now, coupon_end__gt=now, coupon_min__lte=int(grand_total) )
                except Coupons.DoesNotExist:
                    return redirect(place_order)

                s = grand_total - ((grand_total*coup.coupon_offer)/100)
                request.session['coupon_offer'] = coup.coupon_offer
                request.session['coupon_code'] = coup.coupon_code
                request.session['grand_total'] = s

                return redirect(place_order)
        add = request.POST['address']
        user = UserProfile.objects.get(id=add)
        data                =   Order(user=request.user,first_name=user.user.first_name,last_name=user.user.last_name,email=user.user.email,phone=user.user.phone_number,address_line_1=user.address_line_1,address_line_2=user.address_line_2,
        country=user.country,state=user.state,city=user.city,pincode=user.pincode,order_total=grand_total,tax=tax)
        data.save()
        
        yr      =       int(datetime.date.today().strftime('%Y'))
        dt      =       int(datetime.date.today().strftime('%d'))
        mt      =       int(datetime.date.today().strftime('%m'))
        d       =       datetime.date(yr,mt,dt)
        current_date        =   d.strftime('%Y%m%d')
        order_number        =   current_date  +str(data.id)
        data.order_number   =   order_number
        
        data.save()
        request.session['order_number'] = order_number
        order   =   Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
        context={
            'order':order,
            'cart_items':cart_items,
            'total':total,
            'tax':tax,
            'grand_total':request.session['grand_total']
        }
        return render(request,'orders/payments.html',context)
            
    else:
        return redirect('checkout')



def cod(request):
    
    category = Category.objects.all()
    current_user = request.user
    cart_item = CartItem.objects.filter(user=current_user)
    if cart_item :
        total=0
        quantity=0
        tax = 0
        grand_total = 0
        for item in cart_item:
            total += item.product.price * item.quantity
            quantity += item.quantity
        tax = (2*total)/100
        grand_total  = int(total + tax)*100
    if request.method == 'POST':
        messages.success(request, 'Your Order Placed Successfully!!')
        order_number = request.session['order_number']
        Order.objects.filter(user=request.user, is_ordered=False, order_number=order_number).update(is_ordered=True,status="Confirmed")
        order = Order.objects.get(user=request.user, order_number=order_number)
                
        cart_items = CartItem.objects.filter(user = request.user)
        for x in cart_items:
            data = OrderProduct()
            data.order_id = order.id          
            data.user_id = request.user.id
            data.product_id = x.product_id
            data.quantity = x.quantity                      
            data.product_price = x.product.price
            data.ordered = True
            order.status = 'Confirmed'
            data.save()


            pr = x.product
            product = Product.objects.get(id=pr.id)
            product.stock -= x.quantity
            product.save()

        CartItem.objects.filter(user=request.user).delete()
        return redirect('store')
    context ={
        
            'cart_items' : cart_item, 
            'tax' : tax,
            'grand_total':request.session['grand_total'],
            'total' : total,
            'category' : category,
        }
    

    return render(request, 'orders/cod.html',context)



@csrf_exempt
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': int(request.session['grand_total']),
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
login_required(login_url='login')
def my_orders(request):
    orders=Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    context={
        'orders':orders
    }
    return render(request,'accounts/my_orders.html',context)


def couponremove(request):
    request.session['coupon_offer'] = None
    request.session['coupon_code'] = None
    return redirect(place_order)
    