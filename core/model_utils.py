import os
import logging
from PIL import Image, ImageStat
import torch
from torchvision import transforms
from core.model_architecture import ResNet9

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Device configuration (use GPU if available)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Class labels (for output interpretation)
classes = ['Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy', 'Blueberry___healthy', 'Cherry_(including_sour)___healthy', 'Cherry_(including_sour)___Powdery_mildew', 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_', 'Corn_(maize)___healthy', 'Corn_(maize)___Northern_Leaf_Blight', 'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___healthy', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy', 'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight', 'Potato___healthy', 'Potato___Late_blight', 'Raspberry___healthy', 'Soybean___healthy', 'Squash___Powdery_mildew', 'Strawberry___healthy', 'Strawberry___Leaf_scorch', 'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___healthy', 'Tomato___Late_blight', 'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot', 'Tomato___Tomato_mosaic_virus', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus'] # example class names

def is_image_quality_sufficient(image_path, min_resolution=(224, 224), min_brightness=40):
    """
    Validates image quality based on resolution and brightness.
    Returns True if image is usable, False otherwise.
    """
    try:
        img = Image.open(image_path)
        
        # Check resolution
        if img.size[0] < min_resolution[0] or img.size[1] < min_resolution[1]:
            logging.warning(f"Image {image_path} has insufficient resolution: {img.size}")
            return False

        # Check brightness
        stat = ImageStat.Stat(img.convert('L'))  # convert to grayscale
        brightness = stat.mean[0]
        if brightness < min_brightness:
            logging.warning(f"Image {image_path} is too dark (brightness: {brightness:.2f})")
            return False
        logging.info(f"Image {image_path} passed quality checks.")
        return True
    except Exception as e:
        logging.error(f"Failed to check image quality for {image_path}: {e}")
        return False



# Load model
def load_model():
    """
    Loads the trained model with weights and returns it in evaluation mode.
    """
    try:
        model = ResNet9(3, len(classes))
        base_dir = os.path.dirname(os.path.abspath(__file__))  # This gives the path to core/
        model_path = os.path.join(base_dir, 'model', 'plant-disease-model.pth')  # adjust if needed

        model.load_state_dict(torch.load(model_path, map_location=device))
        model.to(device)
        model.eval()
        logging.info("Model loaded successfully.")
        return model
    except Exception as e:
        logging.error(f"Failed to load model: {e}")
        raise

# Preprocess image
def preprocess_image(image_file):
    """
    Applies preprocessing transformations to the input image.
    Returns a tensor ready for model input.
    """
    try:
        transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
        ])
        image = Image.open(image_file).convert("RGB")
        image_tensor = transform(image).unsqueeze(0)  # Add batch dimension
        logging.info(f"Image {image_file} preprocessed successfully.")
        return image_tensor
    except Exception as e:
        logging.error(f"Error preprocessing image {image_file}: {e}")
        raise

# Predict function
def predict_image(image_tensor, model):
    """
    Runs inference on the preprocessed image tensor.
    Returns the predicted class label.
    """
    try:
        image_tensor = image_tensor.to(device)
        outputs = model(image_tensor)
        _, predicted = torch.max(outputs, 1)
        predicted_class = classes[predicted.item()]
        logging.info(f"Prediction completed: {predicted_class}")
        return predicted_class
    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        return None


def parse_prediction(prediction):
    """
    Parses prediction string into crop and disease components.
    Example: 'Apple___Black_rot' -> {'crop': 'Apple', 'disease': 'Black Rot'}
    """
    if not prediction:
        return {"crop": "-", "disease": "-"}
    
    try:
        # Split prediction string into crop and disease
        parts = prediction.split("___")
        crop = parts[0] if parts[0] else "-"
        disease_raw = parts[1] if len(parts) > 1 else "-"
        
        # Format disease (capitalize the first letter of each word and replace underscores)
        disease = disease_raw.replace("_", " ").title() if disease_raw != "-" else "-"
        
        return {
            "crop": crop,
            "disease": disease
        }
    except Exception as e:
        logging.error(f"Error parsing prediction string '{prediction}': {e}")
        return {"crop": "-", "disease": "-"}

