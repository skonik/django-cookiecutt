ARG BASE_IMAGE=python:3.7.4-alpine3.10

FROM ${BASE_IMAGE}

# pass arg when building the image
ARG DJANGO_ENV

ENV DJANGO_ENV=${DJANGO_ENV} \
  PYTHONUNBUFFERED=1 \
  # pip no cache
  PIP_NO_CACHE_DIR=true

# client libs needed in runtime
RUN apk update && apk add --no-cache libpq libjpeg-turbo zlib

WORKDIR /app

# Alpine deps libraries installation.
# install as virtual deps
RUN apk add --no-cache --virtual build-deps \
    # gcc + musl-dev(lib-c implementation)
    build-base \
    # python3 with source headers
    python3-dev \
    # postgres deps
    postgresql-dev \
    # pillow deps
    jpeg-dev zlib-dev \
    # install pipenv
    && pip3 install pipenv

COPY Pipfile Pipfile.lock /app/

# Install python modules to system and clear deps with cache
RUN pipenv install --system --deploy --dev \
    && apk del build-deps \
    && rm -rf /root/.cache/*

COPY . /app/

