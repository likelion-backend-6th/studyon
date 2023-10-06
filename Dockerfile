FROM node:18.14.2 as tailwind

ARG APP_NAME=/app

WORKDIR ${APP_NAME}

COPY ./package.json ./
COPY ./package-lock.json ./
RUN npm install

COPY . ${APP_NAME}

RUN npm run build

FROM python:3.11-alpine

ARG APP_NAME=/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR ${APP_NAME}

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=tailwind ${APP_NAME} ${APP_NAME}

COPY ./scripts/entrypoint.sh /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./scripts/start.sh /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

ENTRYPOINT [ "/entrypoint" ]
CMD ["/start"]