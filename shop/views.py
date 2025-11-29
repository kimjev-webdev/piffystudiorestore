from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'shop/product_list.html', {
        'products': products,
        'categories': categories
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'shop/product_detail.html', {
        'product': product
    })

from accounts.decorators import staff_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ProductImage
from .forms import ProductForm, ProductImageForm

@staff_required
def manage_products(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'shop/manage/products_list.html', {
        'products': products
    })

@staff_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        image_form = ProductImageForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save()

            if request.FILES.get('image'):
                ProductImage.objects.create(
                    product=product,
                    image=request.FILES['image']
                )

            return redirect('shop:manage_products')

    else:
        form = ProductForm()
        image_form = ProductImageForm()

    return render(request, 'shop/manage/product_form.html', {
        'form': form,
        'image_form': image_form,
    })

@staff_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)

        if form.is_valid():
            form.save()
            return redirect('shop:manage_products')

    else:
        form = ProductForm(instance=product)

    return render(request, 'shop/manage/product_form.html', {
        'form': form,
        'product': product
    })

@staff_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('shop:manage_products')


