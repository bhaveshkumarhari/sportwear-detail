from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.forms import ModelForm
from core.models import Item, CustomerProfile

from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from django import forms

CATEGORY_CHOICES = (
    ('','Choose category'),
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

TSHIRT_SIZES = (
    ('','Choose size'),
    ('B','S'),
    ('M','M'),
    ('L','L'),
    ('XL','XL'),
    ('XXL','XXL'),
)

class ProductForm(forms.Form):
    title = forms.CharField()
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, widget=forms.Select(attrs={'class': 'form-control form-control-primary', 'id':'input_category'}))
    description = forms.CharField()
    size = forms.ChoiceField(choices=TSHIRT_SIZES, widget=forms.Select(attrs={'class': 'form-control form-control-primary'}))
    slug = forms.CharField()
    price = forms.FloatField()
    discount_price = forms.FloatField()
    front_image = forms.ImageField()
    back_image = forms.ImageField()
    side_image = forms.ImageField()
    quantity = forms.IntegerField()
    new = forms.BooleanField(required=False)

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = '__all__'

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields= ['username','email','password1','password2']

class ShippingAddressForm(forms.Form):
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    # shipping_country = forms.CharField(required=False)
    shipping_country = CountryField(blank_label='select country').formfield(
        required=True,
        widget=CountrySelectWidget(attrs={
            'class': 'ps-select selectpicker form-control',
    }))
    shipping_zip = forms.CharField(required=False)
    shipping_state = forms.CharField(required=False)
    same_billing_address = forms.BooleanField(required=False)

class BillingAddressForm(forms.Form):
    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    # billing_country = forms.CharField(required=False)
    billing_country = CountryField(blank_label='select country').formfield(
        required=True,
        widget=CountrySelectWidget(attrs={
            'class': 'ps-select selectpicker form-control',
    }))
    billing_zip = forms.CharField(required=False)
    billing_state = forms.CharField(required=False)
    same_shipping_address = forms.BooleanField(required=False)
    

# class UserInfoForm(ModelForm):
#     class Meta:
#         model = User
#         fields = ['first_name', 'last_name', 'email']

class UserInfoForm(ModelForm):
    class Meta:
        model = CustomerProfile
        fields = '__all__'
        exclude = ['user']

class AdminForm(ModelForm):
    class Meta:
        model = CustomerProfile
        fields = '__all__'
        exclude = ['user']