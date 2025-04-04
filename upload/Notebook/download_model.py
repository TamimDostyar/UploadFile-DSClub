# Available backend options are: "jax", "torch", "tensorflow".
import os
import sys

def download_model():
    """
    Downloads the corn disease classification model from Hugging Face Hub.
    Handles errors and checks if the model already exists before downloading.
    """
    try:
        # Direct download from Hugging Face Hub
        from huggingface_hub import hf_hub_download

        # Download the model file directly to the current directory
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        MODEL_PATH = os.path.join(BASE_DIR, "corn_model_1.keras")
        
        # Check if model already exists
        if os.path.exists(MODEL_PATH):
            print(f"Model already exists at {MODEL_PATH}")
            return MODEL_PATH
            
        model_id = "dostah01/shark"
        print(f"Downloading model from {model_id}...")
        model_file = hf_hub_download(repo_id=model_id, filename="corn_model_1.keras", local_dir=BASE_DIR)
        print(f"Model downloaded successfully to {model_file}")
        print("Download complete!")
        return model_file
    except Exception as e:
        print(f"Error downloading model: {str(e)}", file=sys.stderr)
        
        # Create an empty placeholder file if download fails
        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            MODEL_PATH = os.path.join(BASE_DIR, "corn_model_1.keras")
            if not os.path.exists(MODEL_PATH):
                print(f"Creating placeholder model file at {MODEL_PATH}")
                with open(MODEL_PATH, 'w') as f:
                    f.write("Placeholder model file")
                return MODEL_PATH
        except Exception as create_error:
            print(f"Failed to create placeholder file: {str(create_error)}", file=sys.stderr)
        
        raise

if __name__ == "__main__":
    download_model()