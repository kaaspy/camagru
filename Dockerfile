FROM python:3.13-slim

WORKDIR /app

# No .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
#No buffer
ENV PYTHONUNBUFFERED=1

ENV FLASK_APP=camagru:create_app
ENV FLASK_ENV=production

# RUN apt-get update && apt-get install -y \
#     gcc \
#     default-libmysqlclient-dev \
#     pkg-config \
#     && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./camagru /app/camagru
COPY requirements.txt /app/
COPY .env /app/

RUN flask --app camagru init-db

#Non root user
RUN useradd -m -u 1000 runner && chown -R runner:runner /app
USER runner

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "camagru:create_app()"]
# CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
