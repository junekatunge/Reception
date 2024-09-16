from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from .models import  *
from .serializers import VisitorSerializer, LetterSerializer
from rest_framework.views import APIView
from django.core.mail import send_mail,EmailMessage
import logging
from django.shortcuts import get_object_or_404
from email import message_from_string
from django.core.files.base import ContentFile
from django.http import HttpResponse
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


class VisitorListView(APIView):
    #handles retrieving guests and creating guests in generaal 
    def get(self,request):
        #retrieve a list of all visitors
        visitors = Visitor.objects.all()
        serializer = VisitorSerializer(visitors, many=True)
        return Response(serializer.data)
    
    def post(self,request):
        #create a new visitor record
        serializer = VisitorSerializer(data =request.data)
        if serializer.is_valid():
            serializer.save() # Save the new visitor to the database
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class VisitorDetailView(APIView):
        #Handles retrieving, updating, and deleting individual visitors.
    
    def get_object(self, pk):
        # Retrieves a visitor by its primary key (ID).
        try:
            return Visitor.objects.get(pk=pk)
        except Visitor.DoesNotExist:
            return None

    def get(self, request, pk):
        #Retrieves details of a specific visitor.
        visitor = self.get_object(pk)
        if visitor is not None:
            serializer = VisitorSerializer(visitor)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        #Updates the details of a specific visitor.
        visitor = self.get_object(pk)
        if visitor is not None:
            serializer = VisitorSerializer(visitor, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        # Deletes a specific visitor.
        visitor = self.get_object(pk)
        if visitor is not None:
            visitor.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

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


class LetterListView(APIView):
    """Handles listing and creating letters."""

    def get(self, request):
        """Retrieves a list of all letters."""
        letters = Letter.objects.all()
        serializer = LetterSerializer(letters, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Creates a new letter record."""
        serializer = LetterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LetterDetailView(APIView):
   
    def get_object(self, pk):
        # Retrieves a letter by its primary key (ID).
        try:
            return Letter.objects.get(pk=pk)
        except Letter.DoesNotExist:
            return None

    def get(self, request, pk):
        # Retrieves details of a specific letter.
        letter = self.get_object(pk)
        if letter is not None:
            serializer = LetterSerializer(letter)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        # Updates the details of a specific letter.
        letter = self.get_object(pk)
        if letter is not None:
            serializer = LetterSerializer(letter, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        # Deletes a specific letter.
        letter = self.get_object(pk)
        if letter is not None:
            letter.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)