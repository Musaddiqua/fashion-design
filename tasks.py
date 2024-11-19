from pymongo import MongoClient
from diffusers import StableDiffusionPipeline
import os
import torch
from redis import Redis
from rq import Queue

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["fabric_db"]
collection = db["entries"]

# Redis setup for background task queue
redis_conn = Redis()
queue = Queue(connection=redis_conn)

# Hugging Face Stable Diffusion setup
pipeline = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0")
pipeline.to("cuda" if torch.cuda.is_available() else "cpu")  # Use GPU if available

def generate_image_task(prompt):
    """Generate an image asynchronously."""
    try:
        # Generate an image
        image = pipeline(prompt, num_inference_steps=50).images[0]
        image_path = os.path.join("static", f"{prompt.replace(' ', '_')}.png")
        os.makedirs("static", exist_ok=True)  # Ensure the static directory exists
        image.save(image_path)

        # Save prompt and image path in MongoDB
        entry = {"text": prompt, "image_path": image_path}
        collection.insert_one(entry)

        return image_path
    except Exception as e:
        return f"Error generating image: {str(e)}"
