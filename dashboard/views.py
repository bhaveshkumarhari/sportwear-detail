from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View

from django.core.exceptions import ObjectDoesNotExist

from .forms import CreateUserForm, ItemForm, ProductForm, ShippingAddressForm, BillingAddressForm, UserInfoForm, AdminForm

from django.contrib import messages

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.models import Group

from core.models import Item, Address, Order, Payment

from django.contrib.auth.models import User

from django.contrib.auth.mixins import LoginRequiredMixin


@login_required(login_url='dashboard:dashboard-login')
# @allowed_users(allowed_roles=['admin'])
@admin_only
def HomeView(request):
    orders = Order.objects.all() # Get all the orders
    total_orders = orders.filter(ordered=True).count() # Count total successful orders

    items = Item.objects.all() # Get all the items
    total_items = items.count() # Count total items

    users = User.objects.all() # Get all the users

    total_customers = User.objects.filter(groups__name='customer').count()

    # Get revenue by totalling all payment amounts
    payments = Payment.objects.all()
    revenue = 0
    for amounts in payments:
        revenue += amounts.amount

    # Filter all the orders which are successfully completed
    order_qs = Order.objects.filter(ordered=True).order_by('-ordered_date')

    ordered = Order.objects.filter(ordered=True, refund_granted=False, refund_requested=False, received=False, being_delivered=False)
    for setorder in ordered:
        setorder.status = "Ordered"
        setorder.label = "danger"
        setorder.save()

    refund_granted = Order.objects.filter(ordered=True, refund_granted=True)
    for setorder in refund_granted:
        setorder.status = "Refund Granted"
        setorder.label = "primary"
        setorder.save()

    refund_requested = Order.objects.filter(ordered=True, refund_requested=True)
    for setorder in refund_requested:
        setorder.status = "Refund Requested"
        setorder.label = "warning"
        setorder.save()

    received = Order.objects.filter(ordered=True, received=True)
    for setorder in received:
        setorder.status = "Delivered"
        setorder.label = "success"
        setorder.save()
    
    being_delivered = Order.objects.filter(ordered=True, being_delivered=True)
    for setorder in being_delivered:
        setorder.status = "Being Delivered"
        setorder.label = "inverse"
        setorder.save()

    context = {'total_orders':total_orders, 'total_items':total_items, 'total_customers':total_customers, 'revenue':revenue,
                'order_qs':order_qs}

    return render(request, 'dashboard.html', context)

def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

@login_required(login_url='dashboard:dashboard-login')
@admin_only
def customerProfile(request, user):

    user = User.objects.get(username=user)

    orders = Order.objects.filter(user=user, ordered = True)

    shippingform = ShippingAddressForm()

    billingform = BillingAddressForm()

    customer = user.customerprofile

    userform = UserInfoForm(instance=customer)
    
    # userform = UserInfoForm(request.POST or None, instance=user)


    if request.method == 'POST':
        userform = UserInfoForm(request.POST or None, request.FILES, instance=customer)
        if userform.is_valid():
            first_name = userform.cleaned_data.get('first_name')
            last_name = userform.cleaned_data.get('last_name')
            email = userform.cleaned_data.get('email')
            
            if is_valid_form([first_name, last_name, email]):
                userform.save()
                messages.success(request, "User information was changed successfully.")
                return redirect('dashboard:customer-profile', user=user)

    try:
        shipping_address = Address.objects.get(user=user, address_type='S', default=True)
    except ObjectDoesNotExist:
        shipping_address = False

    try:
        billing_address = Address.objects.get(user=user, address_type='B', default=True)
    except ObjectDoesNotExist:
        billing_address = False

    context = {'user':user, 'orders': orders, 'shipping_address':shipping_address, 'billing_address':billing_address, 'userform':userform, 'shippingform':shippingform, 'billingform':billingform}

    return render(request, 'dashboard_user_profile.html', context)


