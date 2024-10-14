from transformers import AutoModel, AutoTokenizer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from deployments.utils import logger, decode_base64_to_image

import json
from typing import AsyncGenerator

from fastapi import BackgroundTasks
from starlette.requests import Request
from starlette.responses import StreamingResponse, Response
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.sampling_params import SamplingParams
from vllm.utils import random_uuid

from ray import serve

from PIL import Image
import base64
import io
import os


@serve.deployment(ray_actor_options={"num_gpus": 1})
class VLLMPredictDeployment:
    def __init__(self, **kwargs):
        """
        Initialize VLLM with support for multimodal (text + image) input.
        """
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
        kwargs["gpu_memory_utilization"] = kwargs.get("gpu_memory_utilization", 0.8)
        kwargs["trust_remote_code"] = True
        args = AsyncEngineArgs(**kwargs)
        self.engine = AsyncLLMEngine.from_engine_args(args)
        self.model_name = kwargs.get('model')

    async def stream_results(self, results_generator) -> AsyncGenerator[bytes, None]:
        num_returned = 0
        async for request_output in results_generator:
            text_outputs = [output.text for output in request_output.outputs]
            assert len(text_outputs) == 1
            text_output = text_outputs[0][num_returned:]
            ret = {"text": text_output}
            yield (json.dumps(ret) + "\n").encode("utf-8")
            num_returned += len(text_output)

    async def may_abort_request(self, request_id) -> None:
        await self.engine.abort(request_id)

    async def __call__(self, request: Request) -> Response:
        """
        Generate completion for multimodal input (text + image).
        """
        request_dict = await request.json()
        prompt = request_dict.pop("prompt")  # Text prompt
        image_base64 = request_dict.pop("image", None)  # Base64 image data
        stream = request_dict.pop("stream", False)  # Streaming option

        if image_base64:
            image = decode_base64_to_image(image_base64)  # Decode image
        else:
            raise HTTPException(status_code=400, detail="Image data is required.")

        sampling_params = SamplingParams(**request_dict)
        request_id = random_uuid()

        # Combine text and image as multimodal input
        inputs = {
            "prompt": prompt,
            "multi_modal_data": {
                "image": image  # Pass decoded image
            }
        }

        # Generate using the multimodal inputs
        results_generator = self.engine.generate(inputs, sampling_params, request_id)

        if stream:
            background_tasks = BackgroundTasks()
            background_tasks.add_task(self.may_abort_request, request_id)
            return StreamingResponse(
                self.stream_results(results_generator), background=background_tasks
            )

        # Non-streaming case
        final_output = None
        async for request_output in results_generator:
            if await request.is_disconnected():
                await self.engine.abort(request_id)
                return Response(status_code=499)
            final_output = request_output

        assert final_output is not None
        text_outputs = [output.text for output in final_output.outputs]
        return Response(content=json.dumps({"text": text_outputs}))


########################### old code #########################
class MiniCPM_V_2_6_Int4:
    def load(self):
        self.model_name = "MiniCPM-Llama3-V-2_5-vllm"
        try:
            self.model = AutoModel.from_pretrained(self.model_name, trust_remote_code=True)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
            self.model.eval()
            logger.info(f"Model {self.model_name} loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {str(e)}")
            raise e

    def infer(self, base64_image: str, question: str):
        try:
            image = decode_base64_to_image(base64_image)
            msgs = [{'role': 'user', 'content': [image, question]}]
            result = self.model.chat(image=None, msgs=msgs, tokenizer=self.tokenizer)
            logger.info("Inference completed successfully.")
            return result
        except Exception as e:
            logger.error(f"Inference failed: {str(e)}")
            raise e


app = FastAPI()
model_instance = MiniCPM_V_2_6_Int4()
model_instance.load()

class MultimodalRequest(BaseModel):
    question: str
    base64_image: str


class MultimodalResponse(BaseModel):
    prediction: str


@app.get("/health_check")
async def health_check():
    logger.info("Health check called.")
    return {"status": "Healthy"}


@app.post("/infer")
async def infer(infer_request: MultimodalRequest):
    try:
        logger.info("Received inference request.")
        prediction = model_instance.infer(infer_request.base64_image, infer_request.question)
        logger.info("Returning inference result.")
        return MultimodalResponse(prediction=prediction)
    except Exception as e:
        logger.error(f"Error during inference request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
