FROM python:3.11-slim

# Greitesnis/patogesnis Python logavimas
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Įdiegiame priklausomybes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Įkeliame programos kodą
COPY src/ ./src/

# Vietinis diskas scenarijams
RUN mkdir -p /app/data
VOLUME ["/app/data"]

# App portas
ENV PORT=5050
EXPOSE 5050

# Paleidimas (production serveris)
CMD ["gunicorn","--chdir","src","-w","2","-b","0.0.0.0:5050","app:app"]
