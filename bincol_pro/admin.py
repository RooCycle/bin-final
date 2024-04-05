from django.contrib import admin
from django.contrib.auth.models import User
#admin.site.register(User)
# Register your models here.
from django.contrib import admin
from .models import Complaint
from .forms import ComplaintAdminForm
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from .models import Complaint
from django.contrib.auth.models import User, Group

class ComplaintAdmin(admin.ModelAdmin):
    form = ComplaintAdminForm
    list_display = ('number', 'subject', 'assigned_to', 'status', 'created_at')
    actions = ['assign_complaint_to_user']

    def assign_complaint_to_user(self, request, queryset):
        # Get the "Drivers" group
        drivers_group = Group.objects.get(name='Drivers')
        # Filter users belonging to the "Drivers" group
        drivers = drivers_group.user_set.all()
        context = {'complaints': queryset, 'users': drivers}
        return render(request, 'assign_complaint_to_user.html', context)

admin.site.register(Complaint, ComplaintAdmin)

from django.contrib import admin
from .models import Bin
from .forms import BinForm
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

class BinAdmin(admin.ModelAdmin):
    form = BinForm
    list_display = ('bin_number', 'location', 'capacity', 'status', 'assigned_driver')
    actions = ['add_bin', 'edit_bin', 'delete_bin']

    def add_bin(self, request, queryset):
        # Redirect to the add bin view
        #return HttpResponseRedirect(reverse('add_bin'))
        pass

    def edit_bin(self, request, queryset):
        # Ensure only one bin is selected for editing
        pass

    def delete_bin(self, request, queryset):
        # Delete selected bins
        pass
    

admin.site.register(Bin, BinAdmin)

