from transformers import BlipProcessor, BlipForQuestionAnswering
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from deployments.utils import logger, decode_base64_to_image


class BLIPVQAModel:
    def load(self):
        self.model_name = "Salesforce/blip-vqa-base"
        try:
            self.processor = BlipProcessor.from_pretrained(self.model_name)
            self.model = BlipForQuestionAnswering.from_pretrained(self.model_name)
            logger.info(f"Model {self.model_name} loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {str(e)}")
            raise e

    def infer(self, base64_image: str, question: str):
        try:
            image = decode_base64_to_image(base64_image)
            inputs = self.processor(image, question, return_tensors="pt")
            output = self.model.generate(**inputs)
            answer = self.processor.decode(output[0], skip_special_tokens=True)
            logger.info("Inference completed successfully.")
            return answer
        except Exception as e:
            logger.error(f"Inference failed: {str(e)}")
            raise e


app = FastAPI()
model_instance = BLIPVQAModel()
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
        prediction = model_instance.infer(
            infer_request.base64_image, infer_request.question
        )
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
