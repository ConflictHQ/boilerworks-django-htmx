from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.permissions import P

from .forms import ProductForm
from .models import Product


@login_required
def product_list(request):
    P.PRODUCT_VIEW.check(request.user)
    products = Product.objects.all()

    search = request.GET.get("search", "").strip()
    if search:
        products = products.filter(name__icontains=search)

    if request.headers.get("HX-Request"):
        return render(request, "products/partials/product_table.html", {"products": products})

    return render(request, "products/product_list.html", {"products": products, "search": search})


@login_required
def product_create(request):
    P.PRODUCT_ADD.check(request.user)

    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, f'Product "{product.name}" created.')
            return redirect("products:detail", slug=product.slug)
    else:
        form = ProductForm()

    return render(request, "products/product_form.html", {"form": form, "title": "New Product"})


@login_required
def product_detail(request, slug):
    P.PRODUCT_VIEW.check(request.user)
    product = get_object_or_404(Product, slug=slug, deleted_at__isnull=True)
    return render(request, "products/product_detail.html", {"product": product})


@login_required
def product_update(request, slug):
    P.PRODUCT_CHANGE.check(request.user)
    product = get_object_or_404(Product, slug=slug, deleted_at__isnull=True)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.updated_by = request.user
            product.save()
            messages.success(request, f'Product "{product.name}" updated.')
            return redirect("products:detail", slug=product.slug)
    else:
        form = ProductForm(instance=product)

    return render(request, "products/product_form.html", {"form": form, "product": product, "title": "Edit Product"})


@login_required
def product_delete(request, slug):
    P.PRODUCT_DELETE.check(request.user)
    product = get_object_or_404(Product, slug=slug, deleted_at__isnull=True)

    if request.method == "POST":
        product.soft_delete(user=request.user)
        messages.success(request, f'Product "{product.name}" deleted.')

        if request.headers.get("HX-Request"):
            from django.http import HttpResponse

            return HttpResponse(status=200, headers={"HX-Redirect": "/products/"})

        return redirect("products:list")

    return render(request, "products/product_confirm_delete.html", {"product": product})
