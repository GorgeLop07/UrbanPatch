import image_17bd952a9740eb2ca0a183a1f3fb157d4277700a from 'figma:asset/17bd952a9740eb2ca0a183a1f3fb157d4277700a.png';
import { useState } from "react";
import { Camera, Search, Square, AlertCircle, Play } from "lucide-react";
import { Button } from "./components/ui/button";
import { Card } from "./components/ui/card";
import { ImageWithFallback } from "./components/figma/ImageWithFallback";
import { motion } from "motion/react";
import exampleImage from "figma:asset/4d3c0ae9161f663421df327798f192fd6f6515b2.png";
import banorteLogo from "figma:asset/b68093ddc72bbd40c5cd6f9e7a4dbde9b5bd85fa.png";

export default function App() {
  const [isScanning, setIsScanning] = useState(true);
  const [detectedCount, setDetectedCount] = useState(0);

  const toggleScanning = () => {
    setIsScanning(!isScanning);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-950 via-red-900 to-red-950 flex flex-col">
      {/* Status Bar Spacer */}
      <div className="h-12 bg-red-950/50 backdrop-blur-sm" />
      
      {/* Header */}
      <header className="bg-red-950/80 backdrop-blur-md border-b border-red-700/50 px-6 py-4 shadow-xl">
        <div className="flex items-center justify-end">
          <img src={image_17bd952a9740eb2ca0a183a1f3fb157d4277700a} alt="Banorte" className="h-8" />
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col p-6 gap-6">
        {/* Camera View Card */}
        <Card className="relative overflow-hidden border-2 border-red-700/50 shadow-2xl bg-red-900/50 backdrop-blur-sm">
          <div className="aspect-[3/4] relative">
            <img 
              src={exampleImage} 
              alt="Camera view"
              className="w-full h-full object-cover"
            />
            
            {/* Overlay gradient */}
            <div className="absolute inset-0 bg-gradient-to-t from-red-950/80 via-transparent to-red-950/40" />
            
            {/* Scanning Animation */}
            {isScanning && (
              <motion.div
                className="absolute inset-0 border-4 border-red-500/50 rounded-lg shadow-[0_0_20px_rgba(239,68,68,0.3)]"
                initial={{ opacity: 0 }}
                animate={{ 
                  opacity: [0.3, 0.8, 0.3],
                  scale: [0.98, 1, 0.98]
                }}
                transition={{ 
                  duration: 2, 
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
            )}

            {/* Detection Corners */}
            {isScanning && (
              <>
                <div className="absolute top-4 left-4 w-12 h-12 border-t-4 border-l-4 border-red-400 rounded-tl-lg" />
                <div className="absolute top-4 right-4 w-12 h-12 border-t-4 border-r-4 border-red-400 rounded-tr-lg" />
                <div className="absolute bottom-4 left-4 w-12 h-12 border-b-4 border-l-4 border-red-400 rounded-bl-lg" />
                <div className="absolute bottom-4 right-4 w-12 h-12 border-b-4 border-r-4 border-red-400 rounded-br-lg" />
              </>
            )}

            {/* Stats Overlay */}
            <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-red-950/90 backdrop-blur-md px-4 py-2 rounded-full border border-red-500/30">
              <div className="flex items-center gap-2 text-red-300">
                <Camera className="w-4 h-4" />
                <span className="text-sm">Cámara activa</span>
              </div>
            </div>
          </div>
        </Card>

        {/* Status Section */}
        <div className="space-y-4">
          {/* Scanning Indicator */}
          <motion.div
            className="bg-gradient-to-r from-red-500/20 to-orange-500/20 border border-red-500/30 rounded-2xl p-4 backdrop-blur-sm"
            animate={isScanning ? { 
              boxShadow: [
                "0 0 20px rgba(239,68,68,0.2)",
                "0 0 30px rgba(239,68,68,0.4)",
                "0 0 20px rgba(239,68,68,0.2)"
              ]
            } : {}}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <div className="flex items-center gap-3">
              <div className="relative">
                <Search className="w-6 h-6 text-red-400" />
                {isScanning && (
                  <motion.div
                    className="absolute -inset-1 border-2 border-red-400 rounded-full"
                    animate={{ scale: [1, 1.5, 1], opacity: [1, 0, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                )}
              </div>
              <div className="flex-1">
                <p className="text-red-300">
                  {isScanning ? "Buscando baches..." : "Detección pausada"}
                </p>
                <p className="text-red-200/60 text-sm">
                  {detectedCount} baches detectados hoy
                </p>
              </div>
            </div>
          </motion.div>

          {/* Control Button */}
          <Button
            onClick={toggleScanning}
            size="lg"
            className={`w-full h-16 text-lg transition-all duration-300 ${
              isScanning 
                ? "bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 shadow-[0_0_30px_rgba(220,38,38,0.3)]" 
                : "bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 shadow-[0_0_30px_rgba(239,68,68,0.3)]"
            }`}
          >
            {isScanning ? <Square className="w-5 h-5 mr-2" /> : <Play className="w-5 h-5 mr-2" />}
            {isScanning ? "DETENER" : "INICIAR DETECCIÓN"}
          </Button>

          {/* Info Card */}
          <Card className="bg-red-900/50 border-red-700/50 p-4 backdrop-blur-sm">
            <div className="flex gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-red-100">
                <p className="text-red-300 mb-1">Consejo</p>
                <p>Mantén la cámara estable y enfocada en la carretera para una mejor detección.</p>
              </div>
            </div>
          </Card>
        </div>
      </main>

      {/* Bottom Navigation Spacer */}
      <div className="h-20 bg-gradient-to-t from-red-950/80 to-transparent" />
    </div>
  );
}
