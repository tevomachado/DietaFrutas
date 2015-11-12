#!/usr/bin/env python

from py2neo import neo4j
from py2neo import Graph
from itertools import combinations

graph_db = neo4j.Graph("http://localhost:7474/db/data/")
query = 'MATCH (f:FaixaEtaria) RETURN f.id'
resultFaixas = graph_db.cypher.execute(query)
for resFaixa in resultFaixas:
  query = ('MATCH (f:FaixaEtaria {id: \''+str(resFaixa[0])+'\'})-[r]->(n) WHERE n.id <> \'Vitamin_D\' AND n.id <> \'Vitamin_B_12\' AND n.id <> \'Zinc\' RETURN n.id,r.quantidadeideal,r.quantidademax ORDER BY n.id')
  resultNutrientes = graph_db.cypher.execute(query)
  listaAlimentos = []
  nomesNutrientes = [x for x in range(len(resultNutrientes))]
  qtidealNutrientes = [x for x in range(len(resultNutrientes))]
  qtmaxNutrientes = [x for x in range(len(resultNutrientes))]
  alimentosIdeais = [x for x in range(len(resultNutrientes))]
  qtAlimentosIdeais = [x for x in range(len(resultNutrientes))]

  for n in range(len(resultNutrientes)):
    nomesNutrientes[n] = str(resultNutrientes[n][0])
    qtidealNutrientes[n] = float(resultNutrientes[n][1])
    if str(resultNutrientes[n][2]) != 'None':
      qtmaxNutrientes[n] = float(str(resultNutrientes[n][2]))
    else:
      qtmaxNutrientes[n] = -1

  for nut in range(len(nomesNutrientes)):
    query = 'MATCH (a:Alimento)-[r]->(n {id: \''+nomesNutrientes[nut]+'\'}) WITH max(r.quantidade) as maxqt MATCH (b)-[s]->(n) WHERE s.quantidade = maxqt RETURN b.id, maxqt'
    resultAlimentoIdeal = graph_db.cypher.execute(str(query))
    alimentosIdeais[nut] = str(resultAlimentoIdeal[0][0])
    qtAlimentosIdeais[nut] = str(resultAlimentoIdeal[0][1])

  alimentosIdeaisDistintos = []
  qtAlimentosIdeaisDistintos = []
  for i in range(len(alimentosIdeais)):
    alimExist = False
    for j in alimentosIdeaisDistintos:
      if alimentosIdeais[i] == j:
	alimExist = True
	break
    if alimExist == False:
      alimentosIdeaisDistintos.append(alimentosIdeais[i])
      qtAlimentosIdeaisDistintos.append(qtAlimentosIdeais[i])

  somasNutrientes = [0 for x in range(len(resultNutrientes))]
  for i in range(len(alimentosIdeaisDistintos)):
    query = 'MATCH (a:Alimento {id:\''+alimentosIdeaisDistintos[i]+'\'})-[r]->(n) WHERE n.id <> \'Vitamin_D\' AND n.id <> \'Vitamin_B_12\' AND n.id <> \'Zinc\' RETURN n.id, r.quantidade ORDER BY n.id'
    resultAlimentoIdeal = graph_db.cypher.execute(str(query))
    for j in range(len(resultAlimentoIdeal)):
      nut = 0
      while resultAlimentoIdeal[j][0] != nomesNutrientes[nut]:
	nut += 1
      somasNutrientes[nut] += float(str(resultAlimentoIdeal[j][1]))
      nut += 1

  quantidadeFaltante = [x for x in range(len(resultNutrientes))]
  for nut in range(len(somasNutrientes)):
    if somasNutrientes[nut] >= qtidealNutrientes[nut]:
      quantidadeFaltante[nut] = 0
    else:
      quantidadeFaltante[nut] = qtidealNutrientes[nut] - somasNutrientes[nut]

  for nut in range(len(nomesNutrientes)):
    somaNutAtual = somasNutrientes[nut]
    if somaNutAtual < qtidealNutrientes[nut]:
      query = 'MATCH (a:Alimento)-[r]->(n {id:\''+nomesNutrientes[nut]+'\'}) RETURN a.id, r.quantidade ORDER BY r.quantidade DESC'
      resultAlimentosFaltantes = graph_db.cypher.execute(str(query))
      for a in range(len(resultAlimentosFaltantes)):
	nomeAlimento = str(resultAlimentosFaltantes[a][0])
	if somaNutAtual >= qtidealNutrientes[nut]:
	  break
	elif nomeAlimento not in alimentosIdeaisDistintos:
	  alimentosIdeaisDistintos.append(nomeAlimento)
	  query = 'MATCH (a:Alimento {id:\''+nomeAlimento+'\'})-[r]->(n) WHERE n.id <> \'Vitamin_D\' AND n.id <> \'Vitamin_B_12\' AND n.id <> \'Zinc\' RETURN n.id, r.quantidade ORDER BY n.id'
	  resultNomeAlimento = graph_db.cypher.execute(str(query))
	  for j in range(len(resultNomeAlimento)):
	    n = 0
	    while resultAlimentoIdeal[j][0] != nomesNutrientes[n]:
	      n += 1
	    somasNutrientes[n] += float(str(resultNomeAlimento[j][1]))
	    n += 1
	  somaNutAtual = somasNutrientes[nut]

  for ali in alimentosIdeaisDistintos:
    query = 'MATCH (f:FaixaEtaria {id:\''+str(resFaixa[0])+'\'}),(a:Alimento {id:\''+ali+'\'}) CREATE (f)-[:seAlimenta]->(a)'
    result = graph_db.cypher.execute(str(query))