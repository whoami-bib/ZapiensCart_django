from django import forms
from category.models import Category
from store.models import Product,Variation
from orders .models import Order






class CategoryEditForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name','slug','discription','cat_image',]
    def __init__(self, *args, **kwargs):
        super(CategoryEditForm, self).__init__(*args, **kwargs)
        self.fields['category_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['slug'].widget.attrs.update({'class': 'form-control'})
        self.fields['discription'].widget.attrs.update({'class': 'form-control'})
        self.fields['cat_image'].widget.attrs.update({'class': 'form-control'})

class ItemCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category','product_name', 'slug', 'descrbtion', 'price', 
         'stock', 'is_available', 'image', ]

    def __init__(self, *args, **kwargs):
        super(ItemCreateForm, self).__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        
        
        self.fields['product_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['slug'].widget.attrs.update({'class': 'form-control'})
        
        self.fields['descrbtion'].widget.attrs.update({'class': 'form-control'})
        self.fields['price'].widget.attrs.update({'class': 'form-control'})
        
        self.fields['stock'].widget.attrs.update({'class': 'form-control'})       
        
        self.fields['image'].widget.attrs.update({'class': 'form-control','id':'id_image1','name':'image', 'onchange':"changeImg(event)"})


class VariationForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(VariationForm, self).__init__(*args, **kwargs)
        self.fields['product'].widget.attrs.update({'class': 'form-control'})
        self.fields['variation_category'].widget.attrs.update({'class': 'form-control'})
        self.fields['variation_value'].widget.attrs.update({'class': 'form-control'})
       
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status',]

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.update({'class': 'form-control'})
   