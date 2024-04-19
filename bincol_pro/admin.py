from django.contrib import admin
from django.contrib.auth.models import User
#admin.site.register(User)
# Register your models here.
from django.contrib import admin
from .models import Complaint, UserProfile
from .forms import ComplaintAdminForm
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from .models import Complaint
from django.contrib.auth.models import User, Group

class ComplaintAdmin(admin.ModelAdmin):
    form = ComplaintAdminForm
    list_display = ('number', 'subject', 'assigned_to', 'status', 'created_at')
    list_display = ['number', 'subject', 'assigned_to', 'status', 'created_at']
    search_fields = ['number']

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
from django.contrib import admin
from django.utils.html import format_html
from .models import Bin


class BinAdmin(admin.ModelAdmin):
    form = BinForm
    list_display = ('bin_number', 'location', 'capacity', 'status', 'assigned_driver')
    #actions = ['add_bin', 'edit_bin', 'delete_bin']
    

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

    def bin_emptying_report_button(self, obj):
        url = reverse('bin_emptying_report')
        return format_html('<a class="button" href="{}">Bin Emptying Report</a>', url)

    bin_emptying_report_button.short_description = "Bin Emptying Report"

    # Add this method to list_display or list_display_links depending on where you want the button to appear
    list_display = ['bin_number', 'location', 'capacity', 'status', 'assigned_driver', 'created_at']
    search_fields = ['bin_number']

    list_display = ['bin_number', 'location', 'capacity', 'status', 'assigned_driver', 'created_at']
    #actions = ['generate_driver_wise_report']
    
    def generate_driver_wise_report(self, request, queryset):
        url = reverse('driver_wise_bin_emptying_report') + f'?assigned_driver={bin.assigned_driver}'
        return format_html('<a class="button" href="{}">Generate Report</a>', url)
    generate_driver_wise_report.short_description = 'Generate Driver-wise Emptying Report'
    
    
admin.site.register(Bin, BinAdmin)


# admin.py

from django.contrib import admin
from .models import AboutUs, ContactUs

class AboutUsAdmin(admin.ModelAdmin):
    list_display = ['title']  # Display the title in the admin list view

admin.site.register(AboutUs, AboutUsAdmin)

class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['title']  # Display the title in the admin list view

admin.site.register(ContactUs, ContactUsAdmin)

#admin.site.register_view('dashboard/', view=admin_dashboard, name='admin_dashboard')

