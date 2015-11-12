#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
import re

url = "https://www.consumerlab.com/rdas/"
req = requests.get(url)
soup = BeautifulSoup(req.content, 'lxml')
tables = soup.find_all("table", {"class" : "reviewTable"})
vetor_site1 = []

table = tables[0]
lines = table.find_all("tr") # pega todas as linhas
for line in lines:
  if line == lines[0]:
    continue
  cols = line.find_all("a")
  for col in cols:	#faz uma iteracao por nome de nutriente
    vetor_site1.append(col.text)

# *************************************************
# Script Cypher
# *************************************************
fn = open("comandos_cypher.txt", "wb+")

# *************************************************
#Segundo site 
# *************************************************

vetor_alimentos = []
vetor_nutrientes = []
nutriente_existente = False

#iteracao nas paginas dos alimentos
for page in range(0,14):
  url = "http://ndb.nal.usda.gov/ndb/?format=&count=&max=25&sort=fd_s&fg=Fruits+and+Fruit+Juices&man=&lfacet=&qlookup=&offset="+str(page*25)+"&order=asc"
  req = requests.get(url)
  soup = BeautifulSoup(req.content, 'lxml')
  name_aux = ""
  col_aux=""

  # tabela com a lista de alimentos
  table = soup.find_all("div", {"class": "wbox"})
  lines = table[0].find_all("tr")


  for line in lines:
    # pula a primeira linha
    if line == lines[0]:
      continue
    
    cols = line.find_all("td")	# guarda todas as colunas da tabela
    col_nut = cols[1].find_all("a") 
    name_cleaned = re.sub(',.*', '', col_nut[0].text) #imprime apenas o nome do alimento, na tabela ha outros campos apos o nome
    
    alimento_existente=False
    for indice_alimentos in range(len(vetor_alimentos)):
      if name_cleaned == vetor_alimentos[indice_alimentos]:
        alimento_existente=True
        break
    if alimento_existente==False and not "USDA" in name_cleaned:	#verifica se consiste em um alimento novo
      #********************* Cypher command ************************
      alim_aux = name_cleaned
      alim_aux = re.sub('( )|(\-)','_', alim_aux)
      alim_aux = re.sub('(\()|(\))','', alim_aux)
      command = "CREATE (:Alimento { id: \'" + alim_aux + "\'})\n"
      fn.write(command)
      #********************* Cypher command ************************ 
      vetor_alimentos.append(name_cleaned)
      print "INSERT INTO Alimento VALUES (\'"+name_cleaned+"\');"
      url = "http://ndb.nal.usda.gov"+col_nut[0].get("href")	#pega o link do alimento
      req = requests.get(url)
      soup = BeautifulSoup(req.content, 'lxml')
      table2 = soup.find_all("div", {"class": "nutlist"})
      lines2 = table2[0].find_all("tr")	#ha apenas uma table
      for line2 in range(len(lines2)): # quantidade de linhas da tabela
	cols = lines2[line2].find_all("td") # colunas de cada linha
	if "Minerals" in cols[0].text:	# busca apenas as vitaminas
	  for line3 in range(line2+1, len(lines2)):	#comeca da linha seguinte
	    col = lines2[line3].find_all("td")	# todas as colunas da linha
	    col_cleaned = re.sub("(\r)|(\n)|(\t)|(,.*)|( \(.*)", '',col[0].text) # elimina caracteres indesejados
	    #col_cleaned = re.sub('-', '', col_cleaned)
	    # pula a coluna que possui apenas a separacao
	    if "Vitamins" in col_cleaned:
	      continue
	    # para nos lipids
	    if "Lipids" in col_cleaned:
	      break	  
	    if col_cleaned != col_aux: # nao repete o nutriente
	      # adiciona apenas nutrientes que estejam no primeiro site
	      nut_valido = False
	      for nut in vetor_site1:
		# se achar um valido, pode adicionar
		if col_cleaned == nut:
		  nut_valido = True
		  break
	      # verifica se o nutriente esta no primeiro site
	      if nut_valido==True:
		nutriente_existente=False
		for indice_nutriente in range(len(vetor_nutrientes)): # verifica se o nutriente ja existe no vetor
		  if col_cleaned == vetor_nutrientes[indice_nutriente]:
		    nutriente_existente=True
		    break
		if nutriente_existente==False: # se nao existir, adiciona no vetor de nutrientes existentes e cria o nutriente no banco
		   # ********************* Cypher command ************************
		   nut = re.sub('( )|(\-)','_', nut)
		   command = "CREATE (:Nutriente { id: \'" + nut + "\'})\n"
		   fn.write(command)
		   # ********************* Cypher command ************************
		   vetor_nutrientes.append(col_cleaned)
		   print "INSERT INTO Nutriente VALUES (\'" + col_cleaned + "\');"
		col_aux = col_cleaned
		mult = 1
		if col[1].text == 'mg':
		  mult = 1000
		elif col[1].text == 'g':
		  mult = 1000000
		elif col[1].text == 'IU':
		  if col_cleaned == 'Vitamin A':
		    mult = 0.3
		  elif col_cleaned == 'Vitamin C':
		    mult = 50
		  elif col_cleaned == 'Vitamin D':
		    mult = 0.025
		  elif col_cleaned == 'Vitamin E':
		    mult = 0.667
		print "INSERT INTO Alimento_Nutriente VALUES (\'" +name_cleaned+"\',\'" + col_cleaned + "\',", float(re.sub(' *','', col[2].text))*mult, ");"
		# ********************* Cypher command ************************
		nut = re.sub('( )|(\-)','_', nut)
		command = "MATCH (a:Alimento),(n:Nutriente) WHERE a.id = \'" + alim_aux + "\' AND n.id = \'" + nut + "\' CREATE (a)-[:contem {quantidade:" + str(float(re.sub(' *','', col[2].text))*mult) + "}]->(n)\n"
		fn.write(command) 
		# ********************* Cypher command ************************
	  break

