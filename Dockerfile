FROM python:3.8-slim-buster as builder

WORKDIR /build

COPY ./app/requirements.txt /build/requirements.txt

RUN pip install --user --no-cache-dir --upgrade -r /build/requirements.txt

ADD ./app/iska app

FROM python:3.8-slim-buster as app

WORKDIR /code

# Setup GDAL
RUN apt-get update &&\
    apt-get install -y binutils libproj-dev gdal-bin python-gdal python3-gdal postgis

COPY --from=builder /build/app /code/
COPY .env /code/.env
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

RUN find /usr/local -depth \
  \( \
  \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
  -o \
  \( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
  \) -exec rm -rf '{}' +;
