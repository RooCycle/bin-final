from django.db import models
from django.contrib.auth.models import User

class Complaint(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected'),
        ('In Progress', 'In Progress'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    assigned_to = models.ForeignKey(User, related_name='assigned_complaints', on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint #{self.number}"
    # Add any other fields you need for the Complaint model


class UserProfile(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)


from django.db import models

class Bin(models.Model):
    LOCATION_CHOICES = (
        ('NSW', 'New South Wales'),
        ('VIC', 'Victoria'),
        ('QLD', 'Queensland'),
    )

    CAPACITY_CHOICES = (
        (100, '100 litres'),
        (200, '200 litres'),
        (300, '300 litres'),
    )

    STATUS_CHOICES = (
        ('Emptied', 'Emptied'),
        ('Filled', 'Filled'),
    )

    bin_number = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=3, choices=LOCATION_CHOICES)
    capacity = models.IntegerField(choices=CAPACITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    assigned_driver = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)


    def __str__(self):
        return self.bin_number

