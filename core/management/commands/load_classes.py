from django.core.management.base import BaseCommand
from core.models import Plant, Disease

def parse_prediction(prediction):
    """
    Parses prediction string into crop and disease components.
    Example: 'Apple___Black_rot' -> {'crop': 'Apple', 'disease': 'Black Rot'}
    """

    # Split prediction string into crop and disease
    parts = prediction.split("___")
    crop = parts[0] if parts[0] else "-"
    disease_raw = parts[1] if len(parts) > 1 else "-"
    
    # Format disease (capitalize the first letter of each word and replace underscores)
    disease = disease_raw.replace("_", " ").title() if disease_raw != "-" else "-"

    return crop, disease

class Command(BaseCommand):
    help = 'Load plant and disease classes into the database'

    def handle(self, *args, **kwargs):
        classes = [
            'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
            'Blueberry___healthy', 'Cherry_(including_sour)___healthy', 'Cherry_(including_sour)___Powdery_mildew',
            'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_',
            'Corn_(maize)___healthy', 'Corn_(maize)___Northern_Leaf_Blight', 'Grape___Black_rot',
            'Grape___Esca_(Black_Measles)', 'Grape___healthy', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
            'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy',
            'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight',
            'Potato___healthy', 'Potato___Late_blight', 'Raspberry___healthy', 'Soybean___healthy',
            'Squash___Powdery_mildew', 'Strawberry___healthy', 'Strawberry___Leaf_scorch',
            'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___healthy', 'Tomato___Late_blight',
            'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite',
            'Tomato___Target_Spot', 'Tomato___Tomato_mosaic_virus', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus'
        ]

        for class_name in classes:
            plant_name, disease_name = parse_prediction(class_name)
            plant, _ = Plant.objects.get_or_create(name=plant_name)
            Disease.objects.get_or_create(name=disease_name, plant=plant)

        self.stdout.write(self.style.SUCCESS('Successfully loaded plant and disease classes.'))


