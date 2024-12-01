from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    # Add first name, last name, email, and username explicitly
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    
    # The password and confirm password fields are already part of the UserCreationForm
    password1 = forms.CharField(
        label="Password", 
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        strip=False,
    )
    password2 = forms.CharField(
        label="Repeat password", 
        widget=forms.PasswordInput(attrs={'placeholder': 'Repeat Password'}),
        strip=False,
    )
    
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')
    
    def clean_password2(self):
        """ Ensure both password fields match """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match")
        return password2
