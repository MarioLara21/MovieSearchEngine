FROM python:3.11.4-alpine3.18

WORKDIR /app

COPY SQLProcesor.py .
COPY requirements.txt .

RUN apk update && \
    apk add --no-cache mariadb-client mariadb-connector-c-dev gcc musl-dev && \
    pip install --no-cache-dir -r requirements.txt

#RUN python -u SQLprocesor.py

CMD [ "python", "-u", "./SQLProcesor.py" ]
