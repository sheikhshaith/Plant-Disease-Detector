from django.urls import path
from .views import *

urlpatterns = [
    # Predict Image View
    # Route to handle the image prediction process. 
    # Accepts an image upload and returns the prediction 
    # for the plant's health condition and disease.
    path('predict/', PredictImageView.as_view(), name='predict-image'),
    
    # Disease History Views
    # Route to list all disease history records or create a new disease history record.
    # GET: List all records.
    # POST: Create a new disease history record.
    path('disease-history/', DiseaseHistoryListCreateAPIView.as_view(), name='disease-history-list'),
    
    # Route to view, update, or delete a specific disease history record.
    # GET: Retrieve a disease history record by its primary key (pk).
    # PUT: Update a disease history record.
    # DELETE: Delete a disease history record.
    path('disease-history/<int:pk>/', DiseaseHistoryDetailAPIView.as_view(), name='disease-history-detail'),

    # Feedback Rating Views
    # Route to list all feedback ratings or create a new feedback rating.
    # GET: List all feedback ratings.
    # POST: Create a new feedback rating.
    path('feedback/', FeedbackRatingListCreateAPIView.as_view(), name='feedback-list'),
    
    # Route to view, update, or delete a specific feedback rating.
    # GET: Retrieve a feedback rating by its primary key (pk).
    # PUT: Update a feedback rating.
    # DELETE: Delete a feedback rating.
    path('feedback/<int:pk>/', FeedbackRatingDetailAPIView.as_view(), name='feedback-detail'),

    # Edit History Views
    # Route to list all edit history records or create a new edit history record.
    # GET: List all edit history records.
    # POST: Create a new edit history record.
    path('edit-history/', EditHistoryListCreateAPIView.as_view(), name='edit-history-list'),
    
    # Route to view or delete a specific edit history record.
    # GET: Retrieve an edit history record by its primary key (pk).
    # DELETE: Delete an edit history record.
    path('edit-history/<int:pk>/', EditHistoryDetailAPIView.as_view(), name='edit-history-detail'),

    # Delete History Views
    # Route to list all delete history records or create a new delete history record.
    # GET: List all delete history records.
    # POST: Create a new delete history record.
    path('delete-history/', DeleteHistoryListCreateAPIView.as_view(), name='delete-history-list'),
    
    # Route to view or delete a specific delete history record.
    # GET: Retrieve a delete history record by its primary key (pk).
    # DELETE: Delete a delete history record.
    path('delete-history/<int:pk>/', DeleteHistoryDetailAPIView.as_view(), name='delete-history-detail'),

    path('crop-library/', CropLibraryListAPIView.as_view(), name='disease-sample-list'),
]
