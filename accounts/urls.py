
from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('otplogin/',views.otplogin,name='otplogin'),
    path('verify/', views.verify_code,name="verify"),
    path('verifyotp/',views.verifyotp,name="verifyotp"),
    


    path('activate/<uidb64>/<token>/',views.activate,name='activate'),
]