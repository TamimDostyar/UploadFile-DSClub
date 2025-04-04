# Available backend options are: "jax", "torch", "tensorflow".
import os
os.environ["KERAS_BACKEND"] = "torch"
	
import keras

def download_model():
    # Direct download from Hugging Face Hub
    from huggingface_hub import hf_hub_download

    # Download the model file directly to the current directory
    model_id = "dostah01/shark"
    print(f"Downloading model from {model_id}...")
    model_file = hf_hub_download(repo_id=model_id, filename="corn_model_1.keras", local_dir=".")
    print(f"Model downloaded successfully to {model_file}")

    print("Download complete!")

if __name__ == "__main__":
    download_model()