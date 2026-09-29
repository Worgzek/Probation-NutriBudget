FROM python:3.10-slim

WORKDIR /app

#psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

#requirements.txt
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#backend -> container
COPY . .

#run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
