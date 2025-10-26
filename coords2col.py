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
        
        # Obtener calle
        calle = (
            address.get('road') or 
            address.get('street') or 
            address.get('pedestrian') or 
            'Sin calle'
        )
        
        return {
            'colonia': colonia,
            'municipio': address.get('city', address.get('town', address.get('municipality', 'No disponible'))),
            'estado': address.get('state', 'No disponible'),
            'calle': calle,
            'address': address,  # Incluir toda la información de address
            'coordenadas': {
                'lat': data.get('lat'),
                'lon': data.get('lon')
            }
        }
    
def otro_main():
    localizador = LocalizadorColonias()
    
    try:
        #lat = float(input("Latitud (ej. 25.686614): "))
        #lon = float(input("Longitud (ej. -100.316112): "))

        lat = 25.65076851606196 
        lon = -100.28913624508401
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

def main():
    localizador = LocalizadorColonias()
    
    # 20 coordenadas GPS diferentes de Monterrey y área metropolitana
    coordenadas = [
        (25.650000, -100.300000),
    (25.679100, -100.306000), 
    (25.698000, -100.330000), 
    (25.656000, -100.270000), 
    (25.710000, -100.290000), 
    (25.685000, -100.280000), 
    (25.640000, -100.310000), 
    (25.680000, -100.260000), 
    (25.689000, -100.339000), 
    (25.660000, -100.275000),
    (25.670000, -100.315000),
    (25.695000, -100.285000),
    (25.655000, -100.325000),
    (25.665000, -100.305000),
    (25.700000, -100.270000),
    (25.705000, -100.310000),
    (25.675000, -100.295000),
    (25.690000, -100.265000),
    (25.655000, -100.290000),
    (25.680000, -100.320000)
    ]
    
    print("BUSCANDO COLONIAS POR GPS:\n")
    
    for i, (lat, lon) in enumerate(coordenadas, 1):
        resultado = localizador.obtener_colonia_por_coordenadas(lat, lon)
        
        if 'error' in resultado:
            print(f"{lat} {lon} Error: {resultado['error']}")
        else:
            colonia = resultado.get('colonia', 'No especificada')
            municipio = resultado.get('municipio', 'No disponible')
            estado = resultado.get('estado', 'No disponible')
            
            # Obtener calle de la respuesta
            calle = "Sin calle"
            if 'address' in resultado:
                address = resultado['address']
                calle = (
                    address.get('road') or 
                    address.get('street') or 
                    address.get('pedestrian') or 
                    'Sin calle'
                )
            
            print(f"({lat}, {lon}) {colonia} . {municipio} . {calle} . {estado}")
        
        # Espera entre requests para no sobrecargar la API
        if i < len(coordenadas):
            time.sleep(1)

if __name__ == "__main__":
    main()
    
    # Descomenta para ver ejemplos
    # print("\n" + "="*60)
    # ejemplos_monterrey()