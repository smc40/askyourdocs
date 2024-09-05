
# app/frontend/Dockerfile
FROM node:14 as builder

ENV BACKEND_URL=https://api.ayd-sandbox.4punkt0.ch
ENV KEYCLOAK_URL=https://auth.ayd-sandbox.4punkt0.ch

RUN echo ${BACKEND_URL}
RUN echo ${KEYCLOAK_URL}

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
RUN apt-get update && apt-get install -y default-jre vim && rm -rf /var/lib/apt/lists/*

COPY app/landing /app/
COPY app/backend app/backend/
COPY askyourdocs askyourdocs/
COPY resources resources/
RUN mkdir -p app/backend/uploads

# Copy the built React app into the FastAPI static directory
COPY --from=builder /app/build /app/static

EXPOSE 8000
COPY app/frontend/entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]

# CMD ["uvicorn", "app.backend.app:app", "--host", "0.0.0.0", "--port", "8000"]

# IMAGE_TAG=0.2.4; docker build -t bouldermaettel/askyourdocs-app:$IMAGE_TAG . ; docker push bouldermaettel/askyourdocs-app:$IMAGE_TAG

