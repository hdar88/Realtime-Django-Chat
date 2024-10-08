from django.forms import ModelForm
from django import forms
from .models import *

'''Form for creating a new chat message using the GroupMessage model.'''

class ChatmessageCreateForm(ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['body']
        widgets =  {
            'body' : forms.TextInput(attrs={'placeholder': 'Add message...', 'class': 'p-4 text-black', 'max-length' : '300', 'autofocus' : True}),
        }
