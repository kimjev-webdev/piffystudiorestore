from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Product, ProductImage, Category, ProductVariant, Cart, CartItem
from .forms import ProductForm, CategoryForm, VariantForm


# ===========================================================
# PUBLIC SHOP VIEWS
# ===========================================================

def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, "shop/product_list.html", {
        "products": products,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    images = product.images.all()
    variants = product.variants.all()

    return render(request, "shop/product_detail.html", {
        "product": product,
        "images": images,
        "variants": variants,
    })


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    variant_id = request.POST.get("variant_id")
    variant = None
    if variant_id:
        variant = ProductVariant.objects.filter(id=variant_id).first()

    cart, created = Cart.objects.get_or_create(user=request.user)

    CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=1
    )

    messages.success(request, f"{product.title} added to cart.")
    return redirect("shop:shop_index")


def success(request):
    return render(request, "shop/success.html")


def cancel(request):
    return render(request, "shop/cancel.html")

# ===========================================================
# CART SYSTEM (PUBLIC)
# ===========================================================

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()

    total = sum(item.total_price for item in items)

    return render(request, "shop/cart.html", {
        "cart": cart,
        "items": items,
        "total": total,
    })


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect("shop:cart")


@login_required
def update_cart_item(request, item_id):
    """
    Updates the quantity of a cart item via POST request.
    """
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == "POST":
        new_quantity = request.POST.get("quantity")
        try:
            new_quantity = int(new_quantity)
            if new_quantity > 0:
                item.quantity = new_quantity
                item.save()
                messages.success(request, "Cart updated.")
            else:
                item.delete()
                messages.info(request, "Item removed from cart.")
        except ValueError:
            messages.error(request, "Invalid quantity.")

    return redirect("shop:cart")


@login_required
def checkout(request):
    """
    Placeholder for Stripe Checkout session.
    You will replace this with stripe.checkout.Session later.
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()

    if not items:
        messages.error(request, "Your cart is empty.")
        return redirect("shop:cart")

    # Stripe integration goes here.
    return render(request, "shop/checkout.html", {
        "cart": cart,
        "items": items,
        "total": sum(i.total_price for i in items),
    })



# ===========================================================
# MANAGEMENT (ADMIN AREA)
# ===========================================================

@login_required
def manage_products(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, "shop/manage/manage_products.html", {
        "products": products
    })


@login_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, "Product created.")
            return redirect("shop:edit_product", pk=product.pk)
    else:
        form = ProductForm()

    return render(request, "shop/manage/add_product.html", {
        "form": form
    })


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated.")
        return redirect("shop:edit_product", pk=pk)

    form = ProductForm(instance=product)
    images = product.images.all()
    variants = product.variants.all()

    return render(request, "shop/manage/edit_product.html", {
        "product": product,
        "form": form,
        "images": images,
        "variants": variants,
    })


@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, "Product deleted.")
    return redirect("shop:manage_products")


@login_required
def bulk_delete(request):
    ids = request.POST.getlist("ids")
    Product.objects.filter(id__in=ids).delete()
    messages.success(request, "Products deleted.")
    return redirect("shop:manage_products")


@login_required
def duplicate_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.pk = None
    product.slug = product.slug + "-copy"
    product.save()
    messages.success(request, "Product duplicated.")
    return redirect("shop:edit_product", pk=product.pk)


# ===========================================================
# IMAGE MANAGEMENT
# ===========================================================

@login_required
def upload_product_image(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == "POST" and request.FILES.getlist("images"):
        for img in request.FILES.getlist("images"):
            ProductImage.objects.create(product=product, image=img)
        messages.success(request, "Images uploaded.")
    return redirect("shop:edit_product", pk=product_id)


@login_required
def delete_product_image(request, image_id):
    image = get_object_or_404(ProductImage, pk=image_id)
    product_id = image.product.id
    image.delete()
    messages.success(request, "Image deleted.")
    return redirect("shop:edit_product", pk=product_id)


@login_required
def update_image_order(request):
    if request.method == "POST":
        order = request.POST.getlist("order[]")

        for idx, image_id in enumerate(order):
            ProductImage.objects.filter(id=image_id).update(position=idx)

        return JsonResponse({"status": "success"})


# ===========================================================
# CATEGORY MANAGEMENT
# ===========================================================

@login_required
def manage_categories(request):
    categories = Category.objects.all()
    return render(request, "shop/manage/manage_categories.html", {"categories": categories})


@login_required
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added.")
            return redirect("shop:manage_categories")
    else:
        form = CategoryForm()

    return render(request, "shop/manage/add_category.html", {"form": form})


@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated.")
            return redirect("shop:manage_categories")
    else:
        form = CategoryForm(instance=category)

    return render(request, "shop/manage/edit_category.html", {
        "form": form,
        "category": category
    })


@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category deleted.")
    return redirect("shop:manage_categories")

# ===========================================================
# VARIANT MANAGEMENT
# ===========================================================

@login_required
def add_variant(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == "POST":
        form = VariantForm(request.POST)
        if form.is_valid():
            variant = form.save(commit=False)
            variant.product = product
            variant.save()
            messages.success(request, "Variant added.")
            return redirect("shop:edit_product", pk=product_id)
    else:
        form = VariantForm()

    return render(request, "shop/manage/add_variant.html", {
        "form": form,
        "product": product,
    })


@login_required
def edit_variant(request, variant_id):
    variant = get_object_or_404(ProductVariant, pk=variant_id)
    product = variant.product

    if request.method == "POST":
        form = VariantForm(request.POST, instance=variant)
        if form.is_valid():
            form.save()
            messages.success(request, "Variant updated.")
            return redirect("shop:edit_product", pk=product.id)
    else:
        form = VariantForm(instance=variant)

    return render(request, "shop/manage/edit_variant.html", {
        "form": form,
        "variant": variant,
        "product": product,
    })


@login_required
def delete_variant(request, variant_id):
    variant = get_object_or_404(ProductVariant, pk=variant_id)
    product_id = variant.product.id
    variant.delete()
    messages.success(request, "Variant deleted.")
    return redirect("shop:edit_product", pk=product_id)
