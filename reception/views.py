from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from .models import  *
from .serializers import VisitorSerializer, LetterSerializer
from rest_framework.views import APIView
from django.core.mail import send_mail
# Create your views here.

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

def send_letter(request, visitor_id):
# Sends a welcome email to a visitor."""
    visitor = Visitor.objects.get(pk=visitor_id)
    subject = 'Welcome to [Your Company Name]'
    message = f"Dear {visitor.name},\n\nThank you for visiting us. We appreciate your interest in [Your Company Name].\n\nSincerely,\n[Your Company Name]"
    from_email = 'your_email@example.com'
    recipient_list = [visitor.email]
    send_mail(subject, message, from_email, recipient_list)
    return Response({'message': 'Letter sent successfully'}, status=status.HTTP_200_OK)


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