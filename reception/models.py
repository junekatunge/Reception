from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Visitor(models.Model):
    name = models.CharField(max_length=100)  # Visitor's name
    email = models.EmailField(blank=True, null=True)# Optional email address
    phone = models.CharField(max_length=20, blank=True, null=True)# Optional phone number
    purpose = models.CharField(max_length=255) # Reason for the visit
    arrival_time = models.DateTimeField(auto_now_add=True)# Time of arrival
    departure_time = models.DateTimeField(blank=True, null=True) # Time of departure

    def __str__(self):
        return self.name # Return the visitor's name for representation
    
class Letter(models.Model):
    """Represents a letter sent or received."""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_letters', null=True, blank=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_letters', null=True, blank=True)
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='letters')
    subject = models.CharField(max_length=255)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)  # True if sent, False if received
    attachment = models.FileField(upload_to='letter_attachments/', blank=True, null=True)  # Added attachment field

    def __str__(self):
        return f"{self.subject} - {self.visitor.name}"
    
