from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from PIL import Image
from io import BytesIO
import requests
import torch
from transformers import AutoModel, AutoTokenizer
from utils.timer import time_it
import logging
from utils.logger import Logger

logger = Logger(logging.DEBUG).get_logger()
app = FastAPI()

class InferenceRequest(BaseModel):
    image_url: str
    question: str

class ModelWrapper:
    def __init__(self, model_name: str, device: str):
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None

    @time_it
    def load_model(self):
        logger.info("loading Model and tokenizer")
        self.model = AutoModel.from_pretrained(
            self.model_name, trust_remote_code=True, torch_dtype=torch.float16
        ).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        self.model.eval()
        logger.info("Model and tokenizer loaded. Server is ready to inference!!!!!!!!!!!")

    @time_it
    def chat(self, image, msgs, sampling=True, temperature=0.7):
        image_tensor = torch.tensor(image).to(self.device).unsqueeze(0).half()  # Convert image to tensor and move to GPU
        with torch.no_grad():
            res = self.model.chat(
                image=image_tensor,
                msgs=msgs,
                tokenizer=self.tokenizer,
                sampling=sampling,
                temperature=temperature
            )
        return res

model_name = 'openbmb/MiniCPM-Llama3-V-2_5'
logger.info(f"Model Name: {model_name}")
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model_wrapper = ModelWrapper(model_name, device)

@app.on_event("startup")
async def startup_event():
    model_wrapper.load_model()

@app.post("/infer")
async def infer(request: InferenceRequest):
    # Download the image
    try:
        response = requests.get(request.image_url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert('RGB')
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error downloading image: {e}")

    # Prepare the input
    msgs = [{'role': 'user', 'content': request.question}]

    # Perform the inference
    res = model_wrapper.chat(image=image, msgs=msgs)
    return {"result": res}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Run the FastAPI application: uvicorn app:app --host 0.0.0.0 --port 8000

# Test the endpoint: curl -X POST "http://127.0.0.1:8000/infer" -H "Content-Type: application/json" -d '{"image_url": "https://st5.depositphotos.com/23843944/64646/v/600/depositphotos_646461852-stock-video-thief-standing-backyard-wearing-mask.jpg", "question": "What is in the image?"}'
