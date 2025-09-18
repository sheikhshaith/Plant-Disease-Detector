#  Plant Disease Detector

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-4.2-brightgreen.svg)](https://www.djangoproject.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0-orange.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A deep learning-powered web application that helps identify plant diseases from images. Built with Django and PyTorch, this system can detect various plant diseases with high accuracy and provide detailed analysis reports.

##  Features

- **Image-based Disease Detection**: Upload images of plant leaves to detect diseases
- **Multiple Plant Support**: Works with various plant species
- **Detailed Reports**: Get comprehensive analysis including disease information and treatment suggestions
- **User History**: Track your previous detections and results
- **Email Notifications**: Receive detailed reports via email
- **Responsive API**: Easy integration with other applications

##  Tech Stack

- **Backend**: Django REST Framework
- **Machine Learning**: PyTorch
- **Model**: Custom ResNet9 architecture
- **Database**: SQLite (configurable to PostgreSQL/MySQL)
- **Frontend**: HTML, CSS, JavaScript (for admin interface)
- **Deployment**: Docker support included

##  Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual Environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/plant-disease-detector.git
   cd plant-disease-detector
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - API: http://127.0.0.1:8000/api/
   - Admin: http://127.0.0.1:8000/admin/

##  API Documentation

### Endpoints

- `POST /api/predict/` - Upload an image for disease detection
- `GET /api/disease-history/` - View detection history
- `POST /api/feedback/` - Submit feedback
- `GET /api/crops/` - List available plants and diseases

### Example Request

```bash
curl -X POST -F "image=@path_to_image.jpg" http://127.0.0.1:8000/api/predict/
```

##  Model Details

The application uses a custom ResNet9 architecture trained on a dataset of plant disease images. The model can identify multiple diseases across various plant species with high accuracy.

### Supported Plants and Diseases

- **Tomato**: Early Blight, Late Blight, Leaf Mold, etc.
- **Potato**: Early Blight, Late Blight
- **Corn**: Cercospora Leaf Spot, Common Rust
- And more...

## 📦 Deployment

The application can be deployed using Docker:

```bash
docker-compose up --build
```

For production deployment, it's recommended to use:
- Gunicorn/Uvicorn as the application server
- Nginx as the reverse proxy
- PostgreSQL as the database
- Redis for caching (optional)

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- Dataset: [PlantVillage Dataset](https://plantvillage.psu.edu/)
- Special thanks to all contributors and open-source projects that made this possible.

## Contact

For any queries or suggestions, please open an issue or contact the maintainers.
# Plant-Disease-Detector
