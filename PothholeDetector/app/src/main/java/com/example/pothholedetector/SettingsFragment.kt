package com.example.pothholedetector

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.SeekBar
import android.widget.TextView
import androidx.appcompat.widget.SwitchCompat
import androidx.fragment.app.Fragment

class SettingsFragment : Fragment() {

    private lateinit var statsManager: LocalStatsManager
    private lateinit var seekBarThreshold: SeekBar
    private lateinit var tvThresholdValue: TextView
    private lateinit var switchSound: SwitchCompat
    private lateinit var switchVibration: SwitchCompat
    private lateinit var switchDarkMode: SwitchCompat

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_settings, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        statsManager = LocalStatsManager(requireContext())

        seekBarThreshold = view.findViewById(R.id.seekBarThreshold)
        tvThresholdValue = view.findViewById(R.id.tvThresholdValue)
        switchSound = view.findViewById(R.id.switchSound)
        switchVibration = view.findViewById(R.id.switchVibration)
        switchDarkMode = view.findViewById(R.id.switchDarkMode)

        // Aplicar tema según modo nocturno
        applyTheme(view)

        // Cargar configuraciones guardadas
        loadSettings()

        // Listener para el SeekBar
        seekBarThreshold.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                val threshold = 30 + progress
                tvThresholdValue.text = "$threshold%"
                statsManager.setConfidenceThreshold(threshold / 100f)
            }

            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })

        // Listener para Sonido
        switchSound.setOnCheckedChangeListener { _, isChecked ->
            statsManager.setSoundEnabled(isChecked)
        }

        // Listener para Vibración
        switchVibration.setOnCheckedChangeListener { _, isChecked ->
            statsManager.setVibrationEnabled(isChecked)
        }

        // Listener para Modo Nocturno
        switchDarkMode.setOnCheckedChangeListener { _, isChecked ->
            statsManager.setDarkModeEnabled(isChecked)
            // Aplicar tema inmediatamente
            applyTheme(view)
            // Notificar al fragmento de inicio para que actualice también
            (activity as? MainActivity)?.refreshHomeFragment()
        }
    }

    private fun applyTheme(view: View) {
        val isDarkMode = statsManager.isDarkModeEnabled()
        val background = if (isDarkMode) {
            R.drawable.bg_gradient_light
        } else {
            R.drawable.bg_gradient_red
        }
        view.setBackgroundResource(background)
    }

    private fun loadSettings() {
        // Cargar umbral
        val threshold = statsManager.getConfidenceThreshold()
        val percentage = (threshold * 100).toInt()
        seekBarThreshold.progress = percentage
        tvThresholdValue.text = "$percentage%"

        // Cargar switches
        switchSound.isChecked = statsManager.isSoundEnabled()
        switchVibration.isChecked = statsManager.isVibrationEnabled()
        switchDarkMode.isChecked = statsManager.isDarkModeEnabled()
    }
}
