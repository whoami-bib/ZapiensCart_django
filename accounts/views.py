
from django.shortcuts import render,redirect



from .models import Account
from .forms import RegistrationForm,VerifyForm, VerifyotpForm, otploginForm
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
from carts.models import Cart


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
                except:
                    pass
                auth.login(request,user)
                messages.success(request,'you are now logged in')
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
    return render(request,'accounts/dashboard.html')
    
