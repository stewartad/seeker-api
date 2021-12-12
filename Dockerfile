# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8

WORKDIR /app

ENV DJANGO_SETTINGS_MODULE=seeker.test_settings

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

COPY ./src/seeker /app
