from django.urls import path
from . import views


urlpatterns = [
    path('admin_login/',views.admin_login,name='admin_login'),
    path('admin_logout/',views.admin_logout,name='admin_logout'),
    path('tables/',views.admin_tab,name='admin_tab'),
    path('manage_user/',views.manage_user,name='manage_user'),
    path('block_user/<int:id>/',views.block_user,name='block_user'),

    path('manage_category/',views.manage_category,name='manage_category'),
    path('delete_category/<int:id>/',views.delete_category,name='delete_category'),
    path('edit_category/<int:id>/',views.edit_category,name='edit_category'),
    path('add_category/',views.add_category,name='add_category'),

    path('manage_product/',views.manage_product,name='manage_product'),
    path('add_product/',views.add_product,name='add_product'),
    path('delete_product/<int:id>/',views.delete_product,name='delete_product'),
    path('edit_product/<int:id>/',views.edit_product,name='edit_product'),

    path('manage_variation/',views.manage_variation,name='manage_variation'),
    path('add_variation/',views.add_variation,name='add_variation'),
    path('edit_variation/<int:id>/',views.edit_variation,name='edit_variation'),
    path('delete_variation/<int:id>/',views.delete_variation,name='delete_variation'),

    path('manage_order/',views.manage_order,name='manage_order'),
    path('edit_order/<int:id>/',views.edit_order,name='edit_order'),
    
]