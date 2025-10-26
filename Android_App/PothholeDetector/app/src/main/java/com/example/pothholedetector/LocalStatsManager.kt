package com.example.pothholedetector

import android.content.Context
import android.content.SharedPreferences
import java.text.SimpleDateFormat
import java.util.*

/**
 * Manager simple para estadísticas locales (solo hoy)
 */
class LocalStatsManager(context: Context) {
    
    private val prefs: SharedPreferences = 
        context.getSharedPreferences("BachAppStats", Context.MODE_PRIVATE)
    
    companion object {
        private const val KEY_DETECTIONS_TODAY = "detections_today"
        private const val KEY_LAST_RESET_DATE = "last_reset_date"
        private const val KEY_CONFIDENCE_THRESHOLD = "confidence_threshold"
        private const val KEY_SOUND_ENABLED = "sound_enabled"
        private const val KEY_VIBRATION_ENABLED = "vibration_enabled"
        private const val KEY_DARK_MODE = "dark_mode"
    }
    
    // === ESTADÍSTICAS DE HOY ===
    
    fun getDetectionsToday(): Int {
        checkAndResetIfNewDay()
        return prefs.getInt(KEY_DETECTIONS_TODAY, 0)
    }
    
    fun incrementDetectionsToday() {
        checkAndResetIfNewDay()
        val current = getDetectionsToday()
        prefs.edit().putInt(KEY_DETECTIONS_TODAY, current + 1).apply()
    }
    
    private fun checkAndResetIfNewDay() {
        val today = getCurrentDate()
        val lastResetDate = prefs.getString(KEY_LAST_RESET_DATE, "")
        
        if (lastResetDate != today) {
            // Es un nuevo día, resetear contador
            prefs.edit()
                .putInt(KEY_DETECTIONS_TODAY, 0)
                .putString(KEY_LAST_RESET_DATE, today)
                .apply()
        }
    }
    
    private fun getCurrentDate(): String {
        val sdf = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
        return sdf.format(Date())
    }
    
    // === CONFIGURACIÓN ===
    
    fun getConfidenceThreshold(): Float {
        return prefs.getFloat(KEY_CONFIDENCE_THRESHOLD, 0.5f)
    }
    
    fun setConfidenceThreshold(threshold: Float) {
        prefs.edit().putFloat(KEY_CONFIDENCE_THRESHOLD, threshold).apply()
    }
    
    fun isSoundEnabled(): Boolean {
        return prefs.getBoolean(KEY_SOUND_ENABLED, true)
    }
    
    fun setSoundEnabled(enabled: Boolean) {
        prefs.edit().putBoolean(KEY_SOUND_ENABLED, enabled).apply()
    }
    
    fun isVibrationEnabled(): Boolean {
        return prefs.getBoolean(KEY_VIBRATION_ENABLED, true)
    }
    
    fun setVibrationEnabled(enabled: Boolean) {
        prefs.edit().putBoolean(KEY_VIBRATION_ENABLED, enabled).apply()
    }
    
    fun isDarkModeEnabled(): Boolean {
        return prefs.getBoolean(KEY_DARK_MODE, false)
    }
    
    fun setDarkModeEnabled(enabled: Boolean) {
        prefs.edit().putBoolean(KEY_DARK_MODE, enabled).apply()
    }
}
