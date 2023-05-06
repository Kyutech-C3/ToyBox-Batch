FROM python:3.10-alpine

RUN mkdir /sitemap

WORKDIR /sitemap

RUN pip install --upgrade pip
RUN pip install pipenv

COPY ./Pipfile .
COPY ./Pipfile.lock .

RUN pipenv install
