import mysql.connector
import snowflake.connector
import pandas as pd
from io import StringIO
from datetime import datetime

# --- CONFIGURACIÓN ---
# A. MySQL (Tu localhost)
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "GioMax102._.", 
    "database": "db_smart_city"
}
# B. Snowflake (Reemplaza con tus credenciales)
SNOWFLAKE_CONFIG = {
    "user": "TU_USUARIO_SNOWFLAKE", 
    "password": "GioMax102._._.", 
    "account": "JO89951.us-east-1", # Ejemplo: 'xyz12345.us-east-1'
    "warehouse": "ANALISIS_SMART_CITY",
    "database": "DB_IA_SMART_CITY",
    "schema": "TU_SCHEMA_NAME" 
}
TABLE_DESTINO = "REGISTROS_FALLAS_BRUTOS"

# --- LÓGICA DE EXTRACCIÓN Y CARGA (EL) ---

def run_migration():
    """Ejecuta la extracción de MySQL y la carga en Snowflake."""
    
    # 1. Conexión a MySQL
    try:
        mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
        print("Conexión a MySQL exitosa.")
    except Exception as e:
        print(f"Error conectando a MySQL: {e}")
        return

    # 2. Extracción (E) - Extraer todos los registros
    # NOTA: En un entorno de producción, usarías una columna de marca de tiempo (timestamp)
    # para extraer solo los datos *nuevos* desde la última ejecución.
    query = "SELECT * FROM REGISTROS_FALLAS;"
    df = pd.read_sql(query, mysql_conn)
    mysql_conn.close()
    
    if df.empty:
        print("No hay nuevos registros para migrar.")
        return

    print(f"Extraídos {len(df)} registros de MySQL.")

    # 3. Preparación de Carga (Snowflake requiere datos en formato de archivo)
    csv_buffer = StringIO()
    # Usamos '|' como separador para evitar conflictos con datos internos como las URLs
    df.to_csv(csv_buffer, index=False, sep='|', header=True)
    
    # 4. Conexión a Snowflake
    try:
        sf_conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
        sf_cursor = sf_conn.cursor()
        print("Conexión a Snowflake exitosa.")
    except Exception as e:
        print(f"Error conectando a Snowflake: {e}")
        return

    # 5. Carga (L) - Usando el comando COPY INTO optimizado
    
    # 5.1 Crear una etapa temporal (stage) para el archivo CSV
    sf_cursor.execute("CREATE OR REPLACE TEMPORARY STAGE temp_stage;")
    
    # 5.2 Poner el archivo CSV en la etapa
    # Esto usa la función put de la librería de Snowflake para subir el buffer de StringIO
    try:
        # Usamos df.shape[0] para el nombre temporal
        sf_cursor.execute(f"PUT file://{datetime.now().strftime('%Y%m%d%H%M%S')}_{df.shape[0]}.csv @temp_stage AUTO_COMPRESS=TRUE",
                         file_stream=csv_buffer.getvalue().encode('utf-8'))

    except Exception as e:
        print(f"Error al subir archivo a la etapa temporal: {e}")
        return
        
    # 5.3 Copiar datos de la etapa a la tabla (Carga)
    copy_query = f"""
    COPY INTO {TABLE_DESTINO} (
        id_registro, id_colonia, latitud, longitud, fecha_hora_deteccion, 
        nivel_confianza, estado_reparacion, url_imagen, id_tipo_falla, id_usuario
    )
    FROM @temp_stage/{datetime.now().strftime('%Y%m%d%H%M%S')}_{df.shape[0]}.csv
    FILE_FORMAT = (
        TYPE = CSV,
        SKIP_HEADER = 1,
        FIELD_DELIMITER = '|',
        ENCODING = 'UTF8',
        TRIM_SPACE = TRUE
    );
    """
    sf_cursor.execute(copy_query)
    print(f"Cargados {df.shape[0]} registros en Snowflake.")
    
    # 6. Transformación (T) - Modelado Analítico Básico (Opcional, pero recomendado)
    # Aquí puedes crear tu tabla final de análisis uniendo las tablas de referencia
    
    print("\n¡Migración ELT completada!")
    sf_conn.close()

if __name__ == "__main__":
    run_migration()