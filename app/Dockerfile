FROM python:3.9-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/main.py .

COPY model/model.pkl .

CMD ["python", "main.py"]
