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

    def save_model(self, request, obj, form, change):
        # Call the parent class's save_model method to save the complaint
        super().save_model(request, obj, form, change)

        # Check if a driver has been assigned to the complaint
        if obj.assigned_to:
            # Get the email of the assigned driver
            driver_email = obj.assigned_to.email

            # Craft the email subject and message
            subject = 'Complaint Assignment Notification'
            message = f'Hello {obj.assigned_to.username},\n\nYou have been assigned to handle complaint {obj.number} - {obj.subject}.\n\nRegards,\nThe Admin Team'

            # Send the email
            send_mail(subject, message, 'bincolwaste@gmail.com', [driver_email])

    def assign_complaint_to_user(self, request, queryset):
        # Get the "Drivers" group
        drivers_group = Group.objects.get(name='Drivers')
        # Filter users belonging to the "Drivers" group
        drivers = drivers_group.user_set.all()
        context = {'complaints': queryset, 'users': drivers}
        #return render(request, 'assign_complaint_to_user.html', context)

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
from django.core.mail import send_mail

class BinAdmin(admin.ModelAdmin):
    form = BinForm
    list_display = ('bin_number', 'location', 'capacity', 'status', 'assigned_driver')
    
    def save_model(self, request, obj, form, change):
        # Call the parent class's save_model method to save the bin
        super().save_model(request, obj, form, change)

        # Check if a driver has been assigned to the bin
        if obj.assigned_driver:
            # Get the email of the assigned driver
            driver_email = obj.assigned_driver.email

            # Craft the email subject and message
            subject = 'Bin Assignment Notification'
            message = f'Hello {obj.assigned_driver.username},\n\nYou have been assigned to manage bin {obj.bin_number} at {obj.location}.\n\nRegards,\nThe Admin Team'

            # Send the email
            send_mail(subject, message, 'bincolwaste@gmail.com', [driver_email])

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'assigned_driver':
            # Filter the queryset to include only users in the Drivers group
            kwargs["queryset"] = Group.objects.get(name='Drivers').user_set.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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

