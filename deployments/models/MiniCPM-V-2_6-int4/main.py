from transformers import AutoModel, AutoTokenizer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from deployments.utils import logger, decode_base64_to_image


class MiniCPM_V_2_6_Int4:
    def load(self):
        self.model_name = "openbmb/MiniCPM-V-2_6-int4"
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
