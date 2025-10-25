# client_device.py
import requests
import json

# --- 1. Simulación de Detección (Reemplaza esto con tu lógica de YOLO real) ---
def simular_deteccion_yolo():
    """Simula el resultado de la detección de YOLO"""
    
    # 1. Obtener datos de GPS (Reemplazar con lectura real de módulo GPS)
    latitud_gps = 25.6866  # Ejemplo: Latitud de Monterrey
    longitud_gps = -100.3161 # Ejemplo: Longitud de Monterrey
    
    # 2. Ejecutar YOLO y obtener el resultado
    resultado_yolo = {
        "nombre_falla_detectada": "Bache Profundo", # Resultado de clasificación
        "nivel_confianza": 0.95,
        "coordenadas_caja_del_error": [100, 200, 150, 250] # Información que no enviaremos a la BD, pero es útil.
    }
    
    # 3. Datos adicionales de contexto
    id_colonia_detectada = 5 
    url_imagen_almacenada = None
    #url_imagen_almacenada = "https://tu-storage.com/imagen_falla_123.jpg"

    return {
        "nombre_falla_detectada": resultado_yolo["nombre_falla_detectada"],
        "nivel_confianza": resultado_yolo["nivel_confianza"],
        "latitud": latitud_gps,
        "longitud": longitud_gps,
        "id_colonia": id_colonia_detectada,
        "url_imagen": url_imagen_almacenada
    }

# --- 2. Enviar la Solicitud POST a la API ---
def enviar_registro_a_api(datos):
    """Función para enviar los datos procesados a la API de FastAPI"""
    
    API_URL = "http://10.22.230.120:8000/api/registrar_falla/"  # Reemplazar con la IP de tu servidor
    
    try:
        response = requests.post(API_URL, json=datos)
        
        if response.status_code == 200:
            print(f"✅ Éxito al enviar. Respuesta del servidor: {response.json()}")
        else:
            print(f"❌ Error al enviar. Código: {response.status_code}, Detalle: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: Asegúrate de que el servidor API esté corriendo.")

if __name__ == "__main__":
    datos_de_falla = simular_deteccion_yolo()
    enviar_registro_a_api(datos_de_falla)