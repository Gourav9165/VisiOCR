from django.db import models

# Create your models here.
class OCR_data(models.Model):
    pass_id = models.AutoField(primary_key=True)
    id_type = models.CharField(max_length=20)
    text = models.CharField(max_length=100)

class OCR_store(models.Model):
    id = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=50, null=True, blank=True)
    Father_name = models.CharField(max_length=50, null=True, blank=True)
    Gender = models.CharField(max_length=10, null=True, blank=True)
    DOB = models.DateField(null=True, blank=True)
    Aadhaar_no = models.CharField(max_length=20, null=True, blank=True)
    Pan_no = models.CharField(max_length=20, null=True, blank=True)
    Phone_no = models.CharField(max_length=10, null=True, blank=True)
    Expiry_time = models.CharField(max_length=20, null=True, blank=True)