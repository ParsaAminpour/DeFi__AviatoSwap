from attr import fields
from django import forms
from matplotlib import widgets
from .models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from email.mime.multipart import MIMEMultipart as main
from email.mime import text
from random import randint
import smtplib
import re

    

class SignUp(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class' : 'username', 'name' : 'username',
            'type' : 'text', 'required' : '', 'placeholder' : 'Your username',
            'onkeydown' : 'usernameValidation()'
        })
        self.fields['email'].widget.attrs.update({
            'class' : 'email', 'name' : 'email',
            'type' : 'text', 'required' : '' , 'placeholder' : 'Your email',
            'onkeydown' : 'emailValidation()'
        })
        self.fields['password1'].widget.attrs.update({
            'class' : 'password1', 'name':'password1',
            'type':'password', 'required' : '' , 'placeholder' : 'password',
            'onkeydown' : 'passwod1Validation()'
        })
        self.fields['password2'].widget.attrs.update({
            'class' : 'password2', 'name' : 'password2',
            'type' : 'password' , 'required' : '' , 'placeholder' : 'password confirmation',
            'onkeydown' : 'password2Validation()'
        })

    class Meta:
        model = User
        fields = ('username' ,'email', 'password1', 'password2')

    def clean_email(self):
        # pattern = r'^[a-z]+(?:(?:\.[a-z]+)+\d*|(?:_[a-z]+)+(?:\.\d+)?)?@(?!.*\.\.)[^\W_][a-z\d.]+[a-z\d]{2}$'
        pattern = r'\w*'
        result = re.match(pattern, self.cleaned_data.get('email'))
        if not bool(result):
            raise forms.ValidationError('email is invalid')
        return self.cleaned_data.get('email')


class login_form(forms.Form):
    username = forms.CharField(widget=forms.TextInput(
        attrs={                                                                                                                                                                                                                                                                                                                                     
            'class' : 'username_login',
            'placeholder' : 'Your Username'
        }
    ))
    password = forms.CharField(widget=forms.TextInput(
        attrs={
            'class':'password',
            'placeholder' : 'Password'
        }
    ))

    # def clean_password(self):
    #     password = self.cleaned_data['password']
    #     pattern = r'\w*'
    #     if not bool(re.match(pattern, password)):
    #         raise forms.ValidationError('The password is invalid')
    #     return password 


# class login_form(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ('username', 'password', )

#         labels = {
#             'username' : _('Username'),
#             'password' : _('Password')
#         }

#         help_texts = {
#             'username' : ''
#         }


#         widgets={
#             'username' : forms.TextInput(attrs={
#                 'class' : 'username_login',
#                 'placeholder' : 'Username'
#             }),
#             'password' : forms.PasswordInput(attrs={
#                 'class' : 'password',
#                 'placeholder':'Password'
#             })
#         }
    
#     def clean_password(self):
#         password = self.cleaned_data['password']
#         pattern = r'\w*'
#         if not bool(re.match(pattern, password)):
#             raise forms.ValidationError('invalid password')
#         return password



# class SignUp(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ('username', 'first_name', 'last_name', 'email')
#         labels = {
#             'username' : _('username'),
#             'first_name' : _('first name'),
#             'last_name' : _('last name'),
#             'email' : _('gmail')
#         }
#         error_messages = {
#             'username' : {
#                 'max_length' : _('This username is invalid')
#             }
#         }
#         help_texts = {
#             'username' : ''
#         }
#         widgets = {
#             'username': forms.TextInput(attrs={
#             'class': 'username',
#             'style': 'background-color: white',
#             'placeholder': 'Your username',
#             }),

#             'first_name' : forms.TextInput(attrs={
#                 'class' : 'first-name',
#                 'placeholder' : 'Your firstname'
#             }),

#             'last_name' : forms.TextInput(attrs={
#                 'class' : 'last-name',
#                 'placeholder': 'Your lastname'
#             }),

#             'email' : forms.EmailInput(attrs={
#                 'class' : 'email',
#                 'placeholder' : 'Your Gmail'
#             })
#         }


#     def send_email(self):
#         msg = main()
#         msg['from'] = 'parsa.aminpour.dev@gmail.com'
#         msg['to'] = self.cleaned_data['email']
#         msg['subject'] = 'login code'
#         body = text(f'Your validation code is {randint(110000,999999)}')
#         msg.attach(body)

#         with smtplib.SMTP(host='smtp.google.com', port=587) as smtp:
#             smtp.ehlo()
#             smtp.starttls()
#             password = 'parsaaminpourdev'
#             smtp.login('parsa.aminpour.dev@gmail.com', password=password)
#             smtp.send_message(msg)

#     def clean_email(self):
#         email = self.cleaned_data['email']
#         pattern = '^[a-z]+(?:(?:\.[a-z]+)+\d*|(?:_[a-z]+)+(?:\.\d+)?)?@(?!.*\.\.)[^\W_][a-z\d.]+[a-z\d]{2}$'
#         if not bool(re.match(pattern, email)):
#             raise forms.ValidationError('This email is invalid')
#         return email
