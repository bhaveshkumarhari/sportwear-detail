from django.urls import path
from .views import HomeView, customerProfile, productList, createProduct, update_product, delete_product, registerPage, loginPage, logoutUser, userPage, customerList, orderList, shippingAddress, billingAddress, adminAccount

app_name = 'dashboard'

urlpatterns = [
    path('dashboard/', HomeView, name="dashboard-home"),
    path('dashboard/customer-profile/<user>/', customerProfile, name="customer-profile"),
    path('dashboard/product-list/', productList, name="dashboard-product-list"),
    path('dashboard/create-product/', createProduct.as_view(), name="create-product"),
    path('dashboard/update-product/<slug>/', update_product, name="update-product"),
    path('dashboard/delete-product/<slug>/', delete_product, name="delete-product"),

    path('dashboard/customer-list/', customerList, name="customer-list"),
    path('dashboard/order-list/', orderList, name="order-list"),

    path('dashboard/register/', registerPage, name="dashboard-register"),
    path('dashboard/login/', loginPage, name="dashboard-login"),
    path('dashboard/logout/', logoutUser, name="dashboard-logout"),

    path('dashboard/account/', adminAccount, name="dashboard-account"),

    path('dashboard/user-page/', userPage.as_view(), name="user-page"),

    path('shipping-address/<user>/', shippingAddress, name="shipping-address"),
    path('billing-address/<user>/', billingAddress, name="billing-address"),
]