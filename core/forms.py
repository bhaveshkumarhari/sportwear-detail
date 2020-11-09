from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from django.forms import ModelForm

from .models import UserProfile, CustomerProfile, GetDetails

from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'Paypal')
)

class GetDetailsForm(ModelForm):
    class Meta:
        model = GetDetails
        fields = '__all__'

# class UserInfoForm(ModelForm):
#     class Meta:
#         model = User
#         fields = ['first_name', 'last_name', 'email']

class UserInfoForm(ModelForm):
    class Meta:
        model = CustomerProfile
        fields = '__all__'
        exclude = ['user']


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields= ['first_name','last_name','username','email','password1','password2']


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_country = CountryField(blank_label='select country').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'ps-select selectpicker',
    }))
    shipping_zip = forms.CharField(required=False)
    shipping_state = forms.CharField(required=False)

    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'ps-select selectpicker',
    }))
    billing_zip = forms.CharField(required=False)
    billing_state = forms.CharField(required=False)

    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)

    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)
    

class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'Promo code',
        'aria-label' : 'Recipient\'s username',
        'aria-describedby' : 'basic-addon2',
        'size': '15'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()
    

class ContactForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))

class ProductForm(forms.Form):
    size = forms.CharField()
    value = forms.CharField()
    color = forms.CharField()


class ShippingAddressForm(forms.Form):
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_country = forms.CharField(required=False)
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
    billing_country = forms.CharField(required=False)
    billing_country = CountryField(blank_label='select country').formfield(
        required=True,
        widget=CountrySelectWidget(attrs={
            'class': 'ps-select selectpicker form-control',
    }))
    billing_zip = forms.CharField(required=False)
    billing_state = forms.CharField(required=False)
    same_shipping_address = forms.BooleanField(required=False)