FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
COPY app.py .
COPY templates ./templates
EXPOSE 8080
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8080", "app:app"]
