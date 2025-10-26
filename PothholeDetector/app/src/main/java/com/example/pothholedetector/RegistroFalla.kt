package com.example.pothholedetector

import com.google.gson.annotations.SerializedName

/**
 * Modelo de datos para enviar al servidor
 */
data class RegistroFalla(
    @SerializedName("latitud")
    val latitud: Double,
    
    @SerializedName("longitud")
    val longitud: Double,
    
    @SerializedName("nombre_falla_detectada")
    val nombreFallaDetectada: String,
    
    @SerializedName("nivel_confianza")
    val nivelConfianza: Double,
    
    @SerializedName("url_imagen")
    val urlImagen: String? = "null"
)

data class ApiResponse(
    val success: Boolean,
    val message: String? = null
)
