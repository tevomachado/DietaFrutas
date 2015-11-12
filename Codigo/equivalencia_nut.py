#!/usr/bin/env python

# ***********************************************************
# o programa cria as relacoes de equivalencia entre alimentos
# baseando-se nas quantidades de cada nutriente que cada
# alimento contem  
# ***********************************************************

from py2neo import neo4j
from py2neo import Graph

nutrientes = []

graph_db = neo4j.Graph("http://localhost:7474/db/data/")

#recupera os nutrientes do grafo
results = graph_db.cypher.execute('Match (n:Nutriente) return n.id')
for result in results:
	nutrientes.append(result[0])

#para cada nutriente, cria os vetores alimentos e suas respectivas quantidades
for nutriente in nutrientes:
	alimentos = []
	quantidades = []
	results = graph_db.cypher.execute('Match (a:Alimento)-[r:contem]->(n:Nutriente {id: \''+nutriente+'\'}) where r.quantidade > 0 return a.id,r.quantidade order by(r.quantidade)')
	for result in results:
		alimentos.append(result[0])
		quantidades.append(result[1])

	#cria as realcoes de equivalencia entre alimentos dado um diferenca de 10%
	#entre as quantidades eh considerada uma equivalencia
	for i in range(len(alimentos)):
		for j in range(len(alimentos)):
			try:
				if quantidades[i] * 1.1 >= quantidades[j + i + 1]:
					print 'MATCH (a:Alimento),(b:Alimento) WHERE a.id = \''+alimentos[i]+'\' AND b.id = \''+alimentos[i + j + 1]+'\' CREATE (a)-[:equivale {id: \''+nutriente+'\'}]->(b) CREATE (b)-[:equivale {id: \''+nutriente+'\'}]->(a)'
				else:
					break
			except:
				pass
	