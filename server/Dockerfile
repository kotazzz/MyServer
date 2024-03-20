FROM python:3.11

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY /server/ /app/server/

CMD ["sanic", "server.main:app", "--port", "24551", "--host", "0.0.0.0", "--dev"]
# sanic server.main:app --port 24551 --host 0.0.0.0 --dev