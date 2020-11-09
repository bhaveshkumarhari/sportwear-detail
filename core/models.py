from django.conf import settings
from django.db import models
from django.shortcuts import reverse

from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

from django_countries.fields import CountryField

CATEGORY_CHOICES = (
    ('TP','Track Pants'),
    ('ET','Event T-Shirt'),
    ('CUT','Customized T-Shirt'),
    ('COT','Corporate T-Shirt'),
    ('GT','Graphics T-Shirt'),
    ('SPT','Sports T-Shirt'),
    ('SUT','Sublimation T-Shirt'),
    ('CT','Collar T-Shirt'),
    ('RNT','Round Neck T-Shirt')
)

ADDRESS_CHOICES = (
    ('B','Billing'),
    ('S','Shipping'),
)

TSHIRT_SIZES = (
    ('S','S'),
    ('M','M'),
    ('L','L'),
    ('XL','XL'),
    ('XXL','XXL'),
)

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    profile_pic = models.ImageField(default="profile_pic.png", null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    title = models.CharField(choices=CATEGORY_CHOICES, max_length=3)
    description = models.TextField(max_length=1000)
    image = models.CharField(max_length=100)
    # image = models.ImageField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Categories'

    def get_absolute_url(self):
        return reverse("core:product-list", kwargs={
            'title': self.title
        })

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=3)
    slug = models.SlugField()
    description = models.CharField(max_length=100)
    front_image = models.ImageField()
    back_image = models.ImageField()
    side_image = models.ImageField()
    # size = models.CharField(choices=TSHIRT_SIZES, max_length=3)
    quantity = models.IntegerField(default=1)
    new = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })

    def get_update_product_url(self):
        return reverse("dashboard:update-product", kwargs={
            'slug': self.slug
        })

    def get_delete_product_url(self):
        return reverse("dashboard:delete-product", kwargs={
            'slug': self.slug
        })
    
    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })
    
    def saving_price(self):
        return int(self.price - self.discount_price)



class VariationManager(models.Manager):
    def all(self):
        return super(VariationManager, self).filter(active=True)

    def sizes(self):
        return self.all().filter(category="size")

    def colors(self):
        return self.all().filter(category="color")

VAR_CATEGORIES = (
    ('size', 'size'),
    ('color', 'color'),
)

class Variation(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    category = models.CharField(max_length=120, choices=VAR_CATEGORIES, default='size')
    title = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=100, decimal_places=2, null=True, blank=True)
    active = models.BooleanField(default=True)

    objects = VariationManager()

    def __str__(self):
        return self.title

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField(default=1)
    # size = models.CharField(null=False, max_length=150)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    # calculate price with item quantity
    def get_total_item_price(self):
        return self.quantity * self.item.price

    # calculate discounted price with item quantity
    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    # calculate saving amount
    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address',on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    status = models.CharField(max_length=20)
    label = models.CharField(max_length=10)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total
    
    def get_total_quantity(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.quantity
        return total

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'

    
class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    subject = models.CharField(max_length=50)
    message = models.TextField(max_length=500)

    def __str__(self):
        return self.email



class GetDetails(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    subject = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    product = models.CharField(max_length=50)
    size = models.CharField(max_length=50)
    colour = models.CharField(max_length=50)
    message = models.TextField(max_length=500)

    def __str__(self):
        return self.email


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)

