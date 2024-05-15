from django.shortcuts import render
from django.contrib.auth.models import User

# views.py
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import authenticate, login
from .models import UserProfile
from .tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.views import PasswordResetCompleteView
from django.urls import reverse_lazy

def signup(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        
        user = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
        user.is_active = False
        user.save()

        # Send activation email
        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        activation_link = f"http://{current_site.domain}/activate/{uid}/{token}"  # Replace with your actual domain
        send_mail(
            'Activate your account',
            f'Click the link to activate your account: {activation_link}',
            'accounts@bincol.com',  # Replace with your email address
            [user.email],
            fail_silently=False,
        )
        return render(request, 'activation_sent.html')

    return render(request, 'signup.html')



from django.core.mail import send_mail
from django.conf import settings

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        # Replace 'admin@example.com' with the actual email address of your admin
        admin_email = 'iandan_bincol@outlook.com'  
        subject = 'User Activation Notification'
        message = f'The user {user.username} has been successfully activated. Please assign them a role'
        from_email = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message, from_email, [admin_email])

        return render(request, 'login.html', {'message': 'Registration successful. Please log in.'})
    else:
        return render(request, 'activation_invalid.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            auth_login(request, user)
            # Check if the user is an admin
            if user.is_staff and user.is_superuser:
                return redirect('admin:index')  # Redirect to Django admin
            else:
                return redirect('dashboard') 
            
        else:
            error_message = 'Invalid username or password: please check and try again'
            return render(request, 'login.html', {'error_message': error_message})
    return render(request, 'login.html')

def home(request):
    return render(request, 'home.html')


@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {'username': request.user.username})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password1 = form.cleaned_data['new_password1']
            new_password2 = form.cleaned_data['new_password2']
            
            # Check if old password is the same as new password
            if old_password == new_password1:
                messages.error(request, "Old password cannot be used as new password.")
                return redirect('change_password')

            # Check if new password contains mixed characters
            if not any(char.isdigit() for char in new_password1) or not any(char.isalpha() for char in new_password1):
                messages.error(request, "New password must contain both letters and digits.")
                return redirect('change_password')

            # Proceed with changing the password
            user = form.save()
            update_session_auth_hash(request, user)  # Update session to prevent logout
            messages.success(request, "Password changed successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "Password change failed. Please try again.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

def password_reset_form(request):
    return render(request, 'password_reset_form.html')

from .forms import ComplaintForm
from django.contrib.auth.decorators import login_required
from .forms import ComplaintForm

"""@login_required
def lodge_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user  # Set the user field
            complaint.save()
            return redirect('complaint_history')
    else:
        form = ComplaintForm()
    return render(request, 'lodge_complaint.html', {'form': form})"""
@login_required
def lodge_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            # Save the complaint
            # Associate the complaint with the currently logged-in user
            complaint = form.save(commit=False)
            complaint.user = request.user  # Assuming user field in the Complaint model is named 'user'
            complaint.save()

            # Notify the admin via email
            admin_email = 'iandan_bincol@outlook.com'  # Replace with your admin's email
            subject = 'New Complaint Lodged'
            message = f'A new complaint with number {complaint.number} has been lodged. Please assign it to a driver.'
            send_mail(subject, message, 'bincolwaste@gmail.com', [admin_email])

            # Display success message
            messages.success(request, 'Complaint lodged successfully. Admin has been notified.')
            return redirect('lodge_complaint')  # Redirect to the homepage
    else:
        form = ComplaintForm()

    return render(request, 'lodge_complaint.html', {'form': form})


from django.shortcuts import render
from .models import Complaint

def complaint_history(request):
    user_complaints = Complaint.objects.filter(user=request.user)
    return render(request, 'complaint_history.html', {'user_complaints': user_complaints})

import csv
from django.shortcuts import render
from .forms import CSVUploadForm
from .models import Complaint

@login_required
def upload_complaints(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            if csv_file.name.endswith('.csv'):
                user = request.user
                # Process the CSV file
                complaints = []
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)
                next(reader)  #skip the first row because its the title row
                for row in reader:
                    complaint = Complaint(
                        user=user,
                        number=row[0],  # Assuming Number is the first column
                        subject=row[1],  # Assuming Subject is the second column
                        description=row[2],  # Assuming Description is the third column
                        status=row[3],  # Assuming Status is the fourth column
                        # Add more fields as needed, adjust column indices accordingly
                    )
                    complaints.append(complaint)
                # Bulk create complaints to improve performance
                Complaint.objects.bulk_create(complaints)
                messages.success(request, 'Complaints uploaded successfully.')
            else:
                messages.error(request, 'Invalid file format. Please upload a CSV file.')
                return render(request, 'upload_complaints.html', {'form': form})
    else:
        form = CSVUploadForm()
    return render(request, 'upload_complaints.html', {'form': form})


from django.contrib.auth.models import Group

def dashboard(request):
    user = request.user
    is_driver = user.groups.filter(name='Drivers').exists()
    is_user = user.groups.filter(name='Ordinary User').exists()
    context = {
        'is_driver': is_driver,
        'is_user': is_user
    }
    return render(request, 'dashboard.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from .models import Bin
from .forms import BinForm

def bin_list(request):
    bins = Bin.objects.all()
    return render(request, 'bin_list.html', {'bins': bins})

def add_bin(request):
    if request.method == 'POST':
        form = BinForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('bin_list')
    else:
        form = BinForm()
    return render(request, 'add_bin.html', {'form': form})

def edit_bin(request, bin_id):
    bin_instance = get_object_or_404(Bin, id=bin_id)
    if request.method == 'POST':
        form = BinForm(request.POST, instance=bin_instance)
        if form.is_valid():
            form.save()
            return redirect('bin_list')
    else:
        form = BinForm(instance=bin_instance)
    return render(request, 'edit_bin.html', {'form': form})

def delete_bin(request, bin_id):
    bin_instance = get_object_or_404(Bin, id=bin_id)
    if request.method == 'POST':
        bin_instance.delete()
        return redirect('bin_list')
    return render(request, 'delete_bin.html', {'bin': bin_instance})


"""def assign_complaint(request, complaint_id):
    complaint = Complaint.objects.get(pk=complaint_id)
    if request.method == 'POST':
        form = AssignComplaintForm(request.POST)
        if form.is_valid():
            assigned_to = form.cleaned_data['assigned_to']
            complaint.assigned_to = assigned_to
            complaint.save()
            return redirect('complaint_history')  # Redirect to complaint history page
    else:
        form = AssignComplaintForm()
    return render(request, 'assign_complaint.html', {'form': form})"""

from django.shortcuts import render
from .models import Complaint, Bin
from django.contrib.auth.models import User, Group

from django.shortcuts import render
from .models import Complaint, Bin, User

def admin_dashboard(request):
    new_complaints = Complaint.objects.filter(status='Pending').count()
    assigned_complaints = Complaint.objects.filter(status='Assigned').count()
    rejected_complaints = Complaint.objects.filter(status='Rejected').count()
    completed_complaints = Complaint.objects.filter(status='Resolved').count()
    total_drivers = User.objects.filter(groups__name='Drivers').count()
    total_full_bins = Bin.objects.filter(status='Filled').count()
    total_emptied_bins = Bin.objects.filter(status='Emptied').count()

    return render(request, 'admin_dashboard.html', {
        'new_complaints': new_complaints,
        'assigned_complaints': assigned_complaints,
        'rejected_complaints': rejected_complaints,
        'completed_complaints': completed_complaints,
        'total_drivers': total_drivers,
        'total_full_bins': total_full_bins,
        'total_emptied_bins': total_emptied_bins,
    })


from django.contrib import messages
from .models import Complaint, Bin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

@login_required
def driver_dashboard(request):
    if request.user.groups.filter(name='Drivers').exists():
        # Fetch data for the driver dashboard
        assigned_complaints = Complaint.objects.filter(assigned_to=request.user)
        in_progress_complaints = Complaint.objects.filter(status='In Progress', assigned_to=request.user)
        resolved_complaints = Complaint.objects.filter(status='Resolved', assigned_to=request.user)
        new_complaints = Complaint.objects.filter(status='Pending', assigned_to=request.user)
        assigned_bins = Bin.objects.filter(assigned_driver=request.user)
        total_bins_emptied = Bin.objects.filter(assigned_driver=request.user, status='Emptied').count()

        # Pagination for assigned bins
        bin_page_number = request.GET.get('bin_page')
        bin_paginator = Paginator(assigned_bins, 5)  # Show 5 bins per page
        assigned_bins_page = bin_paginator.get_page(bin_page_number)

        # Pagination for assigned complaints
        complaint_page_number = request.GET.get('complaint_page')
        complaint_paginator = Paginator(assigned_complaints, 5)  # Show 5 complaints per page
        assigned_complaints_page = complaint_paginator.get_page(complaint_page_number)

        # Handle POST request to update bin status or complaint status
        if request.method == 'POST':
            if 'bin_id' in request.POST:
                bin_id = request.POST.get('bin_id')
                new_bin_status = request.POST.get('new_status')
                bin_instance = Bin.objects.get(pk=bin_id)
                bin_instance.status = new_bin_status
                bin_instance.save()
                messages.success(request, "Bin status updated successfully")
            elif 'complaint_number' in request.POST:
                complaint_id = request.POST.get('complaint_number')
                new_complaint_status = request.POST.get('new_status')
                complaint_instance = get_object_or_404(Complaint, pk=complaint_id)

                # Check if the status is being updated to "Resolved"
                # Check if the status is being updated to "Resolved"
                # Check if the status is being updated to "Resolved"
                if new_complaint_status == 'Resolved':
                    # Get the user who lodged the complaint
                    user = complaint_instance.user
                    # Send an email notification to the user
                    subject = 'Complaint Resolved Notification'
                    message_user = f"Your complaint with number {complaint_instance.number} has been resolved."
                    from_email = settings.DEFAULT_FROM_EMAIL
                    to_email_user = user.email
                    send_mail(subject, message_user, from_email, [to_email_user])

                    # Send an email notification to the admin
                    admin_email = 'iandan_bincol@outlook.com'  # Replace with the admin's email address
                    admin_user = User.objects.get(username='admin')  # Assuming the admin username is 'admin'
                    message_admin = f"A complaint with number {complaint_instance.number} has been resolved."
                    to_email_admin = admin_email if admin_email else admin_user.email
                    send_mail(subject, message_admin, from_email, [to_email_admin])

                # Update the complaint status
                complaint_instance.status = new_complaint_status
                complaint_instance.save()
                messages.success(request, "Complaint status updated successfully")

        # Handle search queries
        bin_id_query = request.GET.get('bin_id')
        complaint_number_query = request.GET.get('complaint_number')

        if bin_id_query:
            assigned_bins = assigned_bins.filter(bin_number__icontains=bin_id_query)
        if complaint_number_query:
            assigned_complaints = assigned_complaints.filter(number=complaint_number_query)

        return render(request, 'driver_dashboard.html', {
            'assigned_complaints_page': assigned_complaints_page,
            'new_complaints': new_complaints,
            'assigned_complaints': assigned_complaints,
            'in_progress_complaints': in_progress_complaints,
            'resolved_complaints': resolved_complaints,
            'assigned_bins_page': assigned_bins_page,
            'assigned_bins': assigned_bins,
            'total_bins_emptied': total_bins_emptied,
            'username': request.user.username,
            'updated_bin_status': new_bin_status if 'new_status' in locals() else None,
            'updated_complaint_status': new_complaint_status if 'new_status' in locals() else None
        })
    else:
        messages.error(request, "Access Denied: You are not authorized as a driver")
        return redirect('dashboard')  # Redirect to home or any other page
  # Redirect to home or any other page
    

# views.py
from django.shortcuts import render
from .models import Bin

def bin_report(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # Retrieve data based on date range
        assigned_bins = Bin.objects.filter(
            assigned_driver=request.user,
            created_at__range=[start_date, end_date]
        )
        
        bins_data = []
        for bin in assigned_bins:
            bin_data = {
                'bin_number': bin.bin_number,
                'status': 'Filled' if bin.status == 'Filled' else 'Emptied' if bin.status == 'Emptied' else 'Unknown',
                'date': bin.created_at if bin.status == 'Filled' else None
            }
            bins_data.append(bin_data)
        
        return render(request, 'bin_report.html', {
            'start_date': start_date,
            'end_date': end_date,
            'bins_data': bins_data,
        })
    else:
        return render(request, 'bin_report.html')
    
def lodged_complaint_report(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # Retrieve data based on date range
        assigned_complaints = Complaint.objects.filter(
            assigned_to=request.user,
            created_at__range=[start_date, end_date]
        )
        resolved_complaints = Complaint.objects.filter(
            assigned_to=request.user,
            status='Resolved',
            created_at__range=[start_date, end_date]
        )
        pending_complaints = Complaint.objects.filter(
            assigned_to=request.user,
            status='Pending',
            created_at__range=[start_date, end_date]
        )
        
        return render(request, 'lodged_complaint_report.html', {
            'start_date': start_date,
            'end_date': end_date,
            'assigned_complaints': assigned_complaints,
            'resolved_complaints': resolved_complaints,
            'pending_complaints': pending_complaints,
        })
    else:
        return render(request, 'lodged_complaint_report.html')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group


from django.contrib import messages
from django.shortcuts import redirect, render

@login_required
def ordinary_user_dashboard(request):
    # Check if the user is in the "Ordinary User" group
    if request.user.groups.filter(name='Ordinary User').exists():
        # Render the ordinary user dashboard template
        return render(request, 'ordinary_user_dashboard.html')
    else:
        # Add a message informing the user they don't have access
        messages.warning(request, "You don't have permission to access the Ordinary User Dashboard.")
        # Redirect the user back to the main dashboard page
        return redirect('dashboard')


def search_complaint(request):
    if request.method == 'GET':
        complaint_number = request.GET.get('complaint_number', '')
        user_complaints = Complaint.objects.filter(user=request.user)
        if complaint_number:
            complaint = user_complaints.filter(number=complaint_number).first()
            if complaint:
                context = {'user_complaints': user_complaints, 'search_result': complaint}
            else:
                context = {'user_complaints': user_complaints, 'search_result': None, 'no_result': True}
            return render(request, 'complaint_history.html', context)
        else:
            return render(request, 'complaint_history.html', {'user_complaints': user_complaints})
    
from django.shortcuts import render
from .models import Bin
from django.utils import timezone

def bin_emptying_report(request):
    emptied_bins = []
    start_date = None
    end_date = None

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        emptied_bins = Bin.objects.filter(
            status='Emptied',
            created_at__range=[start_date, end_date]
        )

    return render(request, 'bin_emptying_report.html', {
        'emptied_bins': emptied_bins,
        'start_date': start_date,
        'end_date': end_date,
    })

from django.shortcuts import render
from .models import Bin

def driver_wise_bin_emptying_report(request):
    drivers_group = Group.objects.get(name='Drivers')
    drivers = User.objects.filter(groups__in=[drivers_group])
    
    if request.method == 'POST':
        # Retrieve form data including driver and date range
        driver_username = request.POST.get('driver_username')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Query bins based on the selected driver and date range
        bins = Bin.objects.filter(assigned_driver__username=driver_username, created_at__range=[start_date, end_date])

        return render(request, 'driver_wise_bin_emptying_report.html', {'bins': bins, 'drivers': drivers})
    else:
        return render(request, 'driver_wise_bin_emptying_report.html', {'drivers': drivers})

from django.shortcuts import render
from .models import Complaint

def lodged_complaints_report(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # Query lodged complaints within the specified date range
        complaints = Complaint.objects.filter(created_at__range=[start_date, end_date])
        
        return render(request, 'lodged_complaints_report.html', {'complaints': complaints, 'form_submitted': True})
    else:
        # If the request method is not POST, render the empty form
        return render(request, 'lodged_complaints_report.html', {'form_submitted': False})
    
from django.shortcuts import render
from .models import Complaint
from django.contrib.auth.models import User, Group

def driver_wise_complaint_report(request):
    # Retrieve all users belonging to the 'Driver' group
    drivers_group = Group.objects.get(name='Drivers')
    drivers = User.objects.filter(groups__in=[drivers_group])
    
    if request.method == 'POST':
        # Process form submission
        driver_id = request.POST.get('driver_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Query complaints based on the selected driver and date range
        complaints = Complaint.objects.filter(assigned_to=driver_id, created_at__range=[start_date, end_date])

        return render(request, 'driver_wise_complaint_report.html', {'complaints': complaints, 'drivers': drivers})
    else:
        return render(request, 'driver_wise_complaint_report.html', {'drivers': drivers})


# views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import AboutUs, ContactUs

def about_us(request):
    about_page = AboutUs.objects.first()  # Assuming there's only one About Us page
    return render(request, 'about_us.html', {'about_page': about_page})

def contact_us(request):
    contact_page = ContactUs.objects.first()  # Assuming there's only one Contact Us page
    return render(request, 'contact_us.html', {'contact_page': contact_page})

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('home')

from django.shortcuts import render
from plotly.offline import plot
import plotly.graph_objs as go
from .models import Complaint

def driver_complaint_status_chart(request):
    # Retrieve complaint statuses for the specific driver
    driver = request.user
    pending_count = Complaint.objects.filter(assigned_to=driver, status='Pending').count()
    in_progress_count = Complaint.objects.filter(assigned_to=driver, status='In Progress').count()
    resolved_count = Complaint.objects.filter(assigned_to=driver, status='Resolved').count()

    # Create the pie chart
    labels = ['Pending', 'In Progress', 'Resolved']
    values = [pending_count, in_progress_count, resolved_count]

    trace = go.Pie(labels=labels, values=values)

    # Generate the HTML for the chart
    chart_div = plot([trace], output_type='div')

    return render(request, 'driver_complaint_status_chart.html', {'chart_div': chart_div})


# views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Bin
import json

from django.shortcuts import render
from plotly.offline import plot
import plotly.graph_objs as go
from .models import Bin

def driver_bin_status_chart(request):
    # Retrieve bin data for the specific driver
    bins = Bin.objects.filter(assigned_driver=request.user)
    
    # Count bin statuses
    filled_bins = bins.filter(status='Filled').count()
    emptied_bins = bins.filter(status='Emptied').count()

    # Create pie chart data
    labels = ['Filled', 'Emptied']
    values = [filled_bins, emptied_bins]

    data = go.Pie(labels=labels, values=values)

    # Generate plot
    plot_div = plot([data], output_type='div', include_plotlyjs=False)

    return render(request, 'driver_bin_status_chart.html', context={'plot_div': plot_div})


from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.shortcuts import redirect

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')  # Specify the URL name of your home page here


from django.shortcuts import render, redirect
from .models import ChartInReports
from django.contrib import messages

def save_chart(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        html_content = request.POST.get('chart_div')

        # Check if a chart with the same name already exists
        if ChartInReports.objects.filter(name=name).exists():
            messages.error(request, f"A chart with the name '{name}' already exists.")
            return redirect('driver_complaint_chart')  # Redirect back to the chart page

        # Save the chart details to the database
        chart = ChartInReports(name=name, html_content=html_content)
        chart.save()

        messages.success(request, f"Chart '{name}' saved successfully.")
        return redirect('driver_complaint_chart')  # Redirect back to the chart page

    else:
        # Handle GET requests if necessary
        pass


from django.shortcuts import redirect

def admin_home_redirect(request):
    return redirect('home')  # Assuming 'home' is the name of the URL pattern for your custom home page




