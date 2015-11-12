#!/usr/bin/env python

from py2neo import neo4j
from py2neo import Graph

graph_db = neo4j.Graph("http://localhost:7474/db/data/")
#entrada = raw_input('Entre com o arquivo: ')
file = open("comandos_cypher.txt",'r')
queries = file.readlines()
for query in queries:
  #print query
  results = graph_db.cypher.execute(query)
  #print results