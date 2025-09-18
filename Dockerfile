FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

RUN mkdir -p /app/data
VOLUME ["/app/data"]

ENV PORT=5050
EXPOSE 5050

# Svarbu: bindinamės prie $PORT (jei jo nėra – 5050)
CMD ["sh","-c","gunicorn --chdir src -w 2 -b 0.0.0.0:${PORT:-5050} app:app"]
