from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
from django.contrib.auth import get_user_model

# Create your models here.

Equipment_availability= (
    ("available", "AVAILABLE"),
    ("not available", "NOT AVAILABLE"),
)
payment_status= (
    ("paid", "PAID"),
    ("pending", "PENDING"),
)
Staff_role = (
    ("deejay", "DEEJAY"),
    ("mc", "MC"),
    ("sound engineer", "SOUND ENGINNER"),
)
Event_type = (
    ("teambuilding", "TEAMBUILDING"),
    ("traditional wedding", "TRADITIONAL WEDDING"),
    ("graduation party", "GRADUATION  PARTY"),
    ("urban wedding", "URBAN WEDDING"),
    ("christmas party", "CHRISTMAS PARTY"),
    ("book launching", "BOOK LAUNCHING"),
    ("festival", "FESTIVAL"),
    ("educational", "EDUCATIONAL"),
    ("funday", "FUNDAY"),
    ("seminar", "SEMINAR"),
    ("confrence", "CONFRENCE"),
    ("workshop", "WORKSHOP"),



)

class User(AbstractUser):
    is_admin = models.BooleanField('Is admin', default=False)
    is_customer = models.BooleanField('Is customer', default=False)
    is_employee = models.BooleanField('Is employee', default=False)
    profile_pic = models.ImageField(null=True, blank=True, upload_to='images/')


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=200)
    email = models.EmailField()

def validate_future_date(value):
    if value < timezone.now():
        raise ValidationError("Past dates are not allowed.")

class Supplier(models.Model):
    SERVICES = (
        ('decor', 'Decor'),
        ('videography', 'Videographer'),
        ('catering', 'Catering'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=200)
    email = models.EmailField()
    service = models.CharField(max_length=200, choices=SERVICES)
    package_name = models.CharField(max_length=200)
    price = models.PositiveIntegerField(null=True)

    def __str__(self):
        return f"{self.user} ({self.service}) - Price: {self.price}"

class Package(models.Model):
    name = models.CharField(max_length=200)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Venue(models.Model):
    name = models.CharField(max_length=100)
    locality = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} ({self.locality})max capacity:{self.capacity} - Price: {self.price}"


class Events(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    attendees_expected = models.PositiveIntegerField(default=0)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=200, default='pending')
    payment_status = models.CharField(max_length=200, choices=payment_status, default="pending")
    date = models.DateTimeField(validators=[validate_future_date], default=datetime.now)
    type = models.CharField(max_length=100, choices=Event_type, default='event')
    decor_package = models.ForeignKey(Package, on_delete=models.CASCADE,
                                      limit_choices_to={'supplier__service': 'decor'}, related_name='events_with_decor', null=True, blank=True)
    catering_package = models.ForeignKey(Package, on_delete=models.CASCADE,
                                         limit_choices_to={'supplier__service': 'catering'},
                                         related_name='events_with_catering', null=True, blank=True)
    videography_package = models.ForeignKey(Package, on_delete=models.CASCADE,
                                            limit_choices_to={'supplier__service': 'videography'},
                                            related_name='events_with_videography', null=True, blank=True)
    total_price = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Equipment(models.Model):
    name = models.CharField(max_length=200)
    quantity = models.IntegerField
    status = models.CharField(choices=Equipment_availability, max_length=200)

class Staff(models.Model):
    name = models.CharField(max_length=200)
    id_number = models.IntegerField
    role = models.CharField(choices=Staff_role, max_length=250)

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

class Revenue(models.Model):
    total_revenue = models.PositiveIntegerField(default=0)
    @staticmethod
    def calculate_total_revenue():
        paid_events = Events.objects.filter(payment_status='paid')
        total_revenue = paid_events.aggregate(total=sum('total_price'))['total']
        return total_revenue or 0

    def __str__(self):
        return self.name






