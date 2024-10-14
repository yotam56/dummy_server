import os
import json
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from PIL import Image
import base64
import io
import ray
import ray.serve as serve
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from utils.logger import Logger
import torch

# Disable Ray's log deduplication
os.environ["RAY_DEDUP_LOGS"] = "0"

# Initialize FastAPI app
app = FastAPI()


# Define the request schema with a helper method to handle Ray's Request objects
class RequestModel(BaseModel):
    text: str
    image_base64: str  # This won't be used in the smaller model, but kept for consistency

    @classmethod
    async def from_request(cls, request) -> "RequestModel":
        """Helper function to extract data from Ray's Request object."""
        body = await request.body()
        try:
            data = json.loads(body)
            return cls(**data)  # Automatically map to RequestModel
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail="Invalid JSON body") from e


# Function to decode image from Base64 string (not used, but kept for consistency)
def decode_image(image_base64: str) -> Image.Image:
    try:
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        return image
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")


# Start Ray and Serve
ray.init(ignore_reinit_error=True)
serve.start()


# Service for inference
@serve.deployment(num_replicas=2)
class DistilBERTService:
    def __init__(self):
        # Initialize custom logger for each replica
        self.logger = Logger(logging.DEBUG).get_logger()
        self.logger.info("Initializing DistilBERTService")

        # Use a small, lightweight transformer model (DistilBERT)
        self.tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
        self.model = AutoModelForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.eval().to(self.device)
        self.logger.info(f"Model loaded and moved to {self.device}")

    @serve.batch(max_batch_size=8, batch_wait_timeout_s=0.2)
    async def __call__(self, request_list):
        self.logger.info(f"Replica {os.getpid()} processing batch of size: {len(request_list)}")

        # Use the RequestModel's helper to process Ray's Request objects
        request_models = [await RequestModel.from_request(request) for request in request_list]
        texts = [req_model.text for req_model in request_models]

        # Tokenize the batch of texts
        inputs = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True).to(self.device)
        self.logger.info(f"Tokenized inputs: {inputs}")

        # Perform inference
        with torch.no_grad():
            outputs = self.model(**inputs)
        self.logger.info(f"Inference outputs: {outputs.logits}")

        # Generate results for each input
        predictions = torch.argmax(outputs.logits, dim=-1)
        results = [{"text": text, "prediction": int(pred)} for text, pred in zip(texts, predictions)]
        self.logger.info(f"Batch processed with results: {results}")

        return results


# Deploy the service using serve.run (new Ray API)
serve.run(DistilBERTService.bind())


# FastAPI Route
@app.post("/predict")
async def predict(request: RequestModel):
    # Forward the request to the Ray Serve deployment
    handle = serve.get_deployment("DistilBERTService").get_handle()
    result = await handle.remote(request)
    return {"result": await result}


# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
