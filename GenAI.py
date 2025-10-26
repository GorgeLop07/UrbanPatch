from google import genai
from google.genai import types
from pdf import pdf_builder
import json 
from flask import Flask
import requests

#server stuff
rute = "http://10.22.229.101:8001/api/reportes/top_10_colonias"

# GET request
#response_get = requests.get(rute)
#response_json = response_get.json()


API_KEY = "AIzaSyBFqFPO6h7F88h4J_cFA6_Wpgs_DBqmyjY"
client = genai.Client(api_key=API_KEY)
responses = []

#JSON READ:
    #from file
with open('test.json', 'r') as file:
    response_json = json.load(file)

data = response_json
No_colonias = 10  #total colonias

nombres = []

for i in range(No_colonias):
    faltas_criticas = 0
    faltas_altas = 0
    faltas_bajas = 0

    nombre_col = data["top_10_colonias"][i]["nombre_colonia"]
    nombres.append(str(nombre_col))
    total_reportes = data["top_10_colonias"][i]["total_fallas"]
    costo_reparacion = total_reportes*450



    responses.append(client.models.generate_content(
    model = "gemini-2.5-flash-lite",

    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0), # Disables thin]king
        #settings:
        #temperature=0.2
        system_instruction=
        ("Eres un trabajador bancario y necesitas realizar un reporte para una colonia con problemas de infraestructura "
         "la respuesta tiene una estructura definida ejemplificada despues las variables usadas son: Nombre colonia, cantidad de fallas, costo de arreglar fallas"
         "en la siguiente parte usa la reparación completa proveida")
    ),
    contents= f'''has un pequeño parrafo sobre los problemas de infraestructura relacionados con pavimentación
    Aqui hay un ejemplo de como estructurarlo:

    La colonia Benito Juarez a recibido reporte de 10 fallas
    El costo total aproximado para arreglar todas las fallas es de 3200 pesos

    VARIABLES: nombre colonia = {nombre_col}, total reportes = {total_reportes},  costo de reparación {costo_reparacion}
    Con los datos anteriores genera un parrafo corto extra sobre la infraestructura en la colonia de una forma mas interpretativa, haslo de forma profesional y no inventes información'''
    ))

pdf_builder(No_colonias, responses, nombres)
#(responses[i]).text , asi accede a la respuesta por colonia.