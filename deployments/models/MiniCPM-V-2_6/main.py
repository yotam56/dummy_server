from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from PIL import Image
import base64
import io
import ray
import ray.serve as serve
from transformers import AutoTokenizer, AutoModel
import torch

# Initialize FastAPI app
app = FastAPI()

# Define the request schema
class RequestModel(BaseModel):
    text: str
    image_base64: str

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

# Service for inference
@serve.deployment(route_prefix="/predict", num_replicas=4)
class MiniCPMService:
    def __init__(self):
        # Initialize tokenizer and model with the specified parameters
        self.tokenizer = AutoTokenizer.from_pretrained(
            'openbmb/MiniCPM-V-2_6', trust_remote_code=True
        )
        self.model = AutoModel.from_pretrained(
            'openbmb/MiniCPM-V-2_6',
            trust_remote_code=True,
            attn_implementation='sdpa',
            torch_dtype=torch.bfloat16
        )
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.eval().to(self.device)

    @serve.batch(max_batch_size=8, batch_wait_timeout_s=0.1)
    async def __call__(self, request_list: List[RequestModel]):
        # Since model.chat might not support batch processing directly,
        # we'll process each request individually
        results = []
        for request in request_list:
            text = request.text
            image = decode_image(request.image_base64)
            msgs = [{'role': 'user', 'content': [image, text]}]

            # Perform inference using model.chat
            with torch.no_grad():
                response = self.model.chat(
                    image=None,
                    msgs=msgs,
                    tokenizer=self.tokenizer
                )
            results.append(response)

        return results

# Deploy the service
MiniCPMService.deploy()

# FastAPI Route
@app.post("/predict")
async def predict(request: RequestModel):
    # Forward the request to the Ray Serve deployment
    handle = serve.get_deployment("MiniCPMService").get_handle()
    result = await handle.remote(request)
    return {"result": await result}

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
