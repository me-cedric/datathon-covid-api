FROM python:3.8-slim

RUN apt update && apt upgrade -y
RUN apt install -y libgtk2.0-dev

RUN useradd -d /home/app -m app

ENV APP_HOME=/home/app/web

WORKDIR $APP_HOME

RUN mkdir $APP_HOME/images

COPY . $APP_HOME

RUN chown -R app:app $APP_HOME

RUN pip install --upgrade pip pipenv

USER app

RUN pipenv install