def shippingAddress(request, user):

    user = User.objects.get(username=user)

    if request.method == 'POST':
        
        form = ShippingAddressForm(request.POST or None)

        if form.is_valid():
            shipping_address = form.cleaned_data.get('shipping_address')
            shipping_address2 = form.cleaned_data.get('shipping_address2')
            shipping_country = form.cleaned_data.get('shipping_country')
            shipping_zip = form.cleaned_data.get('shipping_zip')
            shipping_state = form.cleaned_data.get('shipping_state')
            
            if is_valid_form([shipping_address, shipping_country, shipping_zip, shipping_state]):
                try:
                    old_shipping_address = Address.objects.get(user=user, address_type = 'S')
                    old_shipping_address.delete()
                except ObjectDoesNotExist:
                    pass
                shipping_address = Address(
                        user = user,
                        street_address = shipping_address,
                        apartment_address = shipping_address2,
                        country = shipping_country,
                        zip = shipping_zip,
                        state = shipping_state,
                        address_type = 'S',
                        default = True
                    )
                shipping_address.save()

                #---------- IF SAME BILLING ADDRESS CHECKED --------------

                same_billing_address = form.cleaned_data.get('same_billing_address')

                if same_billing_address:
                    try:
                        old_billing_address = Address.objects.get(user=user, address_type = 'B')
                        old_billing_address.delete()
                    except ObjectDoesNotExist:
                        pass
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    messages.success(request, "Billing address was changed successfully.")
                #-----------------------------------------------------------
                messages.success(request, "Shipping address was changed successfully.")
                return redirect('dashboard:customer-profile', user=user)


def billingAddress(request, user):

    user = User.objects.get(username=user)

    if request.method == 'POST':
        
        form = BillingAddressForm(request.POST or None)

        if form.is_valid():
            billing_address = form.cleaned_data.get('billing_address')
            billing_address2 = form.cleaned_data.get('billing_address2')
            billing_country = form.cleaned_data.get('billing_country')
            billing_zip = form.cleaned_data.get('billing_zip')
            billing_state = form.cleaned_data.get('billing_state')
            
            if is_valid_form([billing_address, billing_country, billing_zip, billing_state]):
                try:
                    old_billing_address = Address.objects.get(user=user, address_type = 'B')
                    old_billing_address.delete()
                except ObjectDoesNotExist:
                    pass

                billing_address = Address(
                        user = user,
                        street_address = billing_address,
                        apartment_address = billing_address2,
                        country = billing_country,
                        zip = billing_zip,
                        state = billing_state,
                        address_type = 'B',
                        default = True
                    )
                billing_address.save()

                #-----IF SAME SHIPPING ADDRESS CHECKED ----------------------

                same_shipping_address = form.cleaned_data.get('same_shipping_address')

                if same_shipping_address:
                    try:
                        old_shipping_address = Address.objects.get(user=user, address_type = 'S')
                        old_shipping_address.delete()
                    except ObjectDoesNotExist:
                        pass
                    shipping_address = billing_address
                    shipping_address.pk = None
                    shipping_address.save()
                    shipping_address.address_type = 'S'
                    shipping_address.save()
                    messages.success(request, "Shipping address was changed successfully.")
                
                #-------------------------------------------------------------
                messages.success(request, "Billing address was changed successfully.")
                return redirect('dashboard:customer-profile', user=user)


@login_required(login_url='dashboard:dashboard-login')
@admin_only
def productList(request):
    items = Item.objects.all()
    context = {'items':items}
    return render(request, 'dashboard_product_list.html', context)

@login_required(login_url='dashboard:dashboard-login')
@admin_only
def customerList(request):
    users = User.objects.filter(groups__name='customer')
    context = {'users':users}
    return render(request, 'customer_list.html', context)

