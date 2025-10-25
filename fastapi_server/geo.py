import requests
import time

class LocalizadorColonias:
    def __init__(self):
        self.session = requests.Session()
        self.nominatim_url = "https://nominatim.openstreetmap.org/reverse"
        self.headers = {
            'User-Agent': 'LocalizadorColonias/1.0 (giovanni.gzz102@gmail.com)'
        }
    
    def obtener_colonia_por_coordenadas(self, latitud:float, longitud:float) -> str:
        """Obtiene la colonia usando coordenadas GPS"""
        params = {
            'lat': latitud,
            'lon': longitud,
            'format': 'json',
            'addressdetails': 1,
            'zoom': 18,
            'accept-language': 'es'
        }
        
        try:
            time.sleep(1)
            response = requests.get(self.nominatim_url, params=params, headers=self.headers)
            
            if response.status_code != 200:
                raise ValueError(f"Error HTTP {response.status_code} al consultar Nominatim: {response.text}")
            data = response.json()
            return self._procesar_respuesta(data)
                
        except requests.RequestException as e:
            # Captura errores de red (timeout, DNS, etc.)
            raise ValueError(f"Error de conexión con Nominatim: {e}") from e
        except ValueError:
            # Re-lanza errores ya identificados, como 'no se encontró dirección'
            raise
        except Exception as e:
            # Captura cualquier otro error inesperado
            raise ValueError(f"Error inesperado en geocodificación: {e}") from e
    
    def _procesar_respuesta(self, data: dict) -> str:
        """Procesa la respuesta de la API para coordenadas"""
        if 'address' not in data:
            raise ValueError('No se encontró información para estas coordenadas')
        
        address = data['address']
        
        # Intentar obtener la colonia de diferentes campos
        colonia = (
            address.get('suburb') or
            address.get('neighbourhood') or
            address.get('residential') or
            address.get('quarter') or
            'No especificada'
        )
        
        return colonia