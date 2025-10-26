package com.example.pothholedetector

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import java.text.SimpleDateFormat
import java.util.*

class StatsFragment : Fragment() {

    private lateinit var statsManager: LocalStatsManager
    private lateinit var tvStatsToday: TextView
    private lateinit var tvStatsDate: TextView

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_stats, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        statsManager = LocalStatsManager(requireContext())

        tvStatsToday = view.findViewById(R.id.tvStatsToday)
        tvStatsDate = view.findViewById(R.id.tvStatsDate)

        updateStats()
    }

    override fun onResume() {
        super.onResume()
        updateStats()
    }

    private fun updateStats() {
        val todayCount = statsManager.getDetectionsToday()
        tvStatsToday.text = todayCount.toString()

        // Mostrar fecha actual
        val sdf = SimpleDateFormat("EEEE, d 'de' MMMM", Locale("es", "ES"))
        val currentDate = sdf.format(Date())
        tvStatsDate.text = currentDate.replaceFirstChar { it.uppercase() }
    }
}
