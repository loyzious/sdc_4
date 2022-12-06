FROM python:3.8
LABEL maintainer="caraet"
COPY . /app
COPY ./openssl.cnf /etc/ssl/
WORKDIR /app
RUN pip install -r requirements.txt