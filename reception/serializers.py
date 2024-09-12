from rest_framework import serializers
from .models import *

class VisitorSerializer(serializers.ModelSerializer):
        """Serializes Visitor data for API interaction."""
    
        class Meta:
            model = Visitor
            fields = '__all__'  # Include all fields from the Visitor model
            
            
class LetterSerializer(serializers.ModelSerializer):
   
        class Meta:
            model = Letter
            fields = '__all__'
    