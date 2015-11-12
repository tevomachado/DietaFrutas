#!/usr/bin/python

from py2neo import neo4j
from py2neo import Graph
import math

nutrientes = []
mediaNutrientes = []
faixaEtaria = []
qtIdeal = []
mediaNutrientesNormalizado = []
qtIdealNormalizado = []

graph_db = neo4j.Graph("http://localhost:7474/db/data/")

#recupera os nutrientes do grafo
results = graph_db.cypher.execute('MATCH (n:Nutriente) WHERE n.id <> \'Zinc\' AND n.id <> \'Vitamin_B_12\' AND n.id <> \'Vitamin_D\' RETURN n.id ORDER BY(n.id)')
for result in results:
	nutrientes.append(result[0])

results = graph_db.cypher.execute('MATCH (f:FaixaEtaria) RETURN f.id')
for result in results:
	faixaEtaria.append(result[0])
	
for fe in faixaEtaria:
	print fe
	for nutriente in nutrientes:
		results = graph_db.cypher.execute('MATCH (:Alimento)-[r:contem]->(:Nutriente {id: \'' + nutriente + '\'}) RETURN AVG(r.quantidade)')	
		mediaNutrientes.append(results[0][0])
		results2 = graph_db.cypher.execute('MATCH (f:FaixaEtaria {id:\'' + fe + '\'})-[p:precisa]->(n:Nutriente {id: \'' + nutriente + '\'}) RETURN p.quantidadeideal')
		qtIdeal.append(results2[0][0])
	for i in range(len(mediaNutrientes)):
		print nutrientes[i],int(math.ceil(qtIdeal[i]/mediaNutrientes[i]))
	del mediaNutrientes[:]
	del qtIdeal[:]

