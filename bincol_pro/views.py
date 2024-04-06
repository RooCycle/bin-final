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

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'login.html', {'message': 'Registration successful. Please log in.'})
    else:
        return render(request, 'activation_invalid.html')

"""def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            auth_login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error_message': 'Invalid login'})
    return render(request, 'login.html')"""
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
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    return render(request, 'login.html')

def home(request):
    return render(request, 'home.html')

#def profile_create(request):
    # We will add logic for creating profile here
    #return render(request, 'profile_create.html')

"""def profile_create(request, username): 
    return render(request, 'profile_create.html', {'username': username})"""

@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {'username': request.user.username})

"""@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Update session to prevent logout
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})"""

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
def lodge_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            form.save()
            # Optionally, you can redirect to a success page or perform other actions
            return redirect('complaint_history')  # Replace 'success_page' with the name of your success page URL
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

def admin_dashboard(request):
    # Retrieve necessary data
    new_complaints = Complaint.objects.filter(status='Pending').count()
    assigned_complaints = Complaint.objects.exclude(assigned_to=None).count()
    rejected_complaints = Complaint.objects.filter(status='Rejected').count()
    completed_complaints = Complaint.objects.filter(status='Resolved').count()
    total_drivers = User.objects.filter(groups__name='Drivers').count()
    total_full_bins = Bin.objects.filter(status='Filled').count()
    total_emptied_bins = Bin.objects.filter(status='Emptied').count()

    # Print the values to check if they are fetched correctly
    print("New Complaints:", new_complaints)
    print("Assigned Complaints:", assigned_complaints)
    print("Rejected Complaints:", rejected_complaints)
    print("Completed Complaints:", completed_complaints)
    print("Total Drivers:", total_drivers)
    print("Total Full Bins:", total_full_bins)
    print("Total Emptied Bins:", total_emptied_bins)

   
    context = {
        'new_complaints': new_complaints,
        'assigned_complaints': assigned_complaints,
        'rejected_complaints': rejected_complaints,
        'completed_complaints': completed_complaints,
        'total_drivers': total_drivers,
        'total_full_bins': total_full_bins,
        'total_emptied_bins': total_emptied_bins,
    }

    return render(request, 'admin/index.html', context)

from django.contrib import messages
from .models import Complaint, Bin

@login_required
def driver_dashboard(request):
    # Check if the user belongs to the "Drivers" group
    if request.user.groups.filter(name='Drivers').exists():
        # Fetch data for the driver dashboard
        assigned_complaints = Complaint.objects.filter(assigned_to=request.user)
        in_progress_complaints = Complaint.objects.filter(status='In Progress', assigned_to=request.user)
        resolved_complaints = Complaint.objects.filter(status='Resolved', assigned_to=request.user)
        assigned_bins = Bin.objects.filter(assigned_driver=request.user)
        total_bins_emptied = Bin.objects.filter(assigned_driver=request.user, status='Emptied').count()

        # Handle POST request to update bin status
        if request.method == 'POST':
            if 'bin_number' in request.POST:  # Update bin status
                bin_id = request.POST.get('bin_number')
                new_status = request.POST.get('new_status')
                # Update the status of the bin
                bin_instance = Bin.objects.get(pk=bin_id)
                bin_instance.status = new_status
                bin_instance.save()
                messages.success(request, "Bin status updated successfully")
            elif 'number' in request.POST:  # Update complaint status
                complaint_id = request.POST.get('number')
                new_status = request.POST.get('new_status')
                # Update the status of the complaint
                complaint = Complaint.objects.get(pk=complaint_id)
                complaint.status = new_status
                complaint.save()
                messages.success(request, "Complaint status updated successfully")

        return render(request, 'driver_dashboard.html', {
            'assigned_complaints': assigned_complaints,
            'in_progress_complaints': in_progress_complaints,
            'resolved_complaints': resolved_complaints,
            'assigned_bins': assigned_bins,
            'total_bins_emptied': total_bins_emptied,
            'username': request.user.username  # Pass the username to the template
        })
    else:
        # Display error message
        messages.error(request, "Access Denied: You are not authorized as a driver")
        return redirect('home')  # Redirect to home or any other page


