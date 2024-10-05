# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from transformers import AutoModel, AutoTokenizer, AutoProcessor
# import torch
# from PIL import Image
#
# class BaseModelClass:
#     def __init__(self, model_name):
#         self.model_name = model_name
#         self.model = None
#         self.tokenizer = None
#         self.processor = None
#
#     def load(self):
#         raise NotImplementedError("Each model class must implement the load method")
#
#     def infer(self, text: str):
#         raise NotImplementedError("Each model class must implement the infer method")
#
#
# class MiniCPM_V_2_6_Int4(BaseModelClass):
#     def load(self):
#         self.model = AutoModel.from_pretrained(self.model_name, trust_remote_code=True)
#         self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
#         self.model.eval()
#
#     def infer(self, image_path: str, question: str):
#         image = Image.open(image_path).convert('RGB')
#         msgs = [{'role': 'user', 'content': [image, question]}]
#         result = self.model.chat(image=None, msgs=msgs, tokenizer=self.tokenizer)
#         return result
#
#
# class MiniCPM_V_2_6(BaseModelClass):
#     def load(self):
#         self.model = AutoModel.from_pretrained(self.model_name, trust_remote_code=True,
#                                                attn_implementation='sdpa', torch_dtype=torch.bfloat16)
#         self.model = self.model.eval().cuda()
#         self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
#
#     def infer(self, image_path: str, question: str):
#
#         image = Image.open(image_path).convert('RGB')
#         msgs = [{'role': 'user', 'content': [image, question]}]
#         result = self.model.chat(image=None, msgs=msgs, tokenizer=self.tokenizer)
#         return result
#
#
# class MiniCPM_Llama3_V_2_5(BaseModelClass):
#     def load(self):
#         self.model = AutoModel.from_pretrained(self.model_name, trust_remote_code=True,
#                                                torch_dtype=torch.float16)
#         self.model = self.model.to(device='cuda')
#         self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
#         self.model.eval()
#
#     def infer(self, text: str):
#         inputs = self.tokenizer(text, return_tensors="pt")
#         with torch.no_grad():
#             outputs = self.model(**inputs)
#         predicted_class = torch.argmax(outputs.logits, dim=1).item()
#         return f"Class {predicted_class}"
#
#
# class Llama3_11B_Vision_Instruct(BaseModelClass):
#     def load(self):
#         self.model = MllamaForConditionalGeneration.from_pretrained(self.model_name, torch_dtype=torch.bfloat16,
#                                                                     device_map="auto")
#         self.processor = AutoProcessor.from_pretrained(self.model_name)
#
#     def infer(self, text: str):
#         inputs = self.processor(text, return_tensors="pt")
#         outputs = self.model.generate(**inputs)
#         return outputs[0]
#
#
# class MiniCPM_V_2(BaseModelClass):
#     def load(self):
#         self.model = AutoModel.from_pretrained(self.model_name, trust_remote_code=True, torch_dtype=torch.bfloat16)
#         self.model = self.model.to(device='cuda', dtype=torch.bfloat16)
#         self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
#         self.model.eval()
#
#     def infer(self, text: str):
#         inputs = self.tokenizer(text, return_tensors="pt")
#         with torch.no_grad():
#             outputs = self.model(**inputs)
#         predicted_class = torch.argmax(outputs.logits, dim=1).item()
#         return f"Class {predicted_class}"
#
#
# class MiniCPM_Llama3_V_2_5_Int4(BaseModelClass):
#     def load(self):
#         self.model = AutoModel.from_pretrained(self.model_name, trust_remote_code=True)
#         self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
#         self.model.eval()
#
#     def infer(self, image_path: str, question: str):
#         image = Image.open(image_path).convert('RGB')
#         msgs = [{'role': 'user', 'content': [image, question]}]
#         result = self.model.chat(image=None, msgs=msgs, tokenizer=self.tokenizer)
#         return result
