FROM python:3.10-slim

WORKDIR /ayd
COPY . .

RUN pip install . && \
    cp -r docs .. && \
    cd .. && \
    rm -rf ayd && \
    rm -rf ~/.cache

RUN python -m nltk.downloader "punkt"
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
