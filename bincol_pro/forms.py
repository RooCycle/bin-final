from django import forms
from .models import Complaint

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = '__all__'

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()