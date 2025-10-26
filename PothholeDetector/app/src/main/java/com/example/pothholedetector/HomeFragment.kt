package com.example.pothholedetector

import android.app.Dialog
import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.Window
import android.widget.Button
import android.widget.TextView
import androidx.fragment.app.Fragment

class HomeFragment : Fragment() {

    private lateinit var statsManager: LocalStatsManager
    private lateinit var tvTodayCount: TextView
    private lateinit var btnStartJourney: Button

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_home, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        statsManager = LocalStatsManager(requireContext())

        tvTodayCount = view.findViewById(R.id.tvTodayCount)
        btnStartJourney = view.findViewById(R.id.btnStartJourney)

        // Aplicar tema según modo nocturno
        applyTheme(view)

        // Actualizar contador
        updateStats()

        // Botón para comenzar trayecto
        btnStartJourney.setOnClickListener {
            showBatteryWarning()
        }
    }

    override fun onResume() {
        super.onResume()
        updateStats()
        // Re-aplicar tema al volver
        view?.let { applyTheme(it) }
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

    private fun updateStats() {
        val todayCount = statsManager.getDetectionsToday()
        tvTodayCount.text = todayCount.toString()
    }

    private fun showBatteryWarning() {
        val dialog = Dialog(requireContext())
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE)
        dialog.setContentView(R.layout.dialog_battery_warning)
        dialog.window?.setBackgroundDrawableResource(android.R.color.transparent)

        val btnCancel: Button = dialog.findViewById(R.id.btnDialogCancel)
        val btnContinue: Button = dialog.findViewById(R.id.btnDialogContinue)

        btnCancel.setOnClickListener {
            dialog.dismiss()
        }

        btnContinue.setOnClickListener {
            dialog.dismiss()
            // Abrir CameraActivity con animación slide
            val intent = Intent(requireContext(), CameraActivity::class.java)
            startActivity(intent)
            requireActivity().overridePendingTransition(R.anim.slide_in_right, R.anim.slide_out_left)
        }

        dialog.show()
    }
}
