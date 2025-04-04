# Available backend options are: "jax", "torch", "tensorflow".
import os
import sys

def download_model():
    """
    Downloads the corn disease classification model from Hugging Face Hub.
    Handles errors and checks if the model already exists before downloading.
    """
    # Check if model already exists first
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, "corn_model_1.keras")
    
    if os.path.exists(MODEL_PATH):
        print(f"Model already exists at {MODEL_PATH}")
        return MODEL_PATH
    
    # Try to import huggingface_hub
    try:
        import huggingface_hub
        from huggingface_hub import hf_hub_download
        print(f"Using huggingface_hub version: {huggingface_hub.__version__}")
    except ImportError:
        print("ERROR: huggingface_hub not installed. Creating placeholder file.")
        # Create an empty placeholder file if import fails
        try:
            if not os.path.exists(MODEL_PATH):
                print(f"Creating placeholder model file at {MODEL_PATH}")
                os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
                with open(MODEL_PATH, 'w') as f:
                    f.write("Placeholder model file - huggingface_hub module not available")
                return MODEL_PATH
        except Exception as create_error:
            print(f"Failed to create placeholder file: {str(create_error)}", file=sys.stderr)
        return None
    
    # Try to download the model
    try:
        model_id = "dostah01/shark"
        print(f"Downloading model from {model_id}...")
        
        # Set a public access token if needed (or use environment variable)
        token = os.environ.get("HF_TOKEN", None)
        if token:
            print("Using provided Hugging Face token")
        else:
            print("No Hugging Face token provided - attempting download without authentication")
            
        model_file = hf_hub_download(
            repo_id=model_id, 
            filename="corn_model_1.keras", 
            local_dir=BASE_DIR,
            token=token,
            force_download=True  # Force download even if cached
        )
        print(f"Model downloaded successfully to {model_file}")
        print("Download complete!")
        return model_file
    except Exception as e:
        print(f"Error downloading model: {str(e)}", file=sys.stderr)
        
        # Create an empty placeholder file if download fails
        try:
            if not os.path.exists(MODEL_PATH):
                print(f"Creating placeholder model file at {MODEL_PATH}")
                with open(MODEL_PATH, 'w') as f:
                    f.write("Placeholder model file - download failed")
                return MODEL_PATH
        except Exception as create_error:
            print(f"Failed to create placeholder file: {str(create_error)}", file=sys.stderr)
        
        return None

if __name__ == "__main__":
    download_model()