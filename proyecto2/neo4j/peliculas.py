# Basado en codigo de: https://github.com/neo4j-examples/movies-python-bolt.git
# Fabian Bustos Proyecto 2 BD2 
# ToDo: hacerlo APIey / Flask components 
import os
import json 
from json import dumps 
from typing import cast 

import neo4j 
from flask import Flask, Response, jsonify
from flask_cors import CORS
from neo4j import GraphDatabase, basic_auth



app = Flask(__name__, static_url_path="/static/")
CORS(app)

url = os.getenv("NEO4J_URI", "neo4j+s://demo.neo4jlabs.com")
username = os.getenv("NEO4J_USER", "movies")
password = os.getenv("NEO4J_PASSWORD", "movies")
neo4j_version = os.getenv("NEO4J_VERSION", "4")
database = os.getenv("NEO4J_DATABASE", "movies")

port = int(os.getenv("PORT", 8080))

driver = GraphDatabase.driver(url, auth=basic_auth(username, password))

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


## refine funcion de busqueda por pelicula 
@app.route("/movies/<title>")
def get_movie(title):
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
def actor_search(name): 
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
def producer_search(name): 
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
@app.route("/director/<name>")
def director_search(name): 
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
def get_movie_plot(title):
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
def get_movies_plot(title):
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
def get_cast(title):
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

@app.route("/")
def home(): 
     return "Home"


#Nombres que funcionan para las busquedas: 
#Actor: Keanu Reeves, Tom Hanks
#Directora: Lilly Wachowski
#Productor: Joel Silver


if __name__ == "__main__":
    
    #driver.close()
    app.run(host='0.0.0.0')