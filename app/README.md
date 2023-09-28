# ayd-app
This repository contains the ayd application.

## Backend


- Install dependencies and Run the app

```sh
  python -m venv <env_name>
  source ./<env_name>/bin/activate
  pip install -r requirements
```

Then
sh
```
source ../.env
cd backend
uvicorn app:app --host 0.0.0.0 --port 8050 --reload
```


## Frontend

```sh
cd frontend # move to the frontend directory
npm install # install the dependencies
```
```sh
npm run dev # start the app
```


## Tests

```sh
cd backend # move to the backend directory
python -m pytest tests -s --cov=api --cov-report term-missing
```

