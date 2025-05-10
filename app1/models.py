from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class employeedata(models.Model):
    fname = models.CharField(max_length=1400)
    lname = models.CharField(max_length=10)
    phone = models.TextField()
    amount = models.DecimalField(decimal_places=2, max_digits=10)

class Advocate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100, null=False)  # Ensure this field exists

    def __str__(self):
        return self.name

class Appointment(models.Model):

    advocate = models.ForeignKey(Advocate, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField()

    def __str__(self):
        return f"{self.client_name} - {self.appointment_date} @ {self.appointment_time}"

