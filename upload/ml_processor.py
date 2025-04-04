import os
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow import keras
import os.path
import sys
from download_model import download_model


# Define class labels based on the model
CLASS_LABELS = {
    0: "Bacterial Leaf Blight", 
    1: "Brown Spot", 
    2: "Leaf Blast", 
    3: "Healthy"
}
# Get the absolute path to the model to avoid any path resolution issues
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "Notebook", "corn_model_1.keras")
model = None

def load_model_if_needed():
    global model
    if model is None:
        try:
            print(f"Loading model from: {MODEL_PATH}")
            print(f"File exists: {os.path.exists(MODEL_PATH)}")
            
            # Use tensorflow.keras directly instead of importing from keras
            model = tf.keras.models.load_model(MODEL_PATH)
            print("Model loaded successfully")
        except Exception as e:
            error_msg = f"Failed to load the model: {str(e)}"
            print(error_msg, file=sys.stderr)
            # Provide alternative model paths to try
            alt_paths = [
                os.path.join(os.path.dirname(BASE_DIR), "upload", "Notebook", "corn_model_1.keras"),
                os.path.join(os.getcwd(), "upload", "Notebook", "corn_model_1.keras")
            ]
            
            # Try alternative paths if the main path fails
            for alt_path in alt_paths:
                try:
                    print(f"Trying alternative path: {alt_path}")
                    if os.path.exists(alt_path):
                        model = tf.keras.models.load_model(alt_path)
                        print(f"Model loaded from alternative path: {alt_path}")
                        return
                except Exception as alt_e:
                    print(f"Failed to load from {alt_path}: {str(alt_e)}")
            
            raise RuntimeError(error_msg)

def preprocess_image(image_path, target_size=(224, 224)):
    """
    Preprocess image for model prediction
    """
    try:
        img = Image.open(image_path)
        img = img.resize(target_size)
        img = np.array(img) / 255.0  # Normalize to [0,1]
        return np.expand_dims(img, axis=0)  # Add batch dimension
    except Exception as e:
        raise ValueError(f"Error preprocessing image: {str(e)}")

def predict_image(image_path):
    """
    Process an uploaded image using the trained model and return the prediction and confidence.
    
    Args:
        image_path (str): Path to the uploaded image file
        
    Returns:
        tuple: (prediction, confidence) where prediction is a string and confidence is a float 0-1
    """
    # Check if the file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found at {image_path}")
    
    # Load the model if it's not already loaded
    load_model_if_needed()
    
    # Preprocess the image
    preprocessed_img = preprocess_image(image_path)
    
    # Make prediction
    predictions = model.predict(preprocessed_img)
    
    # Get the class with highest probability
    predicted_class_idx = np.argmax(predictions[0])
    confidence = float(predictions[0][predicted_class_idx])
    
    # Get the class label
    prediction = CLASS_LABELS.get(predicted_class_idx, "Unknown")
    
    return prediction, confidence
