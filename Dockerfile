
# app/frontend/Dockerfile
FROM node:14 as builder

WORKDIR /app

COPY ./app/frontend /app

RUN npm install
RUN npm run build

FROM python:3.10-slim

WORKDIR /app
# RUN touch requirements.txt
COPY req_freeze.txt ./req_freeze.txt

RUN pip install -r req_freeze.txt

# Install Java needed for TIKA
RUN apt-get update && apt-get install -y default-jre && rm -rf /var/lib/apt/lists/*

COPY app/landing /app/
COPY app/backend app/backend/
COPY askyourdocs askyourdocs/
COPY resources resources/
RUN mkdir -p app/backend/uploads

# Copy the built React app into the FastAPI statimc directory
COPY --from=builder /app/build /app/static

EXPOSE 8000

CMD ["uvicorn", "app.backend.app:app", "--host", "0.0.0.0", "--port", "8000"]

# IMAGE_TAG=0.0.5; docker build -t bouldermaettel/askyourdocs-app:$IMAGE_TAG . ; docker push bouldermaettel/askyourdocs-app:$IMAGE_TAG