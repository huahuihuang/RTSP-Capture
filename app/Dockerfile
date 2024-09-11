FROM python:3.12-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl --fail http://localhost:80/ || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]