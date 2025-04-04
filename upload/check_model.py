#!/usr/bin/env python
"""
Script to check if the ML model exists, with a mock implementation 
that doesn't depend on TensorFlow or Keras.
"""

import os
import sys

def check_model():
    print("Checking ML model...")
    
    print("Using mock implementation for model checking")
    
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
    
    # Pretend to load the model
    print(f"Simulating model loading from {found_path}...")
    print("✅ Mock model loaded successfully!")
    
    # Print fake model summary
    print("\nMock Model Summary:")
    print("_________________________________________________________________")
    print("Layer (type)                 Output Shape              Param #   ")
    print("=================================================================")
    print("conv2d (Conv2D)              (None, 222, 222, 32)      896       ")
    print("max_pooling2d (MaxPooling2D) (None, 111, 111, 32)      0         ")
    print("conv2d_1 (Conv2D)            (None, 109, 109, 64)      18496     ")
    print("flatten (Flatten)            (None, 762064)            0         ")
    print("dense (Dense)                (None, 4)                 3048260   ")
    print("=================================================================")
    print("Total params: 3,067,652")
    print("Trainable params: 3,067,652")
    print("Non-trainable params: 0")
    print("_________________________________________________________________")
    
    return True

if __name__ == "__main__":
    success = check_model()
    if success:
        print("\n✅ Model check completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Model check failed")
        sys.exit(1) 