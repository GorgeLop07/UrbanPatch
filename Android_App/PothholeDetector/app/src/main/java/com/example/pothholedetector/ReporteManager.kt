package com.example.pothholedetector

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.util.Log
import androidx.core.app.ActivityCompat
import com.google.android.gms.location.*
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

/**
 * Manager para reportar fallas al servidor con GPS
 */
class ReporteManager(private val context: Context) {
    
    private var fusedLocationClient: FusedLocationProviderClient = 
        LocationServices.getFusedLocationProviderClient(context)
    
    private var lastReportTime = 0L
    private val reportInterval = 5000L // 5 segundos timeout
    
    companion object {
        private const val TAG = "ReporteManager"
    }
    
    /**
     * Reporta una falla detectada al servidor
     */
    fun reportarFalla(
        nombreFalla: String, 
        confianza: Float,
        onSuccess: () -> Unit = {},
        onError: (String) -> Unit = {}
    ) {
        // Verificar timeout de 5 segundos
        val currentTime = System.currentTimeMillis()
        if (currentTime - lastReportTime < reportInterval) {
            Log.d(TAG, "Reporte ignorado - timeout de 5 segundos activo")
            return
        }
        
        // Verificar permisos de ubicación
        if (ActivityCompat.checkSelfPermission(
                context,
                Manifest.permission.ACCESS_FINE_LOCATION
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            Log.e(TAG, "No hay permisos de ubicación")
            onError("Permisos de ubicación no otorgados")
            return
        }
        
        // Obtener ubicación actual
        fusedLocationClient.lastLocation.addOnSuccessListener { location: Location? ->
            if (location != null) {
                // Crear registro
                val registro = RegistroFalla(
                    latitud = location.latitude,
                    longitud = location.longitude,
                    nombreFallaDetectada = nombreFalla,
                    nivelConfianza = confianza.toDouble()
                )
                
                // Enviar al servidor
                enviarAlServidor(registro, onSuccess, onError)
                
                // Actualizar último tiempo de reporte
                lastReportTime = currentTime
                
                Log.d(TAG, "Enviando reporte: $registro")
            } else {
                Log.e(TAG, "No se pudo obtener la ubicación")
                onError("No se pudo obtener la ubicación GPS")
            }
        }.addOnFailureListener { e ->
            Log.e(TAG, "Error obteniendo ubicación", e)
            onError("Error obteniendo ubicación: ${e.message}")
        }
    }
    
    /**
     * Envía el registro al servidor vía Retrofit
     */
    private fun enviarAlServidor(
        registro: RegistroFalla,
        onSuccess: () -> Unit,
        onError: (String) -> Unit
    ) {
        Log.d(TAG, "═══════════════════════════════════")
        Log.d(TAG, "📤 ENVIANDO REPORTE AL SERVIDOR")
        Log.d(TAG, "🌐 URL: http://10.22.228.118:8000/api/registrar_falla/")
        Log.d(TAG, "📍 Lat: ${registro.latitud}, Lon: ${registro.longitud}")
        Log.d(TAG, "🏷️  Tipo: ${registro.nombreFallaDetectada}")
        Log.d(TAG, "📊 Confianza: ${registro.nivelConfianza}")
        Log.d(TAG, "═══════════════════════════════════")
        
        RetrofitClient.apiService.registrarFalla(registro).enqueue(object : Callback<ApiResponse> {
            override fun onResponse(call: Call<ApiResponse>, response: Response<ApiResponse>) {
                Log.d(TAG, "📥 RESPUESTA RECIBIDA")
                Log.d(TAG, "📊 Código: ${response.code()}")
                Log.d(TAG, "📝 Mensaje: ${response.message()}")
                
                if (response.isSuccessful) {
                    Log.d(TAG, "✅ SUCCESS! Body: ${response.body()}")
                    onSuccess()
                } else {
                    val errorBody = response.errorBody()?.string()
                    Log.e(TAG, "❌ ERROR ${response.code()}")
                    Log.e(TAG, "❌ Error Body: $errorBody")
                    onError("HTTP ${response.code()}: $errorBody")
                }
            }
            
            override fun onFailure(call: Call<ApiResponse>, t: Throwable) {
                Log.e(TAG, "❌❌❌ FALLO TOTAL DE RED ❌❌❌")
                Log.e(TAG, "Tipo de error: ${t.javaClass.simpleName}")
                Log.e(TAG, "Mensaje: ${t.message}")
                Log.e(TAG, "Stack:", t)
                onError("Error de red: ${t.message}")
            }
        })
    }
    
    /**
     * Forzar solicitud de ubicación más reciente
     */
    fun solicitarUbicacionActual() {
        if (ActivityCompat.checkSelfPermission(
                context,
                Manifest.permission.ACCESS_FINE_LOCATION
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            return
        }
        
        val locationRequest = LocationRequest.Builder(
            Priority.PRIORITY_HIGH_ACCURACY,
            1000L
        ).build()
        
        fusedLocationClient.requestLocationUpdates(
            locationRequest,
            object : LocationCallback() {
                override fun onLocationResult(locationResult: LocationResult) {
                    super.onLocationResult(locationResult)
                    Log.d(TAG, "Ubicación actualizada: ${locationResult.lastLocation}")
                }
            },
            null
        )
    }
}
