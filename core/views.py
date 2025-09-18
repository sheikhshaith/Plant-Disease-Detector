import os
import logging
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.files.storage import default_storage

from .email_utils import send_detection_report_email
from .models import *
from .serializers import *
from .model_utils import *

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the plant disease detection model
model = load_model()

class PredictImageView(APIView):
    """
    View for predicting plant disease from an uploaded image.
    - Validates image format and quality
    - Predicts the disease and sends an email report
    """
    def post(self, request, format=None):
        serializer = ImageUploadSerializer(data=request.data)

        # Validate image upload
        if serializer.is_valid():
            image = serializer.validated_data['image']

            # Save the uploaded image
            filename = default_storage.save(f"detection/{image.name}", image)
            image_path = os.path.join(settings.MEDIA_ROOT, filename)
            image_url = request.build_absolute_uri(settings.MEDIA_URL + filename)

            # Check the quality of the uploaded image
            if not is_image_quality_sufficient(image_path):
                logging.warning(f"Image quality insufficient: {image.name}")
                return Response(
                    {"error": "Image quality insufficient, please upload a clearer image."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Process the image and predict the disease
            try:
                img_tensor = preprocess_image(image_path)
                prediction = predict_image(img_tensor, model)

                # Parse the prediction into crop and disease
                parsed_prediction = parse_prediction(prediction)
                crop = parsed_prediction["crop"]
                disease = parsed_prediction["disease"]

                # Determine health status based on the prediction
                if disease == "Healthy":
                    health_status = "Healthy"
                    disease_name = None
                    message = "The plant is healthy."
                elif disease == "Unknown":
                    health_status = "Unhealthy"
                    disease_name = None
                    message = "The plant is not healthy, but the disease could not be identified."
                else:
                    health_status = "Unhealthy"
                    disease_name = disease
                    message = f"The plant is not healthy and is affected by {disease}."

                try:
                    plant = Plant.objects.get(name=crop)
                except Plant.DoesNotExist:
                    logging.error(f"Plant not found in DB: {crop}")
                    return Response({"error": f"Plant '{crop}' not found in database."}, status=404)
                
                if disease_name:
                    try:
                        disease_obj = Disease.objects.get(name=disease_name, plant=plant)
                    except Disease.DoesNotExist:
                        logging.error(f"Disease '{disease_name}' not found for plant '{plant.name}'")
                        return Response({"error": f"Disease '{disease_name}' not found for plant '{plant.name}'."}, status=404)
                else:
                    disease_obj = None  # If healthy or unknown

                # Save the disease detection history to the database
                DiseaseHistory.objects.create(
                    user=request.user,
                    plantID=plant, 
                    diseaseID=disease_obj,
                    status=health_status,
                )
                # Send email with detection results
                try:
                    send_detection_report_email(
                        user=request.user,
                        crop=crop,
                        disease_name=disease_name,
                        health_status=health_status,
                        message=message,
                        image_url=image_url
                    )
                except Exception as e:
                    logging.error(f"Failed to send detection email: {str(e)}")

                # Return the prediction result as a response
                return Response({
                    'condition_status': health_status,
                    'crop':crop,
                    'disease_name': disease_name,
                    'prediction_raw': prediction,
                    'message': message,
                    'image_url': image_url
                })

            except Exception as e:
                logging.error(f"Error during prediction: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # If the serializer is invalid, return the errors
        logging.warning(f"Invalid image upload: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---- DiseaseHistory ----
class DiseaseHistoryListCreateAPIView(APIView):
    """
    List and create disease history records.
    """
    def get(self, request):
        records = DiseaseHistory.objects.all()
        serializer = DiseaseHistorySerializer(records, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DiseaseHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logging.info(f"Created new disease history record: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logging.warning(f"Failed to create disease history: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DiseaseHistoryDetailAPIView(APIView):
    """
    View, update, or delete a specific disease history record.
    """
    def get(self, request, pk):
        record = get_object_or_404(DiseaseHistory, pk=pk)
        serializer = DiseaseHistorySerializer(record)
        return Response(serializer.data)

    def put(self, request, pk):
        record = get_object_or_404(DiseaseHistory, pk=pk)
        serializer = DiseaseHistorySerializer(record, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logging.info(f"Updated disease history record {pk}: {serializer.data}")
            return Response(serializer.data)
        logging.warning(f"Failed to update disease history {pk}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        record = get_object_or_404(DiseaseHistory, pk=pk)
        record.delete()
        logging.info(f"Deleted disease history record {pk}")
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---- FeedbackRating ----
class FeedbackRatingListCreateAPIView(APIView):
    """
    List and create feedback ratings.
    """
    def get(self, request):
        feedbacks = FeedbackRating.objects.all()
        serializer = FeedbackRatingSerializer(feedbacks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FeedbackRatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logging.info(f"Created feedback rating: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logging.warning(f"Failed to create feedback rating: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedbackRatingDetailAPIView(APIView):
    """
    View, update, or delete a specific feedback rating.
    """
    def get(self, request, pk):
        feedback = get_object_or_404(FeedbackRating, pk=pk)
        serializer = FeedbackRatingSerializer(feedback)
        return Response(serializer.data)

    def put(self, request, pk):
        feedback = get_object_or_404(FeedbackRating, pk=pk)
        serializer = FeedbackRatingSerializer(feedback, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logging.info(f"Updated feedback rating {pk}: {serializer.data}")
            return Response(serializer.data)
        logging.warning(f"Failed to update feedback rating {pk}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        feedback = get_object_or_404(FeedbackRating, pk=pk)
        feedback.delete()
        logging.info(f"Deleted feedback rating {pk}")
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---- EditHistory ----
class EditHistoryListCreateAPIView(APIView):
    """
    List and create edit history records.
    """
    def get(self, request):
        edits = EditHistory.objects.all()
        serializer = EditHistorySerializer(edits, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EditHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logging.info(f"Created edit history: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logging.warning(f"Failed to create edit history: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditHistoryDetailAPIView(APIView):
    """
    View or delete a specific edit history record.
    """
    def get(self, request, pk):
        edit = get_object_or_404(EditHistory, pk=pk)
        serializer = EditHistorySerializer(edit)
        return Response(serializer.data)

    def delete(self, request, pk):
        edit = get_object_or_404(EditHistory, pk=pk)
        edit.delete()
        logging.info(f"Deleted edit history record {pk}")
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---- DeleteHistory ----
class DeleteHistoryListCreateAPIView(APIView):
    """
    List and create delete history records.
    """
    def get(self, request):
        deletes = DeleteHistory.objects.all()
        serializer = DeleteHistorySerializer(deletes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DeleteHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logging.info(f"Created delete history: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logging.warning(f"Failed to create delete history: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteHistoryDetailAPIView(APIView):
    """
    View or delete a specific delete history record.
    """
    def get(self, request, pk):
        delete = get_object_or_404(DeleteHistory, pk=pk)
        serializer = DeleteHistorySerializer(delete)
        return Response(serializer.data)

    def delete(self, request, pk):
        delete = get_object_or_404(DeleteHistory, pk=pk)
        delete.delete()
        logging.info(f"Deleted delete history record {pk}")
        return Response(status=status.HTTP_204_NO_CONTENT)

class CropLibraryListAPIView(APIView):
    """
    API to list plant names, disease names, and sample images.
    """
    def get(self, request):
        diseases = Disease.objects.all()
        serializer = CropLibrarySerializer(diseases, many=True, context={'request': request})
        return Response(serializer.data)
