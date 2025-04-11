import tensorflow as tf
import numpy as np
from keras.models import load_model
import os

# Load model from the Notebook directory
model = load_model(os.path.join(os.path.dirname(__file__), "Notebook", "corn_model_1.keras"))

def load_and_preprocess_image(image_path):
    img = tf.io.read_file(image_path)
    img = tf.image.decode_jpeg(img, channels=3)
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
        raise e

# Testing code (runs when this module is executed directly)
if __name__ == "__main__":
    image_path = os.path.join(os.path.dirname(__file__), "Notebook", "gray.png")
    prediction, confidence = predict_image(image_path)
    print(f"Predicted: {prediction} with confidence: {confidence:.2%}")