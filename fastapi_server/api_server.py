# api_server.py
from fastapi import FastAPI, HTTPException, status, Request
import mysql.connector
from datetime import datetime
from db_schema import RegistroFalla # Nota: Este modelo ya no necesita el campo id_usuario
from geo import LocalizadorColonias 

app = FastAPI()

# --- Configuración de Conexión a MySQL ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "GioMax102._.", 
    "database": "db_smart_city"
}

localizador_geo = LocalizadorColonias()

def get_db_connection():
    """Establece y retorna una conexión a la BD."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Error de conexión a MySQL: {err}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Servicio de base de datos no disponible. Revisar logs del servidor."
        )

# --- FUNCIÓN CENTRAL: OBTENER O CREAR USUARIO POR IP ---
def get_or_create_user_id(cursor, ip_dispositivo: str) -> int:
    """Busca un usuario por IP. Si no existe, lo crea y devuelve su ID."""
    
    # 1. Búsqueda
    cursor.execute("SELECT id_usuario FROM USUARIOS WHERE ip_dispositivo = %s", (ip_dispositivo,))
    resultado = cursor.fetchone()

    if resultado:
        return resultado[0]
    
    # 2. Creación (Si no existe)
    query_insert_user = """
    INSERT INTO USUARIOS (ip_dispositivo, tipo_usuario)
    VALUES (%s, 'Dispositivo Cámara')
    """
    cursor.execute(query_insert_user, (ip_dispositivo,))
    
    # 3. Devolver el ID recién creado
    return cursor.lastrowid


# --- 1. Endpoint: REGISTRAR FALLA (POST) ---
@app.post("/api/registrar_falla/")
def registrar_falla(registro: RegistroFalla, request: Request):
    """
    Recibe datos, genera el usuario (si es nuevo) y registra la falla.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Obtener la IP del dispositivo (El identificador del usuario)
        ip_dispositivo = request.client.host

        # --- A. OBTENER/CREAR USUARIO ---
        id_usuario_encontrado = get_or_create_user_id(cursor, ip_dispositivo)

        # --- B. Geocodificación y Búsqueda de IDs ---
        nombre_colonia = localizador_geo.obtener_colonia_por_coordenadas(registro.latitud, registro.longitud)
        
        # B1. ID Colonia
        cursor.execute("SELECT id_colonia FROM COLONIAS WHERE nombre_colonia = %s", (nombre_colonia,))
        resultado_colonia = cursor.fetchone()
        if resultado_colonia is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Colonia '{nombre_colonia}' no encontrada.")
        id_colonia_encontrada = resultado_colonia[0]
        
        # B2. ID Tipo Falla
        cursor.execute("SELECT id_tipo_falla FROM TIPOS_FALLAS WHERE nombre_falla = %s", (registro.nombre_falla_detectada,))
        resultado_tipo_falla = cursor.fetchone()
        if resultado_tipo_falla is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tipo de falla '{registro.nombre_falla_detectada}' no existe.")
        id_tipo_falla_encontrado = resultado_tipo_falla[0]
        
        # --- C. Inserción del registro ---
        query_falla = """
        INSERT INTO REGISTROS_FALLAS (
            id_usuario,
            id_colonia, 
            id_tipo_falla, 
            latitud, 
            longitud, 
            fecha_hora_deteccion, 
            nivel_confianza, 
            estado_reparacion, 
            url_imagen
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        valores_falla = (
            id_usuario_encontrado,           # 1. id_usuario (Obtenido de la función)
            id_colonia_encontrada,           # 2. id_colonia
            id_tipo_falla_encontrado,        # 3. id_tipo_falla
            registro.latitud,                # 4. latitud
            registro.longitud,               # 5. longitud
            datetime.now(),                  # 6. fecha_hora_deteccion
            registro.nivel_confianza,        # 7. nivel_confianza
            'Pendiente',                     # 8. estado_reparacion
            registro.url_imagen              # 9. url_imagen
        )

        cursor.execute(query_falla, valores_falla)
        conn.commit()
        
        return {
            "mensaje": "Falla registrada exitosamente", 
            "id_registro": cursor.lastrowid, 
            "id_usuario_asignado": id_usuario_encontrado
        }
    
    # Manejo de Errores (sin cambios)
    except ValueError as ve:
        conn.rollback() 
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=f"Falla en geocodificación: {ve}")
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        print(f"Error interno durante la inserción/procesamiento: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor.")
    finally:
        cursor.close()
        conn.close()


# --- 2. Endpoint: CONSULTAR REGISTROS (GET) ---
@app.get("/api/dispositivo/registros_totales")
def obtener_registros_por_dispositivo(request: Request):
    """Permite que un dispositivo consulte la cantidad total de fallas que ha reportado usando su IP."""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        ip_dispositivo = request.client.host
        
        # 1. Obtener el id_usuario asociado a la IP
        cursor.execute("SELECT id_usuario FROM USUARIOS WHERE ip_dispositivo = %s", (ip_dispositivo,))
        resultado_user = cursor.fetchone()

        if resultado_user is None:
            return {
                "ip_dispositivo": ip_dispositivo,
                "total_registros_reportados": 0,
                "mensaje": "Dispositivo no encontrado. Reporte una falla primero."
            }
        
        id_usuario = resultado_user[0]
        
        # 2. Contar los registros de ese usuario
        query_count = """
        SELECT COUNT(id_registro) 
        FROM REGISTROS_FALLAS 
        WHERE id_usuario = %s
        """
        cursor.execute(query_count, (id_usuario,))
        total_registros = cursor.fetchone()[0]
        
        return {
            "ip_dispositivo": ip_dispositivo,
            "id_usuario": id_usuario,
            "total_registros_reportados": total_registros
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al consultar registros de usuario: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al consultar la base de datos.")
    finally:
        cursor.close()
        conn.close()

@app.get("/")
def home():
    return {"status": "Servidor de Ingesta de Fallas Activo"}