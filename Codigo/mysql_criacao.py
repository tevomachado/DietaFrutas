#!/usr/bin/python
import MySQLdb
import sys

db = MySQLdb.connect(host="localhost", user="root", passwd="root", db="projetoBD") 
cur = db.cursor()

cur.execute("DROP TABLE IF EXISTS FaixaEtaria")
cur.execute("CREATE TABLE FaixaEtaria (id_idade VARCHAR(80) NOT NULL, PRIMARY KEY (id_idade))")

cur.execute("DROP TABLE IF EXISTS Alimento")
cur.execute("CREATE TABLE Alimento (id_alimento VARCHAR(80) NOT NULL,PRIMARY KEY (id_alimento))")

cur.execute("DROP TABLE IF EXISTS Nutriente")
cur.execute("CREATE TABLE Nutriente (id_nutriente VARCHAR(80) NOT NULL,PRIMARY KEY (id_nutriente))")

cur.execute("DROP TABLE IF EXISTS Alimento_Nutriente")
cur.execute("CREATE TABLE Alimento_Nutriente (id_alimento VARCHAR(80) NOT NULL, id_nutriente VARCHAR(80) NOT NULL, quantidade FLOAT(10,1), PRIMARY KEY (id_alimento, id_nutriente), FOREIGN KEY (id_alimento) REFERENCES Alimento(id_alimento), FOREIGN KEY (id_nutriente) REFERENCES Nutriente (id_nutriente))")

cur.execute("DROP TABLE IF  EXISTS FaixaEtaria_Nutriente")
cur.execute("CREATE TABLE FaixaEtaria_Nutriente (id_nutriente VARCHAR(80) NOT NULL, id_idade VARCHAR(80) NOT NULL, quantidade_ideal FLOAT(11,1), quantidade_maxima FLOAT(11,1), PRIMARY KEY (id_idade, id_nutriente), FOREIGN KEY (id_idade) REFERENCES FaixaEtaria (id_idade), FOREIGN KEY (id_nutriente) REFERENCES Nutriente (id_nutriente))")

entrada = raw_input('Entre com o arquivo: ')

file = open(entrada,'r')

contents = file.readlines()


# Use all the SQL you like
for content in contents:
  try:
    cur.execute(content)
  except:
    print "comando repetido: ", content
    continue
db.commit()