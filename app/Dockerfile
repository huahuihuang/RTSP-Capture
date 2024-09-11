FROM python:3.12-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl --fail http://localhost:8001/ || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]