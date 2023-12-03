from django.forms import ModelForm
from django.forms.widgets import TextInput
from .models import Subject


class SubjectForm(ModelForm):
    class Meta:
        model = Subject
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }
