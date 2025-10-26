package com.example.pothholedetector

import android.content.Context
import android.graphics.Bitmap
import android.graphics.RectF
import android.util.Log
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.support.common.ops.NormalizeOp
import org.tensorflow.lite.support.image.ImageProcessor
import org.tensorflow.lite.support.image.TensorImage
import org.tensorflow.lite.support.image.ops.ResizeOp
import java.io.FileInputStream
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel
import kotlin.math.max
import kotlin.math.min

data class Detection(
    val bbox: RectF,      // x1, y1, x2, y2
    val confidence: Float,
    val classId: Int,
    val className: String
)

class PotholeDetector(private val context: Context) {
    
    private var interpreter: Interpreter? = null
    private val inputSize = 640
    private val confidenceThreshold = 0.5f
    private val iouThreshold = 0.45f
    private val labels = listOf("pothole") // Tu modelo solo detecta baches
    
    companion object {
        private const val TAG = "PotholeDetector"
        private const val MODEL_NAME = "best_float16.tflite"
    }
    
    private val imageProcessor = ImageProcessor.Builder()
        .add(ResizeOp(inputSize, inputSize, ResizeOp.ResizeMethod.BILINEAR))
        .add(NormalizeOp(0f, 255f)) // Normaliza a [0, 1]
        .build()
    
    fun initialize(): Boolean {
        return try {
            val modelFile = loadModelFile()
            interpreter = Interpreter(modelFile, Interpreter.Options().apply {
                setNumThreads(4)
            })
            Log.d(TAG, "Model loaded successfully")
            true
        } catch (e: Exception) {
            Log.e(TAG, "Error loading model", e)
            false
        }
    }
    
    private fun loadModelFile(): MappedByteBuffer {
        val assetFileDescriptor = context.assets.openFd(MODEL_NAME)
        val inputStream = FileInputStream(assetFileDescriptor.fileDescriptor)
        val fileChannel = inputStream.channel
        val startOffset = assetFileDescriptor.startOffset
        val declaredLength = assetFileDescriptor.declaredLength
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
    }
    
    fun detect(bitmap: Bitmap): List<Detection> {
        if (interpreter == null) return emptyList()
        
        try {
            // Preprocesar imagen
            var tensorImage = TensorImage.fromBitmap(bitmap)
            tensorImage = imageProcessor.process(tensorImage)
            
            // Preparar output
            // YOLOv11n output: [1, 84, 8400] -> [batch, (4 bbox + 80 classes), anchors]
            // Pero para 1 clase: [1, 5, 8400] -> [batch, (4 bbox + 1 class), anchors]
            val outputShape = interpreter!!.getOutputTensor(0).shape()
            val outputArray = Array(1) { 
                Array(outputShape[1]) { 
                    FloatArray(outputShape[2]) 
                } 
            }
            
            // Inferencia
            interpreter!!.run(tensorImage.buffer, outputArray)
            
            // Post-procesar
            return postProcess(outputArray[0], bitmap.width, bitmap.height)
            
        } catch (e: Exception) {
            Log.e(TAG, "Error during detection", e)
            return emptyList()
        }
    }
    
    private fun postProcess(output: Array<FloatArray>, originalWidth: Int, originalHeight: Int): List<Detection> {
        val detections = mutableListOf<Detection>()
        
        // output shape: [5 o 84, 8400]
        // output[0-3] = bbox (x, y, w, h)
        // output[4+] = class scores
        
        val numDetections = output[0].size
        val numClasses = output.size - 4
        
        for (i in 0 until numDetections) {
            // Encontrar la clase con mayor confianza
            var maxScore = 0f
            var maxClassId = 0
            
            for (classId in 0 until numClasses) {
                val score = output[4 + classId][i]
                if (score > maxScore) {
                    maxScore = score
                    maxClassId = classId
                }
            }
            
            if (maxScore < confidenceThreshold) continue
            
            // Extraer bbox (formato YOLO: x_center, y_center, width, height)
            val cx = output[0][i]
            val cy = output[1][i]
            val w = output[2][i]
            val h = output[3][i]
            
            // Convertir a coordenadas (x1, y1, x2, y2) normalizadas
            val x1 = (cx - w / 2) / inputSize
            val y1 = (cy - h / 2) / inputSize
            val x2 = (cx + w / 2) / inputSize
            val y2 = (cy + h / 2) / inputSize
            
            // Escalar a dimensiones originales
            val bbox = RectF(
                x1 * originalWidth,
                y1 * originalHeight,
                x2 * originalWidth,
                y2 * originalHeight
            )
            
            detections.add(Detection(
                bbox = bbox,
                confidence = maxScore,
                classId = maxClassId,
                className = if (maxClassId < labels.size) labels[maxClassId] else "unknown"
            ))
        }
        
        // Non-Maximum Suppression
        return applyNMS(detections)
    }
    
    private fun applyNMS(detections: List<Detection>): List<Detection> {
        val sortedDetections = detections.sortedByDescending { it.confidence }
        val selectedDetections = mutableListOf<Detection>()
        
        for (detection in sortedDetections) {
            var shouldSelect = true
            
            for (selectedDetection in selectedDetections) {
                val iou = calculateIoU(detection.bbox, selectedDetection.bbox)
                if (iou > iouThreshold) {
                    shouldSelect = false
                    break
                }
            }
            
            if (shouldSelect) {
                selectedDetections.add(detection)
            }
        }
        
        return selectedDetections
    }
    
    private fun calculateIoU(box1: RectF, box2: RectF): Float {
        val intersectionLeft = max(box1.left, box2.left)
        val intersectionTop = max(box1.top, box2.top)
        val intersectionRight = min(box1.right, box2.right)
        val intersectionBottom = min(box1.bottom, box2.bottom)
        
        val intersectionWidth = max(0f, intersectionRight - intersectionLeft)
        val intersectionHeight = max(0f, intersectionBottom - intersectionTop)
        val intersectionArea = intersectionWidth * intersectionHeight
        
        val box1Area = box1.width() * box1.height()
        val box2Area = box2.width() * box2.height()
        val unionArea = box1Area + box2Area - intersectionArea
        
        return if (unionArea > 0) intersectionArea / unionArea else 0f
    }
    
    fun close() {
        interpreter?.close()
        interpreter = null
    }
}
