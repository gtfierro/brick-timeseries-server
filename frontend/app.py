import requests
import os
import uuid
from collections import defaultdict
from typing import Optional
import rdflib
from fastapi import FastAPI
from pydantic import BaseModel
from SPARQLWrapper import SPARQLWrapper, JSON

class Point(BaseModel):
    name: str
    unit: str
    types: list[str]
    tsid: Optional[str] = None
    on: Optional[str] = None

BRICK = rdflib.BRICK
NS = rdflib.Namespace(os.getenv("MODEL_NAMESPACE"))
OXIGRAPH_URI = "http://oxigraph:7878/"
sparql = SPARQLWrapper(OXIGRAPH_URI + "query")
sparql.setReturnFormat(JSON)

spupdate = SPARQLWrapper(OXIGRAPH_URI + "update")
spupdate.setReturnFormat(JSON)

app = FastAPI()

def do_update(query: str):
    return requests.post(OXIGRAPH_URI + "update", headers= {"Content-Type": "application/sparql-update"}, data=query)


@app.get("/points")
async def points() -> list[Point]:
    sparql.setQuery("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX ref: <https://brickschema.org/schema/Brick/ref#>
    SELECT DISTINCT ?point ?type ?unit ?tsid ?on WHERE {
        ?point rdf:type/rdfs:subClassOf* brick:Point .
        ?point rdf:type ?type ;
               brick:hasUnit ?unit ;
               ref:hasExternalReference [
                a ref:TimeseriesReference ;
                ref:hasTimeseriesId ?tsid ;
               ] .
        OPTIONAL { ?point brick:isPointOf ?on } .
    }""")
    ret = sparql.queryAndConvert()
    intermediate_points = []
    ptypes = defaultdict(set)
    for binding in ret["results"]["bindings"]:
        point_on = binding.get('on')
        intermediate_points.append({
            "name": str(binding['point']['value']),
            "unit": str(binding['unit']['value']),
            "tsid": str(binding['tsid']['value']),
            "on": str(point_on['value']) if point_on else None,
        })
        ptypes[intermediate_points['name']].add(str(binding['type']['value']))

    points = []
    for p in intermediate_points:
        points.append(Point(
            **p.update({'types': sorted(ptypes[p['name']])})
        ))
    return points


@app.post("/register")
async def register(point: Point):
    name = NS[point.name]
    unit = NS[point.unit]
    types = [BRICK[t] for t in point.types]
    if point.tsid is None:
        point.tsid = str(uuid.uuid4())
    tsid = rdflib.Literal(point.tsid)

    update = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX ref: <https://brickschema.org/schema/Brick/ref#>
    INSERT DATA {{
        {name.n3()} a brick:Point, {types[0].n3()} .
        {name.n3()} brick:hasUnit {unit.n3()} .
        {name.n3()} ref:hasExternalReference _:b0
        _:b0 a ref:TimeseriesReference .
        _:b0 ref:hasTimeseriesId {tsid.n3()} .
    }}"""
    print(update)
    print(do_update(update).content)
