#syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /neo4j 


COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt 

COPY peliculas.py . 

#ENV FLASK_APP=peliculas.py 
EXPOSE 5000

#RUN pip install --no-cache-dir -r requirements.txt

# --port=8080
CMD ["python3", "-u", "./peliculas.py"]
