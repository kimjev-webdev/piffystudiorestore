from django import forms
from .models import Product, ProductImage

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title', 'category', 'product_type',
            'price', 'description', 'stock', 'featured'
        ]


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
