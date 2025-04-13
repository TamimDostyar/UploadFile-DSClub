import tensorflow as tf
import numpy as np
from keras.models import load_model
import os
from PIL import Image

# Load model from the Notebook directory
model = load_model(os.path.join(os.path.dirname(__file__), "Notebook", "corn_model_1.keras"))

def load_and_preprocess_image(image_path):
    try:
        # Use PIL for more robust image loading
        with Image.open(image_path) as img:
            img = img.convert('RGB')  # Convert to RGB to handle all image types
            img = img.resize((224, 224))
            img_array = np.array(img) / 255.0
            return tf.convert_to_tensor(img_array)
    except Exception as e:
        print(f"Error loading image with PIL: {str(e)}")
        # Fall back to TensorFlow method if PIL fails
        img = tf.io.read_file(image_path)
        # Try to determine format automatically
        img = tf.image.decode_image(img, channels=3)
        img = tf.image.resize(img, (224, 224))
        img = img / 255.0
        return img

def predict_image(image_path):
    """
    Process an uploaded image through the corn disease classification model
    
    Args:
        image_path: Path to the uploaded image file
        
    Returns:
        (str, float): A tuple containing predicted class label and confidence score
    """
    try:
        # Preprocess the image
        image = load_and_preprocess_image(image_path)
        image = tf.expand_dims(image, axis=0)
        
        # Make prediction
        preds = model.predict(image)
        
        # Get class with highest probability
        predicted_class = np.argmax(preds, axis=1)[0]
        confidence = float(preds[0][predicted_class])
        
        # Map to class labels
        class_labels = {0: "blight", 1: "common_rust", 2: "gray_leaf_spot", 3: "healthy"}
        prediction = class_labels.get(predicted_class, "Unknown")
        
        return prediction, confidence
        
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        # Instead of raising the exception, return a default value
        return "Error processing image", 0.0

# Testing code (runs when this module is executed directly)
if __name__ == "__main__":
    image_path = os.path.join(os.path.dirname(__file__), "Notebook", "gray.png")
    prediction, confidence = predict_image(image_path)
    print(f"Predicted: {prediction} with confidence: {confidence:.2%}")