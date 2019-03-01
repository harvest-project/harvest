FROM python:latest as build

RUN apt update && \
    curl -sL https://deb.nodesource.com/setup_11.x | bash - && \
    apt-get install -y nodejs && \
    apt upgrade -y && \
    pip install pipenv

ENV PIPENV_DONT_LOAD_ENV=1

ARG pipenv_flags="--three"

WORKDIR /app

COPY Pipfile Pipfile.lock /app/

RUN pipenv install $pipenv_flags && npm install && npx webpack
