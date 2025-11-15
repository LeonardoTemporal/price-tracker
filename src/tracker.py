"""
Módulo Tracker para el Price Tracker.
Coordina las operaciones entre el scraper y la base de datos.

Author: HellSpawn
"""
from typing import List, Dict, Optional
from datetime import datetime
import time

from .database import Database
from .scraper import PriceScraper


class Tracker:
    """Clase principal que coordina el rastreo de precios."""
    
    def __init__(self, db_path: str = "price_tracker.db"):
        """
        Inicializa el tracker.
        
        Args:
            db_path: Ruta al archivo de base de datos
        """
        self.db = Database(db_path)
        self.scraper = PriceScraper()
    
    async def agregar_producto(self, nombre: str, url: str, precio_objetivo: Optional[float] = None) -> Dict:
        """
        Añade un nuevo producto y obtiene su precio inicial.
        
        Args:
            nombre: Nombre del producto
            url: URL del producto
            precio_objetivo: Precio objetivo para alertas (opcional)
        
        Returns:
            Diccionario con el resultado de la operación
        """
        try:
            # Primero prueba si se puede acceder a la URL y extraer el precio
            print(f"Probando URL: {url}")
            precio_inicial = await self.scraper.get_price(url)
            
            if precio_inicial is None:
                return {
                    'exito': False,
                    'mensaje': 'No se pudo extraer el precio de la URL. Verifica que la URL sea correcta.',
                    'producto_id': None
                }
            
            # Añade el producto a la base de datos
            producto_id = self.db.agregar_producto(nombre, url, precio_objetivo)
            
            # Registra el precio inicial en el historial
            self.db.agregar_precio_historial(producto_id, precio_inicial)
            
            return {
                'exito': True,
                'mensaje': f'Producto añadido exitosamente. Precio inicial: ${precio_inicial:.2f}',
                'producto_id': producto_id,
                'precio_inicial': precio_inicial
            }
            
        except ValueError as e:
            return {
                'exito': False,
                'mensaje': str(e),
                'producto_id': None
            }
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error inesperado: {str(e)}',
                'producto_id': None
            }
    
    async def actualizar_precio(self, producto_id: int) -> Dict:
        """
        Actualiza el precio de un producto específico.
        
        Args:
            producto_id: ID del producto
        
        Returns:
            Diccionario con el resultado de la actualización
        """
        try:
            producto = self.db.obtener_producto(producto_id)
            
            if not producto:
                return {
                    'exito': False,
                    'mensaje': 'Producto no encontrado',
                    'producto_id': producto_id
                }
            
            # Extrae datos del producto
            _, nombre, url, precio_objetivo, activo, _ = producto
            
            if not activo:
                return {
                    'exito': False,
                    'mensaje': 'El producto está inactivo',
                    'producto_id': producto_id
                }
            
            # Obtiene el precio actual
            precio_actual = await self.scraper.get_price(url)
            
            if precio_actual is None:
                return {
                    'exito': False,
                    'mensaje': 'No se pudo extraer el precio actual',
                    'producto_id': producto_id
                }
            
            # Registra el nuevo precio
            self.db.agregar_precio_historial(producto_id, precio_actual)
            
            # Verifica si hay alerta
            alerta = False
            if precio_objetivo and precio_actual <= precio_objetivo:
                alerta = True
            
            return {
                'exito': True,
                'mensaje': 'Precio actualizado exitosamente',
                'producto_id': producto_id,
                'nombre': nombre,
                'precio_actual': precio_actual,
                'precio_objetivo': precio_objetivo,
                'alerta': alerta
            }
            
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error: {str(e)}',
                'producto_id': producto_id
            }
    
    async def actualizar_todos_los_precios(self) -> List[Dict]:
        """
        Actualiza los precios de todos los productos activos.
        
        Returns:
            Lista de diccionarios con los resultados de cada actualización
        """
        productos = self.db.obtener_productos(solo_activos=True)
        resultados = []
        
        for producto in productos:
            producto_id = producto[0]
            resultado = await self.actualizar_precio(producto_id)
            resultados.append(resultado)
            
            # Pausa breve entre solicitudes para no sobrecargar los servidores
            time.sleep(2)
        
        return resultados
    
    def obtener_resumen_productos(self) -> List[Dict]:
        """
        Obtiene un resumen de todos los productos con su último precio.
        
        Returns:
            Lista de diccionarios con información de cada producto
        """
        productos = self.db.obtener_productos(solo_activos=True)
        resumen = []
        
        for producto in productos:
            producto_id, nombre, url, precio_objetivo, fecha_creacion = producto
            ultimo_precio = self.db.obtener_ultimo_precio(producto_id)
            historial = self.db.obtener_historial(producto_id)
            
            # Calcula estadísticas
            precios = [precio for _, precio in historial]
            precio_min = min(precios) if precios else None
            precio_max = max(precios) if precios else None
            
            # Verifica si hay alerta
            alerta = False
            if precio_objetivo and ultimo_precio and ultimo_precio <= precio_objetivo:
                alerta = True
            
            resumen.append({
                'id': producto_id,
                'nombre': nombre,
                'url': url,
                'precio_actual': ultimo_precio,
                'precio_objetivo': precio_objetivo,
                'precio_min': precio_min,
                'precio_max': precio_max,
                'num_registros': len(historial),
                'fecha_creacion': fecha_creacion,
                'alerta': alerta
            })
        
        return resumen
    
    def obtener_alertas(self) -> List[Dict]:
        """
        Obtiene todos los productos que han alcanzado o bajado del precio objetivo.
        
        Returns:
            Lista de diccionarios con las alertas activas
        """
        alertas = self.db.obtener_alertas()
        resultado = []
        
        for alerta in alertas:
            producto_id, nombre, precio_actual, precio_objetivo = alerta
            ahorro = precio_objetivo - precio_actual
            porcentaje_ahorro = (ahorro / precio_objetivo) * 100
            
            resultado.append({
                'id': producto_id,
                'nombre': nombre,
                'precio_actual': precio_actual,
                'precio_objetivo': precio_objetivo,
                'ahorro': ahorro,
                'porcentaje_ahorro': porcentaje_ahorro
            })
        
        return resultado
    
    async def probar_url(self, url: str) -> Dict:
        """
        Prueba si una URL es válida y se puede extraer el precio.
        
        Args:
            url: URL a probar
        
        Returns:
            Diccionario con información de la prueba
        """
        return await self.scraper.test_url(url)
