import pymongo
from datetime import datetime, timezone
from flask import Flask, request, jsonify, g, current_app, Response
from flask_cors import CORS
from prometheus_client import start_http_server, Counter, Gauge, Histogram
from pymongo.errors import PyMongoError
import time
import logging
import json
from json import dumps 
from typing import cast
import neo4j
from neo4j import GraphDatabase, basic_auth
import os 
import sys

# Basado en: https://github.com/mongodb-university/atlas_starter_python/blob/master/atlas-starter.py

# Configura la conexión a MongoDB Atlas
try:
    conexion= os.environ.get("MONGO_STRING")
    client = pymongo.MongoClient(conexion)

# return a friendly error if a URI error is thrown 
except pymongo.errors.ConfigurationError:
  print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
  sys.exit(1)

try:
    # Seleccionar la base de datos y la colección
    db = client.sample_mflix
    collection = db.movies

except pymongo.errors as e:
    print("Error: ", e)

url = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")
neo4j_version = os.getenv("NEO4J_VERSION")
database = os.getenv("NEO4J_DATABASE")

port = int(os.getenv("PORT"))

driver = GraphDatabase.driver(url, auth=basic_auth(username, password))

# Inicializa Flask
app = Flask(__name__)
CORS(app)

# Inicializa Prometheus
REQUEST_COUNT = Counter('flask_http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_TIME = Histogram('request_time', 'Request Time', ['method', 'endpoint'])

#Funciones incluidas para busqueda por pelicula 
def serialize_movie(movie):
    return {
        "id": movie["id"],
        "title": movie["title"],
        "summary": movie["summary"],
        "released": movie["released"],
        "duration": movie["duration"],
        "rated": movie["rated"],
        "tagline": movie["tagline"],
        "votes": movie.get("votes", 0)
    }

# "   "
def serialize_cast(cast):
    return {
        "name": cast[0],
        "job": cast[1],
        "role": cast[2]
    }

# contador de tiempo por request hecho utilizando https://sureshdsk.dev/flask-decorator-to-measure-time-taken-for-a-request
@app.before_request
def logging_before():
    pass

@app.route('/endpoint', methods=['POST'])
@REQUEST_TIME.labels(method='POST', endpoint='/endpoint').time()
def endpoint():
    REQUEST_COUNT.labels(method='POST', endpoint='/endpoint').inc()
    data = request.get_json()
    usuario = data.get("userId")
    busqueda = data.get("busqueda")

    # Guarda la solicitud en MongoDB
    solicitud = {
        "body": request.get_data(as_text=True),
        "request": busqueda,
        "timestamp": datetime.now(timezone.utc),
        "usuario": usuario
    }
    coleccion = db.registros
    coleccion.insert_one(solicitud)
    
    return jsonify({"mensaje": "Solicitud guardada exitosamente"}), 200


@app.route('/titulo/<palabra>', methods=['GET'])
@REQUEST_TIME.labels(method='GET', endpoint='/titulo').time()
def buscar_pelicula(palabra):
    REQUEST_COUNT.labels(method='GET', endpoint='/titulo/<palabra>').inc()
    try:
        # Seleccionar la base de datos y la colección
        db = client.sample_mflix
        collection = db.movies

        # Realizar la búsqueda en el campo deseado
        regex = f"\\b{palabra}\\b"       # Expresión para buscar la palabra exacta
        resultado = collection.find({"title": { "$regex": regex, "$options": "i" }})

        resultados_json = [documento for documento in resultado]

        # Convertir la lista de diccionarios a JSON y luego a bytes
        for documento in resultados_json:
            documento['_id'] = str(documento['_id'])

        return resultados_json

    except PyMongoError as e:
        return jsonify({"error": str(e)})


@app.route('/director/<director>', methods=['GET'])
@REQUEST_TIME.labels(method='GET', endpoint='/director').time()
def buscar_directors(director):
    REQUEST_COUNT.labels(method='GET', endpoint='/director/<director>').inc()
    try:
        # Seleccionar la base de datos y la colección
        db = client.sample_mflix
        collection = db.movies

        # Realizar la búsqueda en el campo deseado
        agg =  [{"$search": {
            "index": "directores", 
            "wildcard": {
                "query": director,
                "path": "directors",
                "allowAnalyzedField": True
            }
        }}]

        resultado = collection.aggregate(agg)

        
        resultados_json = [documento for documento in resultado]

        # Convertir la lista de diccionarios a JSON y luego a bytes
        for documento in resultados_json:
            documento['_id'] = str(documento['_id'])

        return resultados_json

    except PyMongoError as e:
        return jsonify({"error": str(e)})
    
@app.route('/elenco/<cast>', methods=['GET'])
@REQUEST_TIME.labels(method='GET', endpoint='/elenco').time()
def buscar_cast(cast):
    REQUEST_COUNT.labels(method='GET', endpoint='/elenco/<cast>').inc()
    try:
        # Seleccionar la base de datos y la colección
        db = client.sample_mflix
        collection = db.movies

        # Realizar la búsqueda en el campo deseado
        agg =  [{"$search": {
            "index": "elenco", 
            "wildcard": {
                "query": cast,
                "path": "cast",
                "allowAnalyzedField": True
            }
        }}]

        resultado = collection.aggregate(agg)

        
        resultados_json = [documento for documento in resultado]

        # Convertir la lista de diccionarios a JSON y luego a bytes
        for documento in resultados_json:
            documento['_id'] = str(documento['_id'])

        return resultados_json

    except PyMongoError as e:
        return jsonify({"error": str(e)})
    

@app.route('/trama/<plot>', methods=['GET'])
@REQUEST_TIME.labels(method='GET', endpoint='/trama').time()
def buscar_plot(plot):
    REQUEST_COUNT.labels(method='GET', endpoint='/trama/<plot>').inc()
    try:
        # Seleccionar la base de datos y la colección
        db = client.sample_mflix
        collection = db.movies

        # Realizar la búsqueda en el campo deseado
        agg =  [{"$search": {
            "index": "trama", 
            "wildcard": {
                "query": plot,
                "path": "plot",
                "allowAnalyzedField": True
            }
        }}]

        resultado = collection.aggregate(agg)

        resultados_json = [documento for documento in resultado]

        # Convertir la lista de diccionarios a JSON y luego a bytes
        for documento in resultados_json:
            documento['_id'] = str(documento['_id'])

        return resultados_json

    except PyMongoError as e:
        return jsonify({"error": str(e)})

## refine funcion de busqueda por pelicula 
@app.route("/movies/<title>")
@REQUEST_TIME.labels(method='GET', endpoint='/movies').time()
def get_movie(title):
    REQUEST_COUNT.labels(method='GET', endpoint='/movies/<title>').inc()
    with driver.session() as session:
        result = session.run(
            """
            MATCH (movie:Movie {title:$title})
            OPTIONAL MATCH (movie)<-[r]-(person:Person)
            RETURN movie.title AS title,
            COLLECT(
                [person.name, HEAD(SPLIT(TOLOWER(TYPE(r)), '_')), r.roles]
            ) AS cast
            LIMIT 1
            """,
            title=title
        )

        record = result.single()

        if record is None:
            return Response(dumps({"error": "Movie not found"}), status=404, mimetype="application/json")

        movie_info = {
            "title": record["title"],
            "cast": [
                {
                    "name": member[0],
                    "relationship": member[1],
                    "roles": member[2]
                }
                for member in record["cast"]
            ]
        }

        return Response(dumps(movie_info), mimetype="application/json").data
       

#Busqueda por actor 
@app.route("/actor/<name>")
@REQUEST_TIME.labels(method='GET', endpoint='/actor').time()
def actor_search(name): 
        REQUEST_COUNT.labels(method='GET', endpoint='/actor/<name>').inc()  
        with driver.session() as session:
            result = session.run(
                """
                MATCH (:Person {name: $name})-[:ACTED_IN]->(movie:Movie)
                RETURN movie.title AS title
                """,
                name=name
            )
            
            movies = [record["title"] for record in result]

            if not movies:
                return Response(dumps({"error": "Actor not found "}), 
                                status=404, mimetype="application/json")

            return Response(dumps({"movies": movies}), mimetype="application/json").data
        
# busqueda por productor
@app.route("/producer/<name>")
@REQUEST_TIME.labels(method='GET', endpoint='/producer').time()
def producer_search(name): 
        REQUEST_COUNT.labels(method='GET', endpoint='/producer/<name>').inc()
        with driver.session() as session:
            result = session.run(
                """
                MATCH (:Person {name: $name})-[:PRODUCED]->(movie:Movie)
                RETURN movie.title AS title
                """,
                name=name
            )
            
            movies = [record["title"] for record in result]

            if not movies:
                return Response(dumps({"error": "Producer not found"}), 
                                status=404, mimetype="application/json")

            return Response(dumps({"movies": movies}), mimetype="application/json").data

# busqueda por director
@app.route("/directores/<name>")
@REQUEST_TIME.labels(method='GET', endpoint='/directores').time()
def director_search(name): 
        REQUEST_COUNT.labels(method='GET', endpoint='/directores/name>').inc()
        with driver.session() as session:
            result = session.run(
                """
                MATCH (:Person {name: $name})-[:DIRECTED]->(movie:Movie)
                RETURN movie.title AS title
                """,
                name=name
            )
            
            movies = [record["title"] for record in result]

            if not movies:
                return Response(dumps({"error": "Director not found"}), 
                                status=404, mimetype="application/json")

            return Response(dumps({"movies": movies}), mimetype="application/json").data


@app.route("/plot/<title>")   
@REQUEST_TIME.labels(method='GET', endpoint='/plot').time() 
def get_movie_plot(title):
    REQUEST_COUNT.labels(method='GET', endpoint='/plot/<title>').inc()
    with driver.session() as session:
        result = session.run(
            """
            MATCH (movie:Movie {title: $title})
            RETURN movie.tagline AS plot
            """,
            title=title
        )

        record = result.single()

        if record is None:
            return Response(dumps({"error": "Movie not found"}), status=404, mimetype="application/json")

        plot = record["plot"]

        return Response(dumps({"plot": plot}), mimetype="application/json").data
    
@app.route("/plots/<title>")    
@REQUEST_TIME.labels(method='GET', endpoint='/plots').time()
def get_movies_plot(title):
    REQUEST_COUNT.labels(method='GET', endpoint='/plots/<title>').inc()
    with driver.session() as session:
        result = session.run(
            """
            MATCH (movie:Movie {title: $title})
            RETURN movie.tagline AS plot
            """,
            title=title
        )

        record = result.single()

        if record is None:
            return Response(dumps({"error": "Movie not found"}), status=404, mimetype="application/json")

        plot = record["plot"]

        answer =Response(dumps({"plot": plot}), mimetype="application/json").data
        return json.loads(answer.decode('utf-8'))["plot"]
    
@app.route("/cast/<title>")
@REQUEST_TIME.labels(method='GET', endpoint='/cast').time()
def get_cast(title):
    REQUEST_COUNT.labels(method='GET', endpoint='/cast/<title>').inc()
    with driver.session() as session:
        result = session.run(
            """
            MATCH (movie:Movie {title: $title})<-[:ACTED_IN]-(actor:Person)
            RETURN actor.name AS actorName
            """,
            title=title
        )

        actors = [record["actorName"] for record in result]

        if not actors:
            return Response(dumps({"error": "Movie not found or no actors found"}), 
                            status=404, mimetype="application/json")

        return Response(dumps({"actors": actors}), mimetype="application/json").data


if __name__ == '__main__':
    start_http_server(8000)
    app.run(host='0.0.0.0')


