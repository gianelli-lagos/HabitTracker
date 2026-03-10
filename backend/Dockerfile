FROM python:3.11-slim

WORKDIR /app

COPY dependencies.txt .
RUN pip install --no-cache-dir -r dependencies.txt

COPY . .
#start FASTAPI server when container runs
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]