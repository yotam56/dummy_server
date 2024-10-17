import os
import json
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from PIL import Image
import base64
import io
import ray
import ray.serve as serve
from transformers import BlipProcessor, BlipForQuestionAnswering
from utils.logger import Logger
import torch

# Disable Ray's log deduplication
os.environ["RAY_DEDUP_LOGS"] = "0"

# Initialize FastAPI app
app = FastAPI()


# Define the request schema with image and text
class RequestModel(BaseModel):
    question: str
    image_base64: str

    @classmethod
    async def from_request(cls, request) -> "RequestModel":
        """Helper function to extract data from Ray's Request object."""
        body = await request.body()
        try:
            data = json.loads(body)
            return cls(**data)  # Automatically map to RequestModel
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail="Invalid JSON body") from e


# Function to decode image from Base64 string
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


# Service for BLIP inference
@serve.deployment(num_replicas=2)
class BlipService:
    def __init__(self):
        # Initialize custom logger for each replica
        self.logger = Logger(logging.DEBUG).get_logger()
        self.logger.info("Initializing BlipService")

        # Load BLIP model for Visual Question Answering
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-base")
        self.model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-base")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.eval().to(self.device)
        self.logger.info(f"BLIP model loaded and moved to {self.device}")

    @serve.batch(max_batch_size=4, batch_wait_timeout_s=1.0)
    async def __call__(self, request_list):
        self.logger.info(f"Replica {os.getpid()} processing batch of size: {len(request_list)}")

        # Use the RequestModel's helper to process Ray's Request objects
        request_models = [await RequestModel.from_request(request) for request in request_list]

        # Decode images and extract questions
        images = [decode_image(req_model.image_base64) for req_model in request_models]
        questions = [req_model.question for req_model in request_models]

        # Process the inputs using the BLIP processor
        inputs = self.processor(images, questions, return_tensors="pt").to(self.device)
        self.logger.info(f"Processed inputs: {inputs}")

        # Perform inference
        with torch.no_grad():
            outputs = self.model.generate(**inputs)

        # Decode outputs to human-readable answers
        answers = [self.processor.decode(output, skip_special_tokens=True) for output in outputs]
        self.logger.info(f"Batch processed with answers: {answers}")

        # Return results as list of dictionaries
        results = [{"question": question, "answer": answer} for question, answer in zip(questions, answers)]
        return results


# Deploy the BLIP service
serve.run(BlipService.bind())


# FastAPI Route
@app.post("/predict")
async def predict(request: RequestModel):
    # Forward the request to the Ray Serve deployment
    handle = serve.get_deployment("BlipService").get_handle()
    result = await handle.remote(request)
    return {"result": await result}


# Run the app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
