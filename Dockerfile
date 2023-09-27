FROM python:3.10-slim

WORKDIR /ayd
COPY . .

RUN pip install -r req_freeze.txt
RUN python -m nltk.downloader "punkt"

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
