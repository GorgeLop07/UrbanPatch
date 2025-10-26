# api_server.py (Corregido)
from fastapi import FastAPI, HTTPException, status, Request
import mysql.connector
from datetime import datetime, date
from db_schema import RegistroFalla 
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

# --- FUNCIÓN CENTRAL: OBTENER O CREAR USUARIO POR IP (Sin cambios) ---
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

# --- Endpoint 1: REGISTRAR FALLA (POST) ---
@app.post("/api/registrar_falla/")
def registrar_falla(registro: RegistroFalla, request: Request):
    """
    Recibe datos, genera el usuario (si es nuevo) y registra la falla.
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        ip_dispositivo = request.client.host

        # A. OBTENER/CREAR USUARIO
        id_usuario_encontrado = get_or_create_user_id(cursor, ip_dispositivo)

        # B. Geocodificación y Búsqueda de IDs (Colonia y Tipo Falla)
        try:
            nombre_colonia = localizador_geo.obtener_colonia_por_coordenadas(registro.latitud, registro.longitud)
        except ValueError as ve:
            # Captura errores de Nominatim y Geocodificación
            raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=f"Falla en geocodificación: {ve}")

        
        # B1. ID Colonia
        cursor.execute("SELECT id_colonia FROM COLONIAS WHERE nombre_colonia = %s", (nombre_colonia,))
        resultado_colonia = cursor.fetchone()
        if resultado_colonia is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Colonia '{nombre_colonia}' no encontrada en BD.")
        id_colonia_encontrada = resultado_colonia[0]
        
        # B2. ID Tipo Falla
        cursor.execute("SELECT id_tipo_falla FROM TIPOS_FALLAS WHERE nombre_falla = %s", (registro.nombre_falla_detectada,))
        resultado_tipo_falla = cursor.fetchone()
        if resultado_tipo_falla is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tipo de falla '{registro.nombre_falla_detectada}' no existe en BD.")
        id_tipo_falla_encontrado = resultado_tipo_falla[0]
        
        # C. Inserción del registro 
        # *** CORRECCIÓN 1: Eliminada la coma extra al final de las columnas. ***
        query_falla = """
        INSERT INTO REGISTROS_FALLAS (
            id_usuario,
            id_colonia, 
            id_tipo_falla, 
            latitud, 
            longitud, 
            fecha_hora_deteccion, 
            nivel_confianza, 
            estado_reparacion
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        valores_falla = (
            id_usuario_encontrado,           
            id_colonia_encontrada,           
            id_tipo_falla_encontrado,        
            registro.latitud,                
            registro.longitud,               
            datetime.now(),                  
            registro.nivel_confianza,        
            'Pendiente',                                   
        )

        cursor.execute(query_falla, valores_falla)
        conn.commit()
        
        return {
            "mensaje": "Falla registrada exitosamente", 
            "id_registro": cursor.lastrowid, 
            "id_colonia_asignada": id_colonia_encontrada
        }
    
    # Manejo de Errores
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


# --- Endpoint 2: CONSULTAR REGISTROS POR DISPOSITIVO (GET) (Sin cambios) ---
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


# --- Endpoint 3: TOP 10 COLONIAS CON FALLAS ---
@app.get("/api/reportes/top_10_colonias")
def get_top_10_colonias_con_fallas():
    """Devuelve las 10 colonias con más fallas registradas, incluyendo el detalle de cada falla."""
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # La consulta principal selecciona TODAS las columnas necesarias y ordena por el conteo de registros.
        query_top_10 = """
        SELECT 
            C.id_colonia,
            C.nombre_colonia,
            R.*,               -- Selecciona todas las columnas de REGISTROS_FALLAS
            T.nombre_falla AS tipo_falla_nombre,
            T.prioridad AS tipo_falla_prioridad,
            T.descripcion AS tipo_falla_descripcion
        FROM 
            REGISTROS_FALLAS R
        JOIN 
            COLONIAS C ON R.id_colonia = C.id_colonia
        JOIN 
            TIPOS_FALLAS T ON R.id_tipo_falla = T.id_tipo_falla
        ORDER BY 
            (SELECT COUNT(*) FROM REGISTROS_FALLAS WHERE id_colonia = C.id_colonia) DESC
        LIMIT 1000;
        """
        
        cursor.execute(query_top_10)
        resultados_crudos = cursor.fetchall()
        
        if not resultados_crudos:
            return {"mensaje": "No hay registros de fallas para generar el Top 10."}

        # --- Agrupación en Python ---
        
        top_colonias = {}
        
        for row in resultados_crudos:
            colonia_id = row['id_colonia']
            
            # --- Formateo de datos ---
            fecha_deteccion_str = row['fecha_hora_deteccion'].isoformat() if isinstance(row['fecha_hora_deteccion'], (datetime, date)) else None

            # 1. Preparar el detalle de la falla
            # *** CORRECCIÓN 2: Eliminada la referencia a row['url_imagen']. ***
            detalle_falla = {
                "id_registro": row['id_registro'],
                "latitud": float(row['latitud']),
                "longitud": float(row['longitud']),
                "fecha_hora_deteccion": fecha_deteccion_str,
                "nivel_confianza": float(row['nivel_confianza']),
                "estado_reparacion": row['estado_reparacion'],
                "tipo_falla": {
                    "id_tipo_falla": row['id_tipo_falla'],
                    "nombre": row['tipo_falla_nombre'],
                    "prioridad": row['tipo_falla_prioridad'],
                    "descripcion": row['tipo_falla_descripcion'],
                }
            }
            
            # 2. Agrupar la falla bajo su colonia
            if colonia_id not in top_colonias:
                top_colonias[colonia_id] = {
                    "nombre_colonia": row['nombre_colonia'],
                    "total_fallas": 0,
                    "registros_fallas": []
                }
            
            top_colonias[colonia_id]['total_fallas'] += 1
            top_colonias[colonia_id]['registros_fallas'].append(detalle_falla)

        # 3. Ordenar y limitar al Top 10 final
        lista_ordenada = sorted(
            top_colonias.values(), 
            key=lambda item: item['total_fallas'], 
            reverse=True
        )[:10]

        return {"top_10_colonias": lista_ordenada}

    except Exception as e:
        print(f"Error al generar el reporte Top 10: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error al generar el reporte: {e}"
        )
    finally:
        cursor.close()
        conn.close()


@app.get("/")
def home():
    return {"status": "Servidor de Ingesta de Fallas Activo"}