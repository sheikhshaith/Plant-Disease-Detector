import logging
from django.db import models
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated


# Get the custom user model (to allow easy reference to the user model).
User = get_user_model()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Plant(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Disease(models.Model):
    name = models.CharField(max_length=100)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name="diseases")
    image = models.ImageField(upload_to='disease_samples/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.plant.name})"


class DiseaseHistory(models.Model):
    """
    Model to track the disease history of plants for each user.
    Includes disease detection status and the plant and disease IDs.
    """
    permission_classes = [IsAuthenticated] # Ensure only authenticated users can access
    historyID = models.AutoField(primary_key=True)  # Auto-incrementing ID for disease history
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Link to the user
    plantID = models.ForeignKey(Plant, on_delete=models.CASCADE) # Identifier for the plant
    diseaseID = models.ForeignKey(Disease, on_delete=models.SET_NULL, null=True, blank=True) 
    date_detected = models.DateTimeField(auto_now_add=True)  # Timestamp when the disease is detected
    status = models.CharField(max_length=10) # Status of the disease (e.g., "active", "resolved")

    def __str__(self):
        """Return a string representation of the disease history entry."""
        return f"History {self.historyID} for User {self.user.id}"

    def save(self, *args, **kwargs):
        """Override save method to log when a DiseaseHistory is created or updated."""
        if not self.pk:  # If it's a new record
            logging.info(f"Creating DiseaseHistory for user {self.user.id} with plantID {self.plantID} and diseaseID {self.diseaseID}")
        else:  # If it's an update
            logging.info(f"Updating DiseaseHistory {self.historyID} for user {self.user.id}")
        super().save(*args, **kwargs)
                     
class FeedbackRating(models.Model):
    """
    Model to store user feedback and ratings for the plant disease detection system.
    """
    feedbackID = models.AutoField(primary_key=True) # Auto-incrementing ID for feedback
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Link to the user
    feedbackText = models.TextField() # Text of the feedback provided by the user
    rating = models.IntegerField() # Rating (e.g., 1 to 5)

    def __str__(self):
        """Return a string representation of the feedback entry."""
        return f"Feedback {self.feedbackID} by User {self.user.userID}"
    
    def save(self, *args, **kwargs):
        """Override save method to log feedback creation."""
        logging.info(f"User {self.user.id} provided feedback with rating {self.rating}")
        super().save(*args, **kwargs)

class EditHistory(models.Model):
    """
    Model to track edits made to DiseaseHistory records.
    """
    editID = models.AutoField(primary_key=True) # Auto-incrementing ID for edit history
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Link to the user who made the edit
    history = models.ForeignKey(DiseaseHistory, on_delete=models.CASCADE) # Link to the edited DiseaseHistory

    def __str__(self):
        """Return a string representation of the edit history entry."""
        return f"Edit {self.editID} by User {self.user.id}"

    def save(self, *args, **kwargs):
        """Override save method to log when an edit history record is created."""
        logging.info(f"User {self.user.id} made an edit on DiseaseHistory {self.history.historyID}")
        super().save(*args, **kwargs)

class DeleteHistory(models.Model):
    """
    Model to track deletions of DiseaseHistory records.
    """
    deleteID = models.AutoField(primary_key=True) # Auto-incrementing ID for delete history
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Link to the user who made the deletion
    history = models.ForeignKey(DiseaseHistory, on_delete=models.CASCADE) # Link to the deleted DiseaseHistory

    def __str__(self):
        """Return a string representation of the delete history entry."""
        return f"Delete {self.deleteID} by User {self.user.id}"
    
    def save(self, *args, **kwargs):
        """Override save method to log when a deletion history record is created."""
        logging.info(f"User {self.user.id} deleted DiseaseHistory {self.history.historyID}")
        super().save(*args, **kwargs)