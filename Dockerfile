FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 這行可在 compose.yml 也可在這裡，保持一致
CMD ["python", "app.py"]
