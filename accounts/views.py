
from multiprocessing import context
from django.shortcuts import render,redirect,get_object_or_404

from orders.models import OrderProduct

from .models import Account, UserProfile
from .forms import RegistrationForm,VerifyForm, VerifyotpForm, otploginForm,UserForm,UserProfileForm
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
#email varification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.views.decorators.cache import never_cache
#phone number verification
from . import verify
from .verify import send,check
from carts.views import _cart_id
from carts.models import Cart,CartItem
from orders.models import Order

import requests



# Create your views here.
@never_cache
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            
             
            if Account.objects.filter(phone_number=phone_number).exists():
                messages.error(request,'Phone number already exists')
            
            
            else:                
                user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
                user.phone_number = phone_number
                user.save()
                request.session['phone_number']=phone_number
                send(form.cleaned_data.get('phone_number'))
                return redirect('verify')          
    else:       
        form = RegistrationForm()
    context = {
        'form' : form
    }
    return render(request, 'accounts/register.html',context)

def verifyotp(request):
    if request.method == 'POST':
        
        form = VerifyotpForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            phone_number= request.session['phone_number']
            if check(phone_number, code):
                user=Account.objects.get(phone_number=phone_number)

                if user is not None:
                    auth.login(request,user)
                    messages.success(request,'you are now logged in')
                    return redirect('home')
                else:
                    messages.error(request,'Invalid credentials')
                    return redirect('login')
    else:
        form = VerifyForm()
    return render(request, 'accounts/verify.html', {'form': form})



def verify_code(request):
    if request.method == 'POST':
        
        form = VerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            phone_number= request.session['phone_number']
            if check(phone_number, code):
                user=Account.objects.get(phone_number=phone_number)
                user.is_active = True
                user.save()
                return redirect('login')
    else:
        form = VerifyForm()
    return render(request, 'accounts/verify.html', {'form': form})

# def register(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             first_name = form.cleaned_data['first_name']
#             last_name = form.cleaned_data['last_name']
#             phone_number = form.cleaned_data['phone_number']
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password']
#             username=email.split("@")[0]
            
#             user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
#             user.phone_number =phone_number
#             user.save()
#             request.session['phone_number']=phone_number
            
#             #user Authentication

#             current_site=get_current_site(request)
#             mail_subject='Pleases Activate your Account'
#             message = render_to_string('accounts/account_verification_email.html',{
#                 'user'  : user,
#                 'domain': current_site,
#                 'uid'   : (user.pk),
#                 'token' : default_token_generator.make_token(user),
#             })
#             to_email=email
#             send_email=EmailMessage(mail_subject,message,to=[to_email])
#             send_email.send()
#             # messages.success(request,"thank u for registering with us we have sent an email to your account please verify it")
#             return redirect('/accounts/login/?command=verification&email='+email)

#     else:
#         form=RegistrationForm()
#     context={
#         'form':form
#     }
#     return render(request,'accounts/register.html',context)
@never_cache
def login(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method =='POST':
            email = request.POST['email']
            password = request.POST['password']

            user = auth.authenticate(email=email,password=password)

            if user is not None:
                try:
                    cart=Cart.objects.get(cart_id=_cart_id(request))
                    is_cart_item_exists=CartItem.objects.filter(cart=cart).exists()
                    if is_cart_item_exists:
                        cart_item = CartItem.objects.filter(cart=cart)
                        product_variation=[]
                        for item in cart_item:
                            variation=item.variations.all()
                            product_variation.append(list(variation))

                        cart_item=CartItem.objects.filter(user=user)
                        ex_var_list=[]
                        id=[]
                        for item in cart_item:
                            existing_variation = item.variations.all()
                            ex_var_list.append(list(existing_variation))
                            id.append(item.id)
                        
                        for pr in product_variation:
                            if pr in ex_var_list:
                                index=ex_var_list.index(pr)
                                item_id=id[index]
                                item=CartItem.objects.get(id=item_id)
                                item.quantity +=1
                                item.user=user
                                item.save()
                            else:
                                cart_item=CartItem.objects.filter(cart=cart)
                                for item in cart_item:
                                    item.user=user
                                    item.save()
                except:
                    pass
                auth.login(request,user)
                messages.success(request,'you are now logged in')
                url = request.META.get('HTTP_REFERER')
                try:
                    query= requests.utils.urlparse(url).query
                    params= dict(x.split('=') for x in query.split('&'))
                    if 'next' in params:
                        nextPage=params['next']
                        return redirect(nextPage)
                    
                except:
                    return redirect('home')
            else:
                messages.error(request,'Invalid credentials')
                return redirect('login')
    return render(request,'accounts/login.html')

def otplogin(request):
    if request.method =='POST':
        form = otploginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']

            if Account.objects.filter(phone_number=phone_number).exists():

                user = Account.objects.get(phone_number=phone_number)
                request.session['phone_number']=phone_number
                send(form.cleaned_data.get('phone_number'))
                return redirect('verifyotp') 

            else:
                messages.error(request,"Account Doesnot exist!")
        else:
            messages.error(request,"Enter a Valid Phone Number!")
                

        # if user is not None:
        #         auth.login(request,user)
        #         messages.success(request,'you are now logged in')
        #         return redirect('home')
        # else:
        #     messages.error(request,'Invalid credentials')
        #     return redirect('login')
       
        
    return render(request,'accounts/otp_login.html')
    

@login_required(login_url = 'login')
@never_cache
def logout(request):
    auth.logout(request)
    messages.success(request,'you are logged out')
    return redirect('login')

def activate(request,uidb64,token):
    
    try:
        uid     = uidb64
        user    = Account._default_manager.get(pk=uid)

    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request,"congratulations your account has been varified")
        return redirect('login')
    else:
        messages.error(request,"Invalid Activation link!")
        return redirect("register")

@login_required(login_url='login')
def dashboard(request):
    orders=Order.objects.order_by("-created_at").filter(user_id=request.user.id,is_ordered=True)
    orders_count=orders.count
    userprofile = UserProfile.objects.get(user_id=request.user.id)
    context={
        'orders_count':orders_count,
        'userprofile' : userprofile,
    }
    return render(request,'accounts/dashboard.html',context)
    
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile,user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST,instance=request.user)
        profile_form = UserProfileForm(request.POST,request.FILES,instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            print(user_form)
            profile_form.save()
            messages.success(request,'Your profile Updated.')
            return redirect('edit_profile')
    else:
        user_form=UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form' : user_form,
        'profile_form' : profile_form,
        "userprofile"   : userprofile,
    }
    return render(request,'accounts/edit_profile.html',context)
# Change Password View
@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request,"Password Changed Successfully")
                return redirect ('change_password')
            else:
                messages.error(request,"Wrong Password")
                return redirect ('change_password')
        else:
            messages.error(request,"Passwords donot Match")
            return redirect ('change_password')
    return render(request,'accounts/change_password.html')
login_required(login_url='login')
def order_detail(request,order_id):
    order_detail = OrderProduct.objects.filter(order__order_number = order_id)
    order = Order.objects.get(order_number = order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context = {
        'order_detail': order_detail,
        'order' : order,
        'subtotal':subtotal,
    }
    # __order_number means this order's order number
    return render(request,'accounts/order_detail.html',context)
