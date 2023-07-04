from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelChoiceField
from .models import *

class LoginForm(forms.Form):
    username = forms.CharField(
        widget= forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )

class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'is_admin', 'is_employee', 'is_customer', 'profile_pic')

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'profile_pic')

class EventsUpdateForm(forms.ModelForm):
    class Meta:
        model = Events
        fields = ('name', 'attendees_expected', 'venue',    'catering_package',
                  'decor_package', 'videography_package', 'status', 'total_price')

class EventsForm(forms.ModelForm):
    class Meta:
        model = Events
        fields = ('name', 'type', 'attendees_expected', 'venue', 'date', 'decor_package', 'catering_package',
                  'videography_package')
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'date'})
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('subject', 'message')

class UserCreationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    user_type = forms.ChoiceField(choices=[('customer', 'Customer'), ('supplier', 'Supplier')])

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'password1', 'password2', 'user_type']

class VenueCreationForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = '__all__'