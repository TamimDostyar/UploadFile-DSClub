#!/usr/bin/env python
"""
Script to check if the ML model exists and can be loaded properly.
Run this script to diagnose model loading issues.
"""

import os
import sys
import traceback

def check_model():
    print("Checking ML model...")
    
    # Check if TensorFlow and Keras are installed
    try:
        import tensorflow as tf
        from keras.models import load_model
        print(f"TensorFlow version: {tf.__version__}")
        print(f"Keras version: {tf.keras.__version__}")
    except ImportError as e:
        print(f"Error: Could not import TensorFlow or Keras: {e}")
        print("Please install the required packages with: pip install tensorflow")
        return False
        
    # Get current directory and project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # Define possible model paths to check
    model_paths = [
        os.path.join(current_dir, "Notebook", "corn_model_1.keras"),
        os.path.join(project_root, "upload", "Notebook", "corn_model_1.keras"),
        os.path.join(os.getcwd(), "upload", "Notebook", "corn_model_1.keras"),
    ]
    
    # Check each path
    found_path = None
    for path in model_paths:
        if os.path.exists(path):
            print(f"Model file found at: {path}")
            found_path = path
            break
    
    if not found_path:
        print("Error: Model file not found in any of these locations:")
        for path in model_paths:
            print(f"  - {path}")
        return False
    
    # Try to load the model
    try:
        print(f"Attempting to load model from {found_path}...")
        model = load_model(found_path)
        print("✅ Model loaded successfully!")
        
        # Print model summary
        print("\nModel Summary:")
        model.summary()
        
        return True
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("\nFull traceback:")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = check_model()
    if success:
        print("\n✅ Model check completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Model check failed")
        sys.exit(1) 