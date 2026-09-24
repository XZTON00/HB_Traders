from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomerSignUpForm
from .models import BusinessDetail, Product


def index(request):
    products = Product.objects.filter(is_active=True)
    context = {
        'business': BusinessDetail.load(),
        'products': products,
        'product_count': products.count(),
    }
    return render(request, 'catalog/index.html', context)


def product_detail(request, number):
    product = get_object_or_404(Product, number=number, is_active=True)
    context = {
        'business': BusinessDetail.load(),
        'product': product,
        'previous_product': product.previous(),
        'next_product': product.next(),
    }
    return render(request, 'catalog/detail.html', context)


def register(request):
    if request.user.is_authenticated:
        return redirect('catalog:index')

    if request.method == 'POST':
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name or user.username} — your account is ready.")
            return redirect('catalog:index')
    else:
        form = CustomerSignUpForm()

    return render(request, 'registration/register.html', {
        'business': BusinessDetail.load(),
        'form': form,
    })
