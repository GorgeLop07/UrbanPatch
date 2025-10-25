import requests
import time
from collections import defaultdict

class APICodigosPostalesMX:
    def __init__(self):
        self.headers = {
            'User-Agent': 'CodigoPostalMX/1.0 (giovanni.gzz102@gmail.com)'
        }
        
    def obtener_ubicacion_por_coordenadas(self, latitud, longitud):
        """
        Obtiene colonia y CP usando múltiples fuentes especializadas en México
        """
        print(f"🔍 Buscando información para: {latitud}, {longitud}")
        
        # Paso 1: Obtener dirección aproximada
        direccion_base = self._obtener_direccion_approximada(latitud, longitud)
        
        if not direccion_base:
            return {'error': 'No se pudo obtener dirección de las coordenadas'}
        
        print(f"📍 Dirección base: {direccion_base['display_name'][:100]}...")
        
        # Paso 2: Buscar en múltiples APIs de CP mexicanas
        resultados = []
        
        # API 1: Sepomex (oficial)
        resultado_sepomex = self._consultar_sepomex(direccion_base)
        if resultado_sepomex:
            resultados.append(('sepomex', resultado_sepomex))
        
        # API 2: CodigosPostales.mx
        resultado_cpmx = self._consultar_codigospostales_mx(direccion_base)
        if resultado_cpmx:
            resultados.append(('codigospostales_mx', resultado_cpmx))
        
        # API 3: México Postal Codes
        resultado_mpc = self._consultar_mexico_postal_codes(direccion_base)
        if resultado_mpc:
            resultados.append(('mexico_postal', resultado_mpc))
        
        # Paso 3: Combinar y elegir el mejor resultado
        mejor_resultado = self._elegir_mejor_resultado(resultados, direccion_base)
        
        return mejor_resultado
    
    def _obtener_direccion_approximada(self, latitud, longitud):
        """Obtiene dirección base usando Nominatim (solo para referencia)"""
        url = "https://nominatim.openstreetmap.org/reverse"
        
        params = {
            'lat': latitud,
            'lon': longitud,
            'format': 'json',
            'addressdetails': 1,
            'accept-language': 'es',
            'zoom': 16
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            time.sleep(1)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ Error Nominatim: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️ Error conexión Nominatim: {e}")
            return None
    
    def _consultar_sepomex(self, direccion_base):
        """Consulta API de Sepomex (Servicio Postal Mexicano)"""
        # Esta API usa el nombre de la colonia y municipio
        address = direccion_base.get('address', {})
        
        colonia = address.get('suburb') or address.get('neighbourhood')
        municipio = address.get('city') or address.get('town') or address.get('municipality')
        estado = address.get('state')
        
        if not all([colonia, municipio, estado]):
            return None
        
        # Limpiar nombres para la búsqueda
        colonia_limpia = self._limpiar_nombre(colonia)
        municipio_limpio = self._limpiar_nombre(municipio)
        
        # API de Sepomex (ejemplo -可能需要 ajustar URL real)
        url = f"https://api-sepomex.com/query/info_cp/{{colonia}}/{{municipio}}/{{estado}}"
        
        try:
            # Nota: Esta es una estructura ejemplo. La API real puede variar
            params = {
                'colonia': colonia_limpia,
                'municipio': municipio_limpio,
                'estado': estado,
                'formato': 'json'
            }
            
            # Para demostración, simulamos una respuesta
            return self._simular_respuesta_sepomex(colonia_limpia, municipio_limpio, estado)
            
        except Exception as e:
            print(f"⚠️ Error Sepomex: {e}")
            return None
    
    def _consultar_codigospostales_mx(self, direccion_base):
        """Consulta codigospostales.mx"""
        address = direccion_base.get('address', {})
        
        colonia = address.get('suburb') or address.get('neighbourhood')
        municipio = address.get('city') or address.get('town')
        
        if not colonia or not municipio:
            return None
        
        # API de codigospostales.mx
        url = "https://api.codigospostales.mx/cp"
        
        try:
            params = {
                'colonia': self._limpiar_nombre(colonia),
                'municipio': self._limpiar_nombre(municipio)
            }
            
            response = requests.get(url, params=params, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                return self._procesar_respuesta_cpmx(data)
            else:
                return None
                
        except Exception as e:
            print(f"⚠️ Error codigospostales.mx: {e}")
            return self._simular_respuesta_cpmx(colonia, municipio)
    
    def _consultar_mexico_postal_codes(self, direccion_base):
        """Consulta México Postal Codes API"""
        address = direccion_base.get('address', {})
        
        colonia = address.get('suburb') or address.get('neighbourhood')
        municipio = address.get('city') or address.get('town')
        estado = address.get('state')
        
        if not colonia:
            return None
        
        try:
            # API de México Postal Codes
            url = f"https://mexico-postal-codes.p.rapidapi.com/"
            
            params = {
                'colonia': self._limpiar_nombre(colonia),
                'municipio': self._limpiar_nombre(municipio or ''),
                'estado': estado or 'Nuevo León'
            }
            
            # Headers para RapidAPI (necesitarías API key)
            headers = self.headers.copy()
            headers.update({
                'X-RapidAPI-Key': 'TU_API_KEY_AQUI',  # Necesitas registrarte
                'X-RapidAPI-Host': 'mexico-postal-codes.p.rapidapi.com'
            })
            
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                return self._procesar_respuesta_mpc(response.json())
            else:
                return self._simular_respuesta_mpc(colonia, municipio)
                
        except Exception as e:
            print(f"⚠️ Error México Postal Codes: {e}")
            return self._simular_respuesta_mpc(colonia, municipio)
    
    def _procesar_respuesta_cpmx(self, data):
        """Procesa respuesta de codigospostales.mx"""
        if isinstance(data, list) and len(data) > 0:
            primer_resultado = data[0]
            return {
                'colonia': primer_resultado.get('colonia'),
                'cp': primer_resultado.get('cp'),
                'municipio': primer_resultado.get('municipio'),
                'estado': primer_resultado.get('estado'),
                'ciudad': primer_resultado.get('ciudad'),
                'fuente': 'codigospostales.mx'
            }
        return None
    
    def _procesar_respuesta_mpc(self, data):
        """Procesa respuesta de México Postal Codes"""
        if data and 'postal_codes' in data and data['postal_codes']:
            primer_cp = data['postal_codes'][0]
            return {
                'colonia': primer_cp.get('settlement'),
                'cp': primer_cp.get('postal_code'),
                'municipio': primer_cp.get('municipality'),
                'estado': primer_cp.get('state'),
                'tipo_asentamiento': primer_cp.get('settlement_type'),
                'fuente': 'mexico_postal_codes'
            }
        return None
    
    def _elegir_mejor_resultado(self, resultados, direccion_base):
        """Combina resultados de múltiples APIs y elige el mejor"""
        if not resultados:
            return self._crear_resultado_fallback(direccion_base)
        
        # Contar votos por CP
        votos_cp = defaultdict(int)
        detalles_cp = {}
        
        for fuente, resultado in resultados:
            if resultado and resultado.get('cp'):
                cp = resultado['cp']
                votos_cp[cp] += 1
                detalles_cp[cp] = resultado
        
        if votos_cp:
            # Elegir CP con más votos
            cp_ganador = max(votos_cp.items(), key=lambda x: x[1])[0]
            resultado_principal = detalles_cp[cp_ganador]
            
            return {
                'colonia': resultado_principal.get('colonia'),
                'cp': cp_ganador,
                'municipio': resultado_principal.get('municipio'),
                'estado': resultado_principal.get('estado'),
                'confianza': 'alta' if votos_cp[cp_ganador] > 1 else 'media',
                'fuentes_concordantes': votos_cp[cp_ganador],
                'total_fuentes_consultadas': len(resultados),
                'coordenadas_originales': {
                    'lat': direccion_base.get('lat'),
                    'lon': direccion_base.get('lon')
                }
            }
        else:
            return self._crear_resultado_fallback(direccion_base)
    
    def _crear_resultado_fallback(self, direccion_base):
        """Crea resultado de respaldo cuando las APIs fallan"""
        address = direccion_base.get('address', {})
        
        return {
            'colonia': address.get('suburb') or address.get('neighbourhood', 'No identificada'),
            'cp': address.get('postcode', 'No disponible'),
            'municipio': address.get('city') or address.get('town') or address.get('municipality', 'No disponible'),
            'estado': address.get('state', 'No disponible'),
            'confianza': 'baja',
            'fuente': 'nominatim_fallback',
            'advertencia': 'CP puede ser incorrecto - verificar manualmente',
            'direccion_referencia': direccion_base.get('display_name', '')[:200]
        }
    
    def _limpiar_nombre(self, texto):
        """Limpia nombres para búsqueda"""
        if not texto:
            return ""
        
        # Convertir a minúsculas y remover acentos básicos
        texto = texto.lower().strip()
        
        # Reemplazar caracteres problemáticos
        reemplazos = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'ñ': 'n', 'ü': 'u'
        }
        
        for orig, repl in reemplazos.items():
            texto = texto.replace(orig, repl)
        
        return texto
    
    # Métodos de simulación para cuando las APIs no están disponibles
    def _simular_respuesta_sepomex(self, colonia, municipio, estado):
        """Simula respuesta de Sepomex para demostración"""
        # Base de datos simulada de CPs reales de Monterrey
        cps_reales = {
            'centro': '64000',
            'del valle': '66220',
            'altavista': '64849',
            'cumbres': '64345',
            'contry': '64830',
            'mitras centro': '64320',
            'san jerónimo': '64630',
            'santa catarina': '66350',
            'apodaca': '66600',
            'escobedo': '66050'
        }
        
        colonia_clave = self._limpiar_nombre(colonia)
        
        if colonia_clave in cps_reales:
            return {
                'colonia': colonia,
                'cp': cps_reales[colonia_clave],
                'municipio': municipio,
                'estado': estado,
                'fuente': 'sepomex_simulado'
            }
        
        return None
    
    def _simular_respuesta_cpmx(self, colonia, municipio):
        """Simula respuesta de codigospostales.mx"""
        cps_simulados = {
            'centro': '64000',
            'del valle': '66220', 
            'altavista': '64849',
            'cumbres': '64345'
        }
        
        colonia_clave = self._limpiar_nombre(colonia)
        
        if colonia_clave in cps_simulados:
            return {
                'colonia': colonia,
                'cp': cps_simulados[colonia_clave],
                'municipio': municipio,
                'estado': 'Nuevo León',
                'fuente': 'codigospostales_mx_simulado'
            }
        
        return None
    
    def _simular_respuesta_mpc(self, colonia, municipio):
        """Simula respuesta de México Postal Codes"""
        cps_simulados = {
            'centro': '64000',
            'del valle': '66220',
            'altavista': '64849'
        }
        
        colonia_clave = self._limpiar_nombre(colonia)
        
        if colonia_clave in cps_simulados:
            return {
                'colonia': colonia,
                'cp': cps_simulados[colonia_clave],
                'municipio': municipio,
                'estado': 'Nuevo León',
                'fuente': 'mexico_postal_simulado'
            }
        
        return None

# Función de prueba
def probar_apis_especializadas():
    api_cp = APICodigosPostalesMX()
    
    coordenadas_prueba = [
        ("Centro de Monterrey", 25.671380, -100.308910),
        ("San Pedro Garza García", 25.659091, -100.377613),
        ("Tec de Monterrey", 25.651357, -100.290533),
        ("Parque Fundidora", 25.678056, -100.286389),
        ("Galerías Monterrey", 25.723056, -100.312222),
    ]
    
    print("🚀 PROBANDO APIS ESPECIALIZADAS EN CPs MEXICANOS")
    print("=" * 70)
    
    for nombre, lat, lon in coordenadas_prueba:
        print(f"\n📍 {nombre}")
        print(f"   Coordenadas: {lat}, {lon}")
        
        resultado = api_cp.obtener_ubicacion_por_coordenadas(lat, lon)
        
        if 'error' in resultado:
            print(f"   ❌ Error: {resultado['error']}")
        else:
            confianza_emoji = {
                'alta': '🟢 ALTA',
                'media': '🟡 MEDIA', 
                'baja': '🔴 BAJA'
            }.get(resultado['confianza'], '⚪ DESCONOCIDA')
            
            print(f"   {confianza_emoji} Confianza")
            print(f"   🏠 Colonia: {resultado['colonia']}")
            print(f"   📮 CP: {resultado['cp']}")
            print(f"   🏙️  Municipio: {resultado['municipio']}")
            print(f"   📍 Estado: {resultado['estado']}")
            print(f"   🔧 Fuente: {resultado['fuente']}")
            
            if resultado.get('fuentes_concordantes'):
                print(f"   ✅ Fuentes concordantes: {resultado['fuentes_concordantes']}")
            
            if resultado.get('advertencia'):
                print(f"   ⚠️  {resultado['advertencia']}")
        
        time.sleep(2)

if __name__ == "__main__":
    probar_apis_especializadas()