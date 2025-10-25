# api_server.py
from fastapi import FastAPI, HTTPException, status
import mysql.connector
from datetime import datetime
from db_schema import RegistroFalla
from geo import LocalizadorColonias 

app = FastAPI()

# --- Configuración de Conexión a MySQL (REEMPLAZAR) ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "GioMax102._.", # Asegúrate de que esta credencial sea correcta
    "database": "db_smart_city" # Asegúrate de que esta base de datos exista
}

# Inicializamos el localizador (instancia de la clase) una sola vez al inicio.
localizador_geo = LocalizadorColonias()


def get_db_connection():
    """Establece y retorna una conexión a la BD."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        # Imprime el error real en el log del servidor
        print(f"Error de conexión a MySQL: {err}")
        # Lanza un error HTTP 503 para el cliente (cámara Android)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Servicio de base de datos no disponible. Revisar logs del servidor."
        )

# --- Endpoint principal de Ingesta (POST) ---
@app.post("/api/registrar_falla/")
def registrar_falla(registro: RegistroFalla):
    """
    Recibe datos de Android, los geocodifica, 
    busca los IDs de colonia y tipo de falla, e inserta el registro en MySQL.
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # --- 1. Geocodificación (Obtener nombre de la Colonia) ---
        nombre_colonia = localizador_geo.obtener_colonia_por_coordenadas(
            registro.latitud, 
            registro.longitud
        )

        # --- 2. Búsqueda de id_colonia (por nombre) ---
        cursor.execute("SELECT id_colonia FROM COLONIAS WHERE nombre_colonia = %s", 
                       (nombre_colonia,))
        resultado_colonia = cursor.fetchone()

        if resultado_colonia is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Colonia '{nombre_colonia}' no encontrada en el catálogo MySQL."
            )
            
        id_colonia_encontrada = resultado_colonia[0]
        
        # --- 3. Búsqueda de id_tipo_falla (por nombre de YOLO) ---
        # Aseguramos la integridad referencial (Foreign Key)
        cursor.execute("SELECT id_tipo_falla FROM TIPOS_FALLAS WHERE nombre_falla = %s", 
                       (registro.nombre_falla_detectada,))
        resultado_tipo_falla = cursor.fetchone()

        if resultado_tipo_falla is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Tipo de falla '{registro.nombre_falla_detectada}' no existe en el catálogo MySQL."
            )
            
        id_tipo_falla_encontrado = resultado_tipo_falla[0]
        
        # --- 4. Inserción del registro (Query y Orden Corregidos) ---
        
        # El orden de las columnas DEBE COINCIDIR con el orden de valores_falla
        query_falla = """
        INSERT INTO REGISTROS_FALLAS (
            id_colonia, 
            id_tipo_falla, 
            latitud, 
            longitud, 
            fecha_hora_deteccion, 
            nivel_confianza, 
            estado_reparacion, 
            url_imagen
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Definición de los valores en el ORDEN CORRECTO
        valores_falla = (
            id_colonia_encontrada,           # 1. id_colonia
            id_tipo_falla_encontrado,        # 2. id_tipo_falla
            registro.latitud,                # 3. latitud
            registro.longitud,               # 4. longitud
            datetime.now(),                  # 5. fecha_hora_deteccion
            registro.nivel_confianza,        # 6. nivel_confianza
            'Pendiente',                     # 7. estado_reparacion (Valor fijo de inicio)
            registro.url_imagen              # 8. url_imagen
        )

        cursor.execute(query_falla, valores_falla)
        conn.commit()
        
        return {
            "mensaje": "Falla registrada exitosamente", 
            "id_registro": cursor.lastrowid, # Retornamos el ID de la falla recién creada
            "id_colonia_asignada": id_colonia_encontrada
        }
    
    # --- Manejo de Errores ---
    except ValueError as ve:
        conn.rollback() 
        # Falla en Nominatim o procesamiento de geocodificación
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY, 
            detail=f"Falla en servicio de geocodificación (Nominatim): {ve}"
        )
    
    except HTTPException:
        conn.rollback()
        raise # Relanza los errores 404
        
    except Exception as e:
        conn.rollback()
        print(f"Error interno durante la inserción/procesamiento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error interno del servidor. Verifique logs para detalles."
        )
    
    finally:
        # Asegura que la conexión y el cursor se cierren siempre
        cursor.close()
        conn.close()

@app.get("/")
def home():
    return {"status": "Servidor de Ingesta de Fallas Activo"}