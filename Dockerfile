FROM python:alpine
ENV PYTHONUNBUFFERED=1
WORKDIR /code

COPY requirements.txt .

RUN apk update && apk add libpq jpeg-dev zlib-dev libjpeg
RUN apk --no-cache  add curl

# install python binary packages
RUN apk --no-cache add py3-aiohttp


RUN apk add --no-cache --virtual .build-deps \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    && apk add --no-cache libpq \
    && pip install --no-cache-dir Pillow \
    && pip install --no-cache-dir aiohttp \
    && pip install --no-cache-dir psycopg2 \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del --no-cache .build-deps

COPY . .