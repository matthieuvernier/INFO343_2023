
#!pip install elasticsearch==7.16.3
import elasticsearch

from datetime import datetime
import pandas as pd
from pandasql import sqldf 

#Parametros de conexion al motor de búsqueda Sophia
IP = "search.sophia2.org"
PORT = 9200
USER= ""
PASS= ""

#Parametros de la busqueda
country="chile"
from_="2018-01-01"
to_="2023-12-31"
media_outlets=["emol","cnnchile","lanacion","elciudadano","elmostrador","ciper","latercera","eldinamo",
"ahoranoticiasmega"]

keyword="incendios forestales"
simple_keyword=False

#Conexión a Sophia y búsqueda
es = elasticsearch.Elasticsearch(
    IP,
    #port=PORT,
    http_auth=(USER, PASS)
)

match=""
if (simple_keyword):
    match="match"
else:
    match="match_phrase"

query = { 
    "bool": { 
      "must": [
        {match: { "text":keyword}}

      ],
    "filter": [
        {"range": {
      "date": {
        "gte": from_,
        "lt": to_
      }}},
        { "term":  { "country": country }},
        { "terms":  { "media_outlet": media_outlets }} 
    ]
    }  
}

print("inicio búsqueda...")
res = es.search(index="news", query=query, size=10000)
print("Son %d noticias encontradas..." % res['hits']['total']['value'])

# Guardar los datos en un dataframe y luego un CSV
data = {'id_news':[],'country':[],'media_outlet':[],'url':[],'title':[],'text':[],'date':[],'search':[]}

df = pd.DataFrame(data)  
  
for hit in res['hits']['hits']:
    id_news = hit['_source']['id_news']
    country = hit['_source']['country']
    media_outlet = hit['_source']['media_outlet']
    url = hit['_source']['url']
    title = hit['_source']['title']
    text = hit['_source']['text']
    date = hit['_source']['date']
    search = keyword
    
    new_row = {'id_news':id_news, 'country':country, 'media_outlet':media_outlet, 'url':url, 'title':title, 'text':text, 'date':date, 'search':search}
    
    df = df.append(new_row, ignore_index=True)

#eliminar las noticias duplicadas
df = df.drop_duplicates(subset='url', keep='first')

#guardar en un CSV
nombre_archivo=keyword.replace(' ', '')+"_"+country+"_"+from_+"_"+to_+".csv"
print("El archivo se llama:")
print(nombre_archivo)
df.to_csv("./"+nombre_archivo)

#print tabla
result = sqldf("SELECT media_outlet,count(*) FROM df GROUP BY media_outlet ORDER BY count(*) DESC")
print(result)

