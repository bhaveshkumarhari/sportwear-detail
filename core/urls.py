from django.urls import path
from django.contrib.auth import views as auth_views

from .views import (
    registerPage,
    loginPage,
    logoutUser,
    HomeView, 
    ProductListView, 
    ProductDetailView, 
    ContactView, 
    add_to_cart, 
    remove_from_cart, 
    remove_single_item_from_cart, 
    OrderSummaryView,
    CheckoutView,
    PaymentView,
    userProfile,
    shippingAddress,
    billingAddress,
    CustomerOrders,
    AddCouponView,
    RequestRefundView,
    success,
    getDetailsView,
    sendDetailsView,
    successView
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('product/<slug>/', ProductDetailView.as_view(), name="product"),
    path('product-list/<title>/', ProductListView, name="product-list"),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-single-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('order-summary/', OrderSummaryView.as_view(), name="order-summary"),
    path('checkout/', CheckoutView.as_view(), name="checkout"),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    
    path('contact-us/', ContactView.as_view(), name="contact-us"),

    path('register/', registerPage, name="register"),
    path('login/', loginPage, name="login"),
    path('logout/', logoutUser, name="logout"),
    path('user-profile/', userProfile, name="user-profile"),
    path('customer-orders/', CustomerOrders.as_view(), name="customer-orders"),

    path('shipping-address/', shippingAddress, name="shipping-address"),
    path('billing-address/', billingAddress, name="billing-address"),
    
    path('success/', success, name="success"),

    path('get-details/<product>/', getDetailsView, name="get-details"),
    path('send-details/', sendDetailsView, name="send-details"),
    path('success-message/', successView, name="success-message"),
]