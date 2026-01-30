FROM python:3.11-slim

WORKDIR /app

# No .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
#No buffer
ENV PYTTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

#Non root user
RUN useradd -m -u 1000 runner && chown -R runner:runner /app
USER runner

EXPOSE 5000

CMD ["python", "/app/app.py"]
#CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--reload", "--debugger"]
