FROM node:16-alpine as frontend-builder
WORKDIR /src

ADD ./frontend /src
RUN yarn install
RUN yarn run build

FROM python:3.10-buster as backend-builder

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
COPY ./backend/poetry.lock /src/poetry.lock
COPY ./backend/pyproject.toml /src/pyproject.toml
RUN pip install poetry && poetry config virtualenvs.create false && poetry install -C /src

FROM python:3.10-buster

ADD ./backend /src
COPY --from=backend-builder /venv /venv
ENV PATH="/venv/bin:$PATH"
COPY --from=frontend-builder /src/dist /src/static
RUN apt-get -qq update -y \
    && apt-get install -y libpq-dev build-essential \
    && apt-get -qq clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf ~/.cache


ENV STATIC_DIR=/src/static

#RUN apk update && apk add libpq
WORKDIR /src

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EXPOSE 8000

