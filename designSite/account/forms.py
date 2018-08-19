from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length = 32)
    password = forms.CharField(max_length = 32)

class RegisterForm(forms.Form):
    username = forms.CharField(max_length = 32)
    email = forms.CharField(max_length = 32)
    password = forms.CharField(max_length = 32)
    org = forms.CharField(max_length = 100)
    igem = forms.CharField(max_length = 100)
