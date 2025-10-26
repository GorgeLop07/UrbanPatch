# UrbanPatch - Sistema de Detección de Baches

Sistema inteligente de detección y registro de baches en calles mediante visión por computadora y redes neuronales YOLO, desarrollado para HackMty 2025.

## Descripción del Proyecto

UrbanPatch es una solución integral para la detección automática de fallas en el pavimento (baches) utilizando modelos de machine learning YOLOv11n optimizados para dispositivos móviles y embebidos. El sistema captura imágenes en tiempo real, identifica baches con alta precisión, y registra su ubicación GPS en un servidor central para facilitar el mantenimiento urbano.

### Características Principales

- Detección en tiempo real de baches mediante YOLOv11n con TensorFlow Lite
- Registro automático de ubicación GPS de cada detección
- Aplicación móvil nativa para Android con interfaz moderna
- Sistema de timeout para evitar detecciones duplicadas
- Sincronización con servidor FastAPI mediante API REST
- Estadísticas locales de detecciones por sesión

## Estructura del Proyecto

```
HackMty_2025/
├── Android_App/              # Aplicación móvil Android
│   └── PothholeDetector/     # Proyecto Android Studio
│       ├── app/
│       │   ├── src/
│       │   │   ├── main/
│       │   │   │   ├── assets/       # Modelos TFLite
│       │   │   │   ├── java/         # Código fuente Kotlin
│       │   │   │   └── res/          # Recursos UI
│       │   └── build.gradle.kts
│       └── gradle/
│
├── YOLO_Fine_Tuning/         # Entrenamiento del modelo
│   ├── HackMty_Yolov8n.ipynb
│   ├── modelos_1Clase/       # Modelo para 1 clase (pothole)
│   └── modelos_3Clases/      # Modelo para 3 clases
│
└── Gemini_Request/           # Scripts de integración GenAI
    ├── GenAI.py
    └── pdf.py
```

## Requisitos del Sistema

### Aplicación Android
- Android 7.0 (API 24) o superior
- Android SDK 34
- Permisos: Cámara, Ubicación (GPS), Vibración
- Espacio: ~50 MB

### Desarrollo
- Android Studio Hedgehog o superior
- Gradle 8.13
- Kotlin 1.9+
- Java 17
- Android SDK instalado en `~/Android/Sdk`

### Raspberry Pi (Prototipo a desarrollar)
- Raspberry Pi 4 Model B 
- Ubuntu Server 22.04 o una distribucion de Raspy 
- Python 3.10+
- Cámara USB HD (Steren)
- Bibliotecas: OpenCV, TensorFlow Lite Runtime, Requests

## Instalación y Ejecución

### 1. Aplicación Android

#### Opción A: Instalar APK Precompilado

```bash
# Transferir el APK al dispositivo Android
adb install app-debug.apk

#Este se puede descargar desde la direccion:
#app/build/outputs/apk/debug/app-debug.apk
```

#### Opción B: Compilar desde Código Fuente

```bash
# 1. Clonar el repositorio
git clone https://github.com/GorgeLop07/HackMty_2025.git
cd HackMty_2025/Android_App/PothholeDetector

# 2. Configurar Android SDK (si no existe)
echo "sdk.dir=/home/$USER/Android/Sdk" > local.properties

# 3. Compilar la aplicacion
./gradlew assembleDebug

# 4. El APK se generara en:
# app/build/outputs/apk/debug/app-debug.apk

# 5. Instalar en dispositivo conectado
adb install app/build/outputs/apk/debug/app-debug.apk
```

#### Como usar la aplicacion :00

1. Abrir la aplicación "UrbanPatch"
2. Conceder permisos de cámara y ubicación
3. Presionar el botón "Iniciar Detección"
4. La cámara se activará y comenzará a detectar baches automáticamente
5. Cada detección se registra con GPS y se envía al servidor
6. Ver estadísticas en la pestaña "Estadísticas"
7. Configurar opciones en la pestaña "Ajustes"

### 2. Configuración del Servidor

El sistema requiere un servidor FastAPI con el siguiente endpoint:

```
POST http://10.22.232.9:8001/api/registrar_falla/
```

#### Formato del JSON de Registro

```json
{
  "latitud": 25.6866,
  "longitud": -100.3161,
  "nombre_falla_detectada": "pothole",
  "nivel_confianza": 0.85
}
```

#### Cambiar la Dirección del Servidor

Para actualizar la IP del servidor, editar: (**ESTO ES MUY IMPORTANTE**)

**Android:**
- `Android_App/PothholeDetector/app/src/main/java/com/example/pothholedetector/RetrofitClient.kt`
  ```kotlin
  private const val BASE_URL = "http://TU_IP:8001/"
  ```

