import requests
import time

class LocalizadorColonias:
    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/reverse"
        self.search_url = "https://nominatim.openstreetmap.org/search"
    
    def obtener_colonia_por_coordenadas(self, latitud, longitud):
        """Obtiene la colonia usando coordenadas GPS"""
        params = {
            'lat': latitud,
            'lon': longitud,
            'format': 'json',
            'addressdetails': 1,
            'zoom': 18,
            'accept-language': 'es'
        }
        
        headers = {
            'User-Agent': 'LocalizadorColonias/1.0 (giovanni.gzz102@gmail.com)'
        }
        
        try:
            response = requests.get(self.nominatim_url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return self._procesar_respuesta(data)
            else:
                return {'error': f"Error HTTP {response.status_code}"}
                
        except Exception as e:
            return {'error': f"Error de conexión: {e}"}
        finally:
            time.sleep(1)
    
    def _procesar_respuesta(self, data):
        """Procesa la respuesta de la API para coordenadas"""
        if 'address' not in data:
            return {'error': 'No se encontró información para estas coordenadas'}
        
        address = data['address']
        
        # Intentar obtener la colonia de diferentes campos
        colonia = (
            address.get('suburb') or
            address.get('neighbourhood') or
            address.get('residential') or
            address.get('quarter') or
            'No especificada'
        )
        
        return {
            'colonia': colonia,
            'municipio': address.get('city', address.get('town', address.get('municipality', 'No disponible'))),
            'estado': address.get('state', 'No disponible'),
            'coordenadas': {
                'lat': data.get('lat'),
                'lon': data.get('lon')
            }
        }
    
def main():
    localizador = LocalizadorColonias()
    
    try:
        #lat = float(input("Latitud (ej. 25.686614): "))
        #lon = float(input("Longitud (ej. -100.316112): "))

        lat = 25.65240075381403
        lon = -100.30283765582529 
        print("\n BUSCANDO COLONIA POR GPS")
        
        
        resultado = localizador.obtener_colonia_por_coordenadas(lat, lon)
        
        if 'error' in resultado:
            print(f"\n Error: {resultado['error']}")
        else:
            print(f"\n INFORMACIÓN ENCONTRADA:")
            print(f"Colonia: {resultado['colonia']}")
            #print(f"Código Postal: {resultado['codigo_postal']}")
            print(f"Municipio: {resultado['municipio']}")
            print(f"Estado: {resultado['estado']}")
            print(f"Dirección: {resultado['direccion_completa']}")
    
    except ValueError:
        print("Error: Formato de coordenadas incorrecto")
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    except Exception as e:
        print(f"Error inesperado: {e}")

# Función para probar con ejemplos conocidos de Monterrey
def ejemplos_monterrey():
    """Ejemplos de coordenadas y CPs en Monterrey"""
    localizador = LocalizadorColonias()
    
    ejemplos_coordenadas = [
        ("Centro de Monterrey", 25.686614, -100.316112),
        ("San Pedro Garza García", 25.657983, -100.378357),
        ("Tec de Monterrey", 25.651564, -100.289342),
        ("Parque Fundidora", 25.678927, -100.284752),
    ]
    
    for nombre, lat, lon in ejemplos_coordenadas:
        print(f"\n{nombre}:")
        resultado = localizador.obtener_colonia_por_coordenadas(lat, lon)
        if 'colonia' in resultado:
            print(f"   Colonia: {resultado['colonia']}")
            print(f"   CP: {resultado['codigo_postal']}")
            print(f"Dirección: {resultado['direccion_completa']}")
        time.sleep(2)

if __name__ == "__main__":
    main()
    
    # Descomenta para ver ejemplos
    # print("\n" + "="*60)
    # ejemplos_monterrey()