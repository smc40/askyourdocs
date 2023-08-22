# askyourdocs
**Goal:** Locally hosted chatbot answering questions to your documents

**User Story:** As a *public relations employee* I would like to *ask questions to documents,* so *I can answer to requests faster*

## Links
- Q&A over Docs (LangChain): https://python.langchain.com/en/latest/use_cases/question_answering.html
- PrivateGPT: https://artificialcorner.com/privategpt-a-free-chatgpt-alternative-to-interact-with-your-documents-offline-ea1c98f98062

## Use Huggingface Models
Install transformers
```
pip install transformers, torch, SentencePiese, accelerate
```
download and use a model
```python
from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-small")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-small")

prompt = "In the following sentence, what is the drugname: Ibuprofen is well known to cause diarrhia."
input_ids = tokenizer(prompt, return_tensors="pt").input_ids

outputs = model.generate(input_ids, max_length = 512)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

## Requirements

- python 3.9+

## Usage

```sh
uvicorn askyourdocs.app:app --host 0.0.0.0 --port 8006 --reload
```

