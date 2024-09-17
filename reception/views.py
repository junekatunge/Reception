from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import status
from .models import  *
from .serializers import VisitorSerializer, LetterSerializer
from django.core.mail import send_mail,EmailMessage
import logging
from django.shortcuts import get_object_or_404
from email import message_from_string
from django.core.files.base import ContentFile
from django.http import HttpResponse
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
# Create your views here.

def test_email(request):
    send_mail(
        'Test Email',  # Subject
        'This is a test email from Django using Gmail.',  # Message
        'jkatunge13@gmail.com',  # From email
        ['jkatunge13@gmail.com'],  # To email
        fail_silently=False,  # Raise an exception if it fails
    )
    return HttpResponse("Test email sent successfully!")


class VisitorListView(ListCreateAPIView):
    """Handles listing and creating visitors."""
    queryset = Visitor.objects.all()
    serializer_class = VisitorSerializer
    
class VisitorDetailView(RetrieveUpdateDestroyAPIView):
    """Handles retrieving, updating, and deleting a single visitor."""
    queryset = Visitor.objects.all()
    serializer_class = VisitorSerializer
    lookup_field = 'pk'  

# def send_letter(request, visitor_id):
# # Sends a welcome email to a visitor."""
#     visitor = Visitor.objects.get(pk=visitor_id)
#     subject = 'Welcome to [Your Company Name]'
#     message = f"Dear {visitor.name},\n\nThank you for visiting us. We appreciate your interest in [Your Company Name].\n\nSincerely,\n[Your Company Name]"
#     from_email = 'your_email@example.com'
#     recipient_list = [visitor.email]
#     send_mail(subject, message, from_email, recipient_list)
#     return Response({'message': 'Letter sent successfully'}, status=status.HTTP_200_OK)


# Setting up logging to capture errors and other relevant information
logger = logging.getLogger(__name__)
# Helper function to handle email sending
def send_email(subject, content, from_email, recipient_list, attachment=None):
    """
    Sends an email, optionally with an attachment.
    
    Args:
        subject (str): Subject of the email.
        content (str): Content/body of the email.
        from_email (str): Sender's email address.
        recipient_list (list): List of recipient email addresses.
        attachment (File, optional): Optional attachment to send with the email.
    
    Returns:
        bool: True if the email was sent successfully, False if it failed.
    """
    try:
        if attachment:
            # Create an EmailMessage object with the attachment
            email = EmailMessage(subject, content, from_email, recipient_list)
            email.attach(attachment.name, attachment.read(), attachment.content_type)
            email.send()  # Send the email with attachment
        else:
            # Send email without attachment
            send_mail(subject, content, from_email, recipient_list)
        return True
    except Exception as e:
        # Log any error that occurs during the email sending process
        logger.error(f"Failed to send email: {str(e)}")
        return False

# Helper function to save an attachment to the database
def save_attachment(letter, attachment):
    """
    Saves an attachment to the letter instance.
    
    Args:
        letter (Letter): The letter object to which the attachment will be saved.
        attachment (File): The uploaded file to save as an attachment.
    """
    try:
        # Save the uploaded file as an attachment to the letter model
        letter.attachment.save(attachment.name, attachment, save=True)
    except Exception as e:
        # Log any error that occurs during attachment saving
        logger.error(f"Failed to save attachment: {str(e)}")

# View function to handle sending a letter
def send_letter(request, visitor_id):
    """
    Sends a letter to a visitor and optionally attaches a file.
    
    Args:
        request: The HTTP request object.
        visitor_id (int): The ID of the visitor to whom the letter is being sent.
    
    Returns:
        Response: A DRF Response object with a success or error message.
    """
    # Fetch the visitor by ID or return 404 if not found
    visitor = get_object_or_404(Visitor, pk=visitor_id)
    
    # Handle POST requests only
    if request.method == 'POST':
        # Extract email data from the request
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        from_email = 'your_email@example.com'  # Use a valid email address
        recipient_list = [visitor.email]  # Send email to the visitor's email
        attachment = request.FILES.get('attachment')  # Get attachment if uploaded

        # Try to send the email
        if send_email(subject, content, from_email, recipient_list, attachment):
            # If email is sent successfully, create a letter record in the database
            letter = Letter.objects.create(visitor=visitor, subject=subject, content=content, is_sent=True)
            if attachment:
                # Save the attachment if present
                save_attachment(letter, attachment)
            return Response({'message': 'Letter sent successfully'}, status=status.HTTP_200_OK)
        else:
            # Return an error response if the email fails to send
            return Response({'error': 'Failed to send the email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handle invalid request methods (only POST is allowed)
    return Response({'error': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)

# View function to handle receiving a letter
def receive_letter(request, visitor_id):
    """
    Receives a letter from a visitor and processes optional attachments.
    
    Args:
        request: The HTTP request object.
        visitor_id (int): The ID of the visitor sending the letter.
    
    Returns:
        Response: A DRF Response object with a success or error message.
    """
    # Fetch the visitor by ID or return 404 if not found
    visitor = get_object_or_404(Visitor, pk=visitor_id)
    
    # Handle POST requests only
    if request.method == 'POST':
        # Extract data from the request
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        raw_email = request.POST.get('raw_email')  # Raw email content

        # Create a letter object in the database
        letter = Letter.objects.create(visitor=visitor, subject=subject, content=content, is_sent=False)

        # If there's a raw email, process the attachments from it
        if raw_email:
            email_message = message_from_string(raw_email)  # Convert the raw email into an email message object
            process_attachments(email_message, letter)  # Process any attachments in the email

        return Response({'message': 'Letter received successfully'}, status=status.HTTP_200_OK)

    # Handle invalid request methods (only POST is allowed)
    return Response({'error': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)

# Helper function to process attachments from an email
def process_attachments(email_message, letter):
    """
    Extracts and saves attachments from an email message to a letter.
    
    Args:
        email_message (Message): The parsed email message object.
        letter (Letter): The letter object to which attachments will be saved.
    """
    try:
        # Iterate through the parts of the email to find attachments
        for part in email_message.walk():
            # Skip multipart sections (we only care about the actual attachments)
            if part.get_content_maintype() == 'multipart':
                continue
            # Skip parts without a 'Content-Disposition' (not an attachment)
            if part.get('Content-Disposition') is None:
                continue
            filename = part.get_filename()  # Get the filename of the attachment
            if filename:
                # Decode and save the attachment content
                attachment_content = part.get_payload(decode=True)
                attachment_file = ContentFile(attachment_content)
                # Save the attachment file to the storage
                attachment_path = default_storage.save(f'letter_attachments/{filename}', attachment_file)
                # Assign the attachment to the letter and save
                letter.attachment = attachment_path
                letter.save()
    except Exception as e:
        # Log any error that occurs during attachment processing
        logger.error(f"Failed to process attachments: {str(e)}")



class LetterPagination(PageNumberPagination):
    """Custom pagination class to define default page size and other settings."""
    page_size = 10  # Default number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100

class LetterListView(ListCreateAPIView):
    """Handles listing and creating letters."""
    queryset = Letter.objects.all()
    serializer_class = LetterSerializer
    pagination_class = LetterPagination  # Use custom pagination
    filter_backends = [OrderingFilter, SearchFilter]  # Enable filtering and ordering
    ordering_fields = ['sent_at', 'subject']  # Allow ordering by these fields
    search_fields = ['subject', 'content']  # Allow searching by these fields
    
class LetterDetailView(RetrieveUpdateDestroyAPIView):
    """Handles retrieving, updating, and deleting a specific letter."""
    queryset = Letter.objects.all()
    serializer_class = LetterSerializer