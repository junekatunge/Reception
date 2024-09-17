from . import views 
from django.urls import path
from .views import test_email

urlpatterns = [
    path('api/visitors/',views.VisitorListView.as_view(),name = 'visitor-list'),# List and create visitors
    path('api/visitors/<int:pk>/',views.VisitorDetailView.as_view(),name = 'visitor-detail'),# Retrieve, update, delete individual visitors
    path('api/visitors/<int:visitor_id>/send_email/', views.send_letter, name='sendletter'),
    #for letters
    path('api/letters/', views.LetterListView.as_view(), name='letter-list'),
    path('api/letters/<int:pk>/', views.LetterDetailView.as_view(), name='letter-detail'),
    path('send-test-email/', test_email, name='test_email'),

]