# *************************************************
#Primeiro site 
# *************************************************

url = "https://www.consumerlab.com/rdas/"
req = requests.get(url)
soup = BeautifulSoup(req.content, 'lxml')
tables = soup.find_all("table", {"class" : "reviewTable"})
vetor_site1 = []
faixascriadas = 0

for table in tables:
  if table == tables[0]:	#primeira tabela nao contem informacoes
    continue
  lines = table.find_all("tr")
  cols_0 = lines[0].find_all("td")
  for col in range(len(cols_0)):	#faz uma iteracao por nome de nutriente
    col_names = cols_0[col].find_all("strong") #obtem os nomes dos nutrientes
    for line in range(len(lines)):
      if col == 0:
	continue
      if line == 1 or line == 0:
	continue
      cols = lines[line].find_all("td")
      for col_inline in range(len(cols)):	#analisa coluna por coluna da linha de index 'line' de table
	if col_inline == col:
	  try:
	    cells_idade = cols[0].find_all("center")
	    cells_idade_cleaned = re.sub('(\r\n)|(\n)|(\t)|(  ).*', '', cells_idade[0].text)
	    nobr = re.findall('.*nobr.*',str(cells_idade[0]))
	    if len(nobr)>0:
	      cells_idade_cleaned = '14 - 18'
	    if cells_idade_cleaned == '1 - 3':
	      cells_idade_cleaned = 'Toddler'
	    elif cells_idade_cleaned == '4 - 8':
	      cells_idade_cleaned = 'Child'
	    elif cells_idade_cleaned == '9 - 13':
	      cells_idade_cleaned = 'Preteenager'
	    elif cells_idade_cleaned == '14 - 18':
	      cells_idade_cleaned = 'Teenager'
	    if faixascriadas < 5:
	      faixascriadas += 1
	      print 'INSERT INTO FaixaEtaria VALUES (\''+cells_idade_cleaned+'\');'
	      command = "CREATE (:FaixaEtaria { id: \'"+cells_idade_cleaned+"\'})\n"
	      fn.write(command)
	    #etapa que tira os caracteres inuteis dos valores das tabelas
	    col_names_cleaned = re.sub('(See Report).*', '', col_names[0].text)
	    col_names_cleaned = re.sub('\(.*', '', col_names_cleaned)
	    col_names_cleaned = re.sub(' *$', '', col_names_cleaned)	  
	    cells_mg = cols[col + (col - 1)].find_all("center")	#tabela alinhada, calculo para obter os dados referentes a cada nutriente
	    cells_mg_cleaned = re.sub('(  )*', '', cells_mg[0].text)
	    cells_mg_cleaned = re.sub('(\r\n)|(\n)|(\t)|(  ).*', '', cells_mg_cleaned)
	    cells_mg_cleaned = re.sub('(g)+.*', 'g', cells_mg_cleaned)
	    cells_mg_cleaned = re.sub('(IU)+.*', 'IU', cells_mg_cleaned)
	    cells_mg_cleaned = re.sub(',', '', cells_mg_cleaned)
	    valoridealprocura = re.findall('[0-9]+[.]*[0-9]*',cells_mg_cleaned)
	    valorideal = valoridealprocura[0]
	    unidadeideal = re.sub('[0-9]+[.]*[0-9]*[ ]*', '',cells_mg_cleaned)
	    multideal = 1
	    if unidadeideal == 'mg':
	      multideal = 1000
	    elif unidadeideal == 'g':
	      multideal = 1000000
	    elif unidadeideal == 'IU':
	      if col_names_cleaned == 'Vitamin A':
		multideal = 0.3
	      elif col_names_cleaned == 'Vitamin C':
		multideal = 50
	      elif col_names_cleaned == 'Vitamin D':
		multideal = 0.025
	      elif col_names_cleaned == 'Vitamin E':
		multideal = 0.667
	    cells_upper = cols[col + col].find_all("center")
	    cells_upper_cleaned = re.sub('(\r\n)|(\n)|(\t)|(  ).*', '', cells_upper[0].text)
	    cells_upper_cleaned = re.sub('(g)+.*', 'g', cells_upper_cleaned)
	    cells_upper_cleaned = re.sub('(IU)+.*', 'IU', cells_upper_cleaned)
	    cells_upper_cleaned = re.sub(',', '', cells_upper_cleaned)
	    cells_upper_cleaned = re.sub('.*NE.*','NULL', cells_upper_cleaned)	#substituir NE por null
	    if cells_upper_cleaned != 'NULL':
	      valormaximoprocura = re.findall('[0-9]+[.]*[0-9]*',cells_upper_cleaned)
	      valormaximo = valormaximoprocura[0]
	      unidademaximo = re.sub('[0-9]+[.]*[0-9]*[ ]*', '',cells_upper_cleaned)
	      multmaximo = 1
	      if unidademaximo == 'mg':
		multmaximo = 1000
	      elif unidademaximo == 'g':
		multmaximo = 1000000
	      elif unidademaximo == 'IU':
		if col_names_cleaned == 'Vitamin A':
		  multmaximo = 0.3
		elif col_names_cleaned == 'Vitamin C':
		  multmaximo = 50
		elif col_names_cleaned == 'Vitamin D':
		  multmaximo = 0.025
		elif col_names_cleaned == 'Vitamin E':
		  multmaximo = 0.667
	      #ao final ha apenas os valores e unidade
	    col_names_cleaned = re.sub('Vitamin B6', 'Vitamin B-6', col_names_cleaned)	#corrigir Vitamin B6
	    for nutriente in vetor_nutrientes:
	      if nutriente == col_names_cleaned:
		try:	
		  col_names_cleaned_cypher = re.sub('( )|(\-)','_', col_names_cleaned)
		  if cells_upper_cleaned != 'NULL':
		    fn.write("MATCH (f:FaixaEtaria),(n:Nutriente) WHERE f.id = \'" + cells_idade_cleaned + "\' AND n.id = \'" + col_names_cleaned_cypher + "\' CREATE (f)-[:precisa {quantidadeideal: "+str(float(valorideal)*multideal)+", quantidademax: "+str(float(valormaximo)*multmaximo)+"}]->(n)\n")
		    print 'INSERT INTO FaixaEtaria_Nutriente VALUES (\''+col_names_cleaned+'\',\''+cells_idade_cleaned+'\',',float(valorideal)*multideal,',',float(valormaximo)*multmaximo,');'
		  else:
		    fn.write("MATCH (f:FaixaEtaria),(n:Nutriente) WHERE f.id = \'" + cells_idade_cleaned + "\' AND n.id = \'" + col_names_cleaned_cypher + "\' CREATE (f)-[:precisa {quantidadeideal: "+str(float(valorideal)*multideal)+"}]->(n)\n")
		    print 'INSERT INTO FaixaEtaria_Nutriente VALUES (\''+col_names_cleaned+'\',\''+cells_idade_cleaned+'\',',float(valorideal)*multideal,',NULL);'
		except:
		  col_names_cleaned_cypher = re.sub('( )|(\-)','_', col_names_cleaned)
		  cells_idade = cols[0].find_all("nobr")
		  cells_idade_cleaned = re.sub('(\r\n)|(\n)|(\t)|(  ).*', '', cells_idade[0].text)
		  if cells_upper_cleaned != 'NULL':
		    fn.write("MATCH (f:FaixaEtaria),(n:Nutriente) WHERE f.id = \'" + cells_idade_cleaned + "\' AND n.id = \'" + col_names_cleaned_cypher + "\' CREATE (f)-[:precisa {quantidadeideal: "+str(float(valorideal)*multideal)+", quantidademax: "+str(float(valormaximo)*multmaximo)+"}]->(n)\n")
		    print 'INSERT INTO FaixaEtaria_Nutriente VALUES (\''+col_names_cleaned+'\',\''+cells_idade_cleaned+'\',',float(valorideal)*multideal,',',float(valormaximo)*multmaximo,');'
		  else:
		    fn.write("MATCH (f:FaixaEtaria),(n:Nutriente) WHERE f.id = \'" + cells_idade_cleaned + "\' AND n.id = \'" + col_names_cleaned_cypher + "\' CREATE (f)-[:precisa {quantidadeideal: "+str(float(valorideal)*multideal)+"}]->(n)\n")
		    print 'INSERT INTO FaixaEtaria_Nutriente VALUES (\''+col_names_cleaned+'\',\''+cells_idade_cleaned+'\',',float(valorideal)*multideal,',NULL);'
		  continue
	  except:
	   continue
