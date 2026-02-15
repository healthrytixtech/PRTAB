FROM python:3.11-slim
# slim = stripped-down version of the Debian image containing only the essentials to run Python

WORKDIR /app
# /app = directory in container

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*
#for postgres

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 
# 0.0.0.0 tells the app to listen to requests from outside the container rather than just internally