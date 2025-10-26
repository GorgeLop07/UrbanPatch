from google import genai
from google.genai import types
from pdf import pdf_builder
import json 

API_KEY = "AIzaSyBFqFPO6h7F88h4J_cFA6_Wpgs_DBqmyjY"
client = genai.Client(api_key=API_KEY)
responses = []

#JSON READ:
with open('test.json', 'r') as file:
    data = json.load(file)
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
        #temperature=0.5
        system_instruction=
        ("Eres un trabajador bancario y necesitas realizar un reporte para una colonia con problemas de infraestructura "
         "la respuesta tiene una estructura definida ejemplificada despues las variables usadas son: Nombre colonia, cantidad de fallas, costo de arreglar fallas"
         "en la siguiente parte usa la reparación completa proveida")
    ),
    contents= f'''has un pequeño parrafo sobre los problemas de infraestructura relacionados con pavimentación
    Aqui hay un ejemplo de como estructurarlo:

    La colonia Benito Juarez a recibido reporte de 10 fallas
    El costo total aproximado para arreglar todas las fallas es de 3200 pesos    
    
    VARIABLES: nombre colonia = {nombre_col}, total reportes = {total_reportes},  costo de reparación {costo_reparacion}'''
    ))

pdf_builder(No_colonias, responses, nombres)
#(responses[i]).text , asi accede a la respuesta por colonia.