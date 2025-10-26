package com.example.pothholedetector

import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.POST

/**
 * API Service para comunicarse con el servidor
 */
interface ApiService {
    
    // Con trailing slash como en el curl exitoso
    @POST("api/registrar_falla/")
    fun registrarFalla(@Body registro: RegistroFalla): Call<ApiResponse>
}