@login_required(login_url='dashboard:dashboard-login')
@admin_only
def orderList(request):
    orders = Order.objects.all() # Get all the orders
    total_orders = orders.filter(ordered=True).count() # Count total successful orders

    items = Item.objects.all() # Get all the items
    total_items = items.count() # Count total items

    users = User.objects.all() # Get all the users
    total_users = users.count() - 1 # Count total users

    # Get revenue by totalling all payment amounts
    payments = Payment.objects.all()
    revenue = 0
    for amounts in payments:
        revenue += amounts.amount

    # Filter all the orders which are successfully completed
    order_qs = Order.objects.filter(ordered=True).order_by('-ordered_date')

    ordered = Order.objects.filter(ordered=True, refund_granted=False, refund_requested=False, received=False, being_delivered=False)
    for setorder in ordered:
        setorder.status = "Ordered"
        setorder.label = "danger"
        setorder.save()

    refund_granted = Order.objects.filter(ordered=True, refund_granted=True)
    for setorder in refund_granted:
        setorder.status = "Refund Granted"
        setorder.label = "primary"
        setorder.save()

    refund_requested = Order.objects.filter(ordered=True, refund_requested=True)
    for setorder in refund_requested:
        setorder.status = "Refund Requested"
        setorder.label = "warning"
        setorder.save()

    received = Order.objects.filter(ordered=True, received=True)
    for setorder in received:
        setorder.status = "Delivered"
        setorder.label = "success"
        setorder.save()
    
    being_delivered = Order.objects.filter(ordered=True, being_delivered=True)
    for setorder in being_delivered:
        setorder.status = "Being Delivered"
        setorder.label = "inverse"
        setorder.save()

    context = {'total_orders':total_orders, 'total_items':total_items, 'total_users':total_users, 'revenue':revenue,
                'order_qs':order_qs}
                
    return render(request, 'dashboard_orders.html', context)

class createProduct(View):

    def get(self, *args, **kwargs):
        form = ProductForm()
        context = {'form':form}
        return render(self.request, 'create_product.html', context)
    def post(self, *args, **kwargs):
        form = ProductForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            category = form.cleaned_data.get('category')
            description = form.cleaned_data.get('description')
            size = form.cleaned_data.get('size')
            slug = form.cleaned_data.get('slug')
            quantity = form.cleaned_data.get('quantity')
            price = form.cleaned_data.get('price')
            discount_price = form.cleaned_data.get('discount_price')
            front_image = form.cleaned_data.get('front_image')
            back_image = form.cleaned_data.get('back_image')
            side_image = form.cleaned_data.get('side_image')
            new = form.cleaned_data.get('new')

            items = Item(
                title = title,
                category = category,
                description = description,
                size = size,
                slug = slug,
                quantity = quantity,
                price = price,
                discount_price = discount_price,
                front_image = front_image,
                back_image = back_image,
                side_image = side_image,
                new = new
            )
            items.save() 
            messages.success(self.request,'Successfully added product to your inventory')
            return redirect('dashboard:dashboard-product-list')
        messages.warning(self.request,'Please enter valid information')
        return redirect('dashboard:create-product')

@login_required(login_url='dashboard:dashboard-login')
@admin_only
def update_product(request, slug):
    try:
        product = Item.objects.get(slug=slug)
    except Item.DoesNotExist:
        return redirect('dashboard:dashboard-product-list')

    form = ItemForm(request.POST or None, instance = product)

    if form.is_valid():
        form.save()
        messages.success(request,'Successfully updated product of inventory')
        return redirect('dashboard:dashboard-product-list')

    context = {'form':form, 'product':product}
    return render(request, 'update_product.html', context)

@login_required(login_url='dashboard:dashboard-login')
@admin_only
def delete_product(request, slug):
    try:
        product = Item.objects.get(slug=slug)
    except Item.DoesNotExist:
        return redirect('dashboard:dashboard-product-list')

    product.delete()
    messages.warning(request,'Successfully deleted product from inventory')
    return redirect('dashboard:dashboard-product-list')


@unauthenticated_user
def registerPage(request):
    # if request.user.is_authenticated:
    #     return redirect('core:home')
    # else:
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            # For every user registration, add user to customer group
            group = Group.objects.get(name='admin')
            user.groups.add(group)

            messages.success(request,'Account was created for ' + username)
            return redirect('dashboard:dashboard-login')
    context = {'form':form}
    return render(request, 'dashboard_register.html', context)

@unauthenticated_user
def loginPage(request):
    # if request.user.is_authenticated:
    #     return redirect('core:home')
    # else:
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard:dashboard-home')
        else:
            messages.warning(request, 'Username OR password is incorrect')

    context = {}
    return render(request, 'dashboard_login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('dashboard:dashboard-login')


def adminAccount(request):
    admin = request.user.customerprofile
    form = AdminForm(instance=admin)

    if request.method == 'POST':
        form = AdminForm(request.POST, request.FILES, instance=admin)
        if form.is_valid():
            form.save()

    context = {'form': form}

    return render(request, 'admin_account.html', context)

class userPage(View):

    def get(self, *args, **kwargs):

        return render(self.request, 'user_page.html')