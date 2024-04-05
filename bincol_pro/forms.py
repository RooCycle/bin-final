from django import forms
from .models import Complaint

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = '__all__'

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()

from django import forms
from .models import Bin

class BinForm(forms.ModelForm):
    class Meta:
        model = Bin
        #fields = ['bin_number', 'location', 'capacity', 'status', 'assigned_driver']
        fields = '__all__'

    """def __init__(self, *args, **kwargs):
        super(BinForm, self).__init__(*args, **kwargs)
        self.fields['location'].widget.attrs.update({'class': 'form-control'})
        self.fields['capacity'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})
        self.fields['assigned_driver'].widget.attrs.update({'class': 'form-control'})"""
    def clean_assigned_driver(self):
        assigned_driver = self.cleaned_data['assigned_driver']
        if assigned_driver and not assigned_driver.groups.filter(name='Drivers').exists():
            raise forms.ValidationError("The selected driver must be in the 'Drivers' group.")
        return assigned_driver

# forms.py
from django import forms
from .models import Complaint
from django.contrib.auth.models import Group

class ComplaintAdminForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = '__all__'

    def clean_assigned_to(self):
        assigned_to = self.cleaned_data.get('assigned_to')
        if assigned_to:
            drivers_group = Group.objects.get(name='Drivers')
            if assigned_to.groups.filter(name='Drivers').exists():
                return assigned_to
            else:
                raise forms.ValidationError("The selected user must belong to the Drivers group.")
        else:
            return assigned_to
