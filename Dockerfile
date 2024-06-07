FROM python:3.10.12-alpine3.18 as requirements-stage

RUN mkdir /backend
WORKDIR /backend

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /backend/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.10.12-alpine3.18 as build-stage

WORKDIR /code

COPY --from=requirements-stage /backend/requirements.txt /code/requirements.txt

RUN apk add --no-cache \
    build-base \
    mysql-dev \
    pkgconfig
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .
COPY tests/.test.env /code/tests

ENV DJANGO_SETTINGS_MODULE=InnoterService.settings
ENV PYTHONUNBUFFERED=1

CMD ["sh", "start_app.sh"]
