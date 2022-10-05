from django.contrib import admin

from wishlists.models import Wishlist, WishlistItem

# Register your models here.
class WishlistAdmin(admin.ModelAdmin):
    list_display=('wishlist_id','date_added')
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('product','is_active')
     
# Register your models here.
admin.site.register(Wishlist,WishlistAdmin)
admin.site.register(WishlistItem,WishlistItemAdmin)
