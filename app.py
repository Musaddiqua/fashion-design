from flask import Flask, render_template, request, jsonify
from redis import Redis
from rq import Queue
from tasks import generate_image_task, collection  # Importing collection from tasks.py
import os
import requests

# Flask setup
app = Flask(__name__)

# Redis setup for background task queue
redis_conn = Redis()
queue = Queue(connection=redis_conn)

# Sustainable Fabric Classification API URL (Placeholder; replace with actual API)
FABRIC_API_URL = "https://platform.openai.com/docs/api-reference/images/create"

@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_image():
    """Endpoint to generate an image."""
    data = request.get_json()
    prompt = data.get("text", "default fashion design")
    
    # Enqueue the task for background processing
    job = queue.enqueue(generate_image_task, prompt)
    
    # Polling for job result (can be optimized with async handling)
    while job.result is None:
        pass
    
    job_result = job.result  # Get the generated image path

    if job_result and os.path.exists(job_result):
        # Return the image URL
        image_url = f"/static/{os.path.basename(job_result)}"
        return jsonify({"image_url": image_url})
    else:
        return jsonify({"error": "Failed to generate image"}), 500

@app.route("/classify", methods=["POST"])
def classify_material():
    """Classify material using a third-party API."""
    data = request.get_json()
    image_path = data.get("image_path")

    if not image_path or not os.path.exists(image_path):
        return jsonify({"error": "Invalid or missing image path"}), 400

    try:
        # Send image to the Sustainable Fabric Classification API
        with open(image_path, "rb") as image_file:
            response = requests.post(
                FABRIC_API_URL,
                files={"file": image_file}
            )
        
        if response.status_code == 200:
            classification_response = response.json()

            # Update MongoDB with classification results
            collection.update_one(
                {"image_path": image_path},
                {"$set": {"classification": classification_response}}
            )
            
            return jsonify(classification_response)
        else:
            return jsonify({"error": "Failed to classify image", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