**Raspberry Pi:**
- `raspy.py`
  ```python
  SERVER_URL = "http://TU_IP:8001/api/registrar_falla/"
  ```

Luego recompilar la aplicación Android:
```bash
cd Android_App/PothholeDetector
./gradlew assembleDebug
```

## Modelo de Machine Learning

### YOLOv11n - Optimizado para Edge Computing

- **Arquitectura:** YOLOv11 Nano (versión ligera)
- **Framework:** Ultralytics
- **Formato:** TensorFlow Lite (.tflite)
- **Tamaño de entrada:** 640x640 píxeles
- **Clases detectadas:** pothole (bache)
- **Precisión promedio:** ~85% mAP

### Modelos Disponibles

| Modelo | Plataforma | Cuantización | Tamaño | Uso |
|--------|-----------|-------------|---------|-----|
| best_float32.tflite | Android | Float32 | ~6 MB | Alta precisión |
| best_float16.tflite | Android | Float16 | ~3 MB | Balanceado |
| best_int8.tflite | Raspberry Pi | INT8 | ~2 MB | Optimizado ARM |

### Reentrenar el Modelo

```bash
# Abrir el notebook de entrenamiento
jupyter notebook YOLO_Fine_Tuning/HackMty_Yolov8n.ipynb

# Seguir las instrucciones del notebook para:
# 1. Cargar dataset personalizado
# 2. Configurar hiperparámetros
# 3. Entrenar el modelo
# 4. Exportar a TensorFlow Lite
```

## Arquitectura del Sistema

```
┌─────────────────┐
│  Android App    │───┐
│  (UrbanPatch)   │   │
└─────────────────┘   │
                      │
┌─────────────────┐   │    ┌──────────────────┐
│ Raspberry Pi 5  │───┼───→│  FastAPI Server  │
│  + USB Camera   │   │    │  (10.22.232.9)   │
└─────────────────┘   │    └──────────────────┘
                      │             │
┌─────────────────┐   │             ↓
│  Otros Clientes │───┘    ┌──────────────────┐
│   (Futuros)     │        │    Database      │
└─────────────────┘        │   (PostgreSQL)   │
                           └──────────────────┘
```

### Flujo de Datos

1. **Captura:** La cámara captura frames en tiempo real
2. **Inferencia:** El modelo YOLO procesa cada frame (o cada N frames)
3. **Detección:** Si se detecta un bache con confianza > 50%:
   - Se obtiene la ubicación GPS actual
   - Se crea un registro JSON
   - Se envía al servidor vía HTTP POST
4. **Timeout:** Sistema de 3-5 segundos entre reportes para evitar duplicados
5. **Almacenamiento:** El servidor persiste los datos en base de datos
6. **Visualización:** Dashboard web muestra mapa de baches reportados

## Características Técnicas

### Aplicación Android

- **Lenguaje:** Kotlin
- **Arquitectura:** MVVM con ViewBinding
- **Cámara:** CameraX API
- **Inferencia:** TensorFlow Lite Interpreter
- **Networking:** Retrofit 2 + OkHttp
- **GPS:** Google Play Services Location API
- **UI:** Material Design 3

## Solución de Problemas

### Error: SDK location not found

```bash
# Crear archivo local.properties
echo "sdk.dir=$HOME/Android/Sdk" > local.properties
```

### Error: No se puede conectar al servidor

1. Verificar que el servidor esté ejecutándose
2. Comprobar la IP y puerto en `RetrofitClient.kt`
3. Verificar conectividad de red (misma red local)
4. Revisar logs de la aplicación con `adb logcat`

### GPS no funciona en Android

1. Activar GPS en configuración del dispositivo
2. Otorgar permisos de ubicación a la app
3. Usar la app en exteriores para mejor señal
4. Verificar permisos en `AndroidManifest.xml`

## Contribuciones

Este proyecto fue desarrollado durante el HackMty 2025

### Desarrolladores

- @GorgeLop07 - Jorge Luis Lopez Garcia
- @Thermoflask7 - Mateo Zaragoza Burruel
- @GioMax102 - Mario Giovanni Gonzalez Lopez
- @Juanrdz42 - Juan Antonio Rodriguez Reyna
- Oficialmente: EQUIPO 2 **(YEA)**

## Contacto y Soporte

Para preguntas, reportes de bugs o sugerencias:

- **Repository:** https://github.com/GorgeLop07/HackMty_2025
- **Issues:** https://github.com/GorgeLop07/HackMty_2025/issues

## TODOSSS

- Clasificación de múltiples tipos de fallas (grietas, hundimientos)
- Dashboard web en tiempo real con mapas
- Integración con sistemas municipales
- Aplicación iOS
- Implementacion de codigo en Rasperry 4 

