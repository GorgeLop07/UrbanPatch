package com.example.pothholedetector

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.os.Bundle
import android.util.Log
import android.view.View
import android.view.animation.AnimationUtils
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import com.example.pothholedetector.databinding.ActivityMainBinding
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var cameraExecutor: ExecutorService
    private lateinit var potholeDetector: PotholeDetector
    private var imageAnalysis: ImageAnalysis? = null
    private var isDetecting = false
    private var lastDetectionTime = 0L
    private val detectionInterval = 500L

    companion object {
        private const val TAG = "MainActivity"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        cameraExecutor = Executors.newSingleThreadExecutor()
        potholeDetector = PotholeDetector(this)

        // Estado inicial
        binding.tvStatus.text = "Detección pausada"
        binding.btnStart.text = "INICIAR DETECCIÓN"

        // Inicializar detector
        if (potholeDetector.initialize()) {
            Toast.makeText(this, "Modelo cargado exitosamente", Toast.LENGTH_SHORT).show()
        } else {
            binding.tvStatus.text = "Error cargando modelo"
            Toast.makeText(this, "Error cargando modelo", Toast.LENGTH_LONG).show()
        }

        binding.btnStart.setOnClickListener {
            toggleDetection()
        }

        if (hasCameraPermission()) {
            startCamera()
        } else {
            requestCameraPermission()
        }
    }

    private fun toggleDetection() {
        isDetecting = !isDetecting
        runOnUiThread {
            if (isDetecting) {
                binding.btnStart.text = "DETENER"
                binding.tvStatus.text = "Buscando baches..."
                
                // Iniciar animación solo del indicador
                val rotateAnim = AnimationUtils.loadAnimation(this, R.anim.rotate_animation)
                binding.statusIndicator.startAnimation(rotateAnim)
            } else {
                binding.btnStart.text = "INICIAR DETECCIÓN"
                binding.tvStatus.text = "Detección pausada"
                
                // Detener animación
                binding.statusIndicator.clearAnimation()
            }
        }
    }

    private fun hasCameraPermission() =
        ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) ==
                PackageManager.PERMISSION_GRANTED

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            startCamera()
        } else {
            Toast.makeText(this, "Permiso de cámara requerido", Toast.LENGTH_LONG).show()
            finish()
        }
    }

    private fun requestCameraPermission() {
        requestPermissionLauncher.launch(Manifest.permission.CAMERA)
    }

    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)

        cameraProviderFuture.addListener({
            val cameraProvider = cameraProviderFuture.get()

            val preview = Preview.Builder()
                .build()
                .also {
                    it.setSurfaceProvider(binding.viewFinder.surfaceProvider)
                }

            imageAnalysis = ImageAnalysis.Builder()
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build()
                .also {
                    it.setAnalyzer(cameraExecutor) { imageProxy ->
                        processImage(imageProxy)
                    }
                }

            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA

            try {
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(
                    this, cameraSelector, preview, imageAnalysis
                )
            } catch (e: Exception) {
                Log.e(TAG, "Error starting camera", e)
            }

        }, ContextCompat.getMainExecutor(this))
    }

    private fun processImage(imageProxy: ImageProxy) {
        if (!isDetecting) {
            imageProxy.close()
            return
        }

        // Throttle detections
        val currentTime = System.currentTimeMillis()
        if (currentTime - lastDetectionTime < detectionInterval) {
            imageProxy.close()
            return
        }
        lastDetectionTime = currentTime

        try {
            // Convertir ImageProxy a Bitmap
            val bitmap = imageProxy.toBitmap()

            // Detectar
            val detections = potholeDetector.detect(bitmap)

            // Actualizar UI
            runOnUiThread {
                if (detections.isNotEmpty()) {
                    val detection = detections.first()
                    val confidence = (detection.confidence * 100).toInt()
                    
                    binding.tvStatus.text = "¡BACHE DETECTADO! ($confidence%)"
                    
                    Log.d(TAG, "Pothole detected: confidence=${detection.confidence}, bbox=${detection.bbox}")
                } else {
                    binding.tvStatus.text = "Buscando baches..."
                }
            }

        } catch (e: Exception) {
            Log.e(TAG, "Error processing image", e)
        } finally {
            imageProxy.close()
        }
    }

    private fun ImageProxy.toBitmap(): Bitmap {
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        bitmap.copyPixelsFromBuffer(planes[0].buffer)
        return bitmap
    }

    override fun onDestroy() {
        super.onDestroy()
        cameraExecutor.shutdown()
        potholeDetector.close()
    }
}