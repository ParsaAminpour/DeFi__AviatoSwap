from django import forms
from datetime import datetime as dt
from django.utils import timezone
from swap.forms import EditProfileForm
from .models import Message
from rich.console import Console

console  = Console()

class Chat(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('message',)
    
        widgets = {
            'message' : forms.TextInput(attrs={
                'class':'msg-area', 'placeholder':'Your message...',
                'required':True
            }),
        }
    
    def clean_message(self):
        msg = self.cleaned_data.get("message")
        if len(msg) >= 256 or len(msg) ==0:
            return forms.ValidationError("This message length is out of the range")
            
        return self.cleaned_data.get("message")

    def __init__(self, *args, **kwargs):
        super(Chat, self).__init__(args, kwargs)
        self.fields['message'].required = True
        self.fields['owner'].required = True
        self.fields['time'] = timezone.now()