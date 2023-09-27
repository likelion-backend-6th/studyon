FROM python:3.11-alpine

ARG APP_NAME=/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR ${APP_NAME}

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ${APP_NAME}

ENTRYPOINT ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]