"""
Módulo de base de datos para el Price Tracker.
Gestiona la persistencia de productos y el historial de precios.

Author: HellSpawn
"""
import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional
import os


class Database:
    """Clase para gestionar la base de datos SQLite del rastreador de precios."""
    
    def __init__(self, db_path: str = "price_tracker.db"):
        """
        Inicializa la conexión a la base de datos.
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Obtiene una conexión a la base de datos."""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Crea las tablas necesarias si no existen."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de productos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                precio_objetivo REAL,
                activo INTEGER DEFAULT 1,
                fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de historial de precios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historial_precios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER NOT NULL,
                precio REAL NOT NULL,
                fecha TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def agregar_producto(self, nombre: str, url: str, precio_objetivo: Optional[float] = None) -> int:
        """
        Añade un nuevo producto a la base de datos.
        
        Args:
            nombre: Nombre del producto
            url: URL de la página del producto
            precio_objetivo: Precio objetivo para alertas (opcional)
        
        Returns:
            ID del producto insertado
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO productos (nombre, url, precio_objetivo)
                VALUES (?, ?, ?)
            ''', (nombre, url, precio_objetivo))
            
            producto_id = cursor.lastrowid
            conn.commit()
            return producto_id
        except sqlite3.IntegrityError:
            raise ValueError("Este producto ya existe en la base de datos")
        finally:
            conn.close()
    
    def obtener_productos(self, solo_activos: bool = True) -> List[Tuple]:
        """
        Obtiene todos los productos de la base de datos.
        
        Args:
            solo_activos: Si True, solo retorna productos activos
        
        Returns:
            Lista de tuplas con los datos de los productos
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if solo_activos:
            cursor.execute('''
                SELECT id, nombre, url, precio_objetivo, fecha_creacion
                FROM productos
                WHERE activo = 1
                ORDER BY fecha_creacion DESC
            ''')
        else:
            cursor.execute('''
                SELECT id, nombre, url, precio_objetivo, fecha_creacion, activo
                FROM productos
                ORDER BY fecha_creacion DESC
            ''')
        
        productos = cursor.fetchall()
        conn.close()
        return productos
    
    def obtener_producto(self, producto_id: int) -> Optional[Tuple]:
        """
        Obtiene un producto específico por su ID.
        
        Args:
            producto_id: ID del producto
        
        Returns:
            Tupla con los datos del producto o None si no existe
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, nombre, url, precio_objetivo, activo, fecha_creacion
            FROM productos
            WHERE id = ?
        ''', (producto_id,))
        
        producto = cursor.fetchone()
        conn.close()
        return producto
    
    def actualizar_producto(self, producto_id: int, nombre: str = None, 
                           precio_objetivo: float = None, activo: bool = None):
        """
        Actualiza los datos de un producto.
        
        Args:
            producto_id: ID del producto a actualizar
            nombre: Nuevo nombre (opcional)
            precio_objetivo: Nuevo precio objetivo (opcional)
            activo: Nuevo estado activo/inactivo (opcional)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if nombre is not None:
            updates.append("nombre = ?")
            params.append(nombre)
        
        if precio_objetivo is not None:
            updates.append("precio_objetivo = ?")
            params.append(precio_objetivo)
        
        if activo is not None:
            updates.append("activo = ?")
            params.append(1 if activo else 0)
        
        if updates:
            params.append(producto_id)
            query = f"UPDATE productos SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
    
    def eliminar_producto(self, producto_id: int):
        """
        Marca un producto como inactivo (no lo elimina físicamente).
        
        Args:
            producto_id: ID del producto a eliminar
        """
        self.actualizar_producto(producto_id, activo=False)
    
    def agregar_precio_historial(self, producto_id: int, precio: float, fecha: str = None):
        """
        Añade un registro de precio al historial.
        
        Args:
            producto_id: ID del producto
            precio: Precio registrado
            fecha: Fecha del registro (opcional, usa la actual por defecto)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if fecha:
            cursor.execute('''
                INSERT INTO historial_precios (producto_id, precio, fecha)
                VALUES (?, ?, ?)
            ''', (producto_id, precio, fecha))
        else:
            cursor.execute('''
                INSERT INTO historial_precios (producto_id, precio)
                VALUES (?, ?)
            ''', (producto_id, precio))
        
        conn.commit()
        conn.close()
    
    def obtener_historial(self, producto_id: int) -> List[Tuple]:
        """
        Obtiene el historial de precios de un producto.
        
        Args:
            producto_id: ID del producto
        
        Returns:
            Lista de tuplas (fecha, precio)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT fecha, precio
            FROM historial_precios
            WHERE producto_id = ?
            ORDER BY fecha ASC
        ''', (producto_id,))
        
        historial = cursor.fetchall()
        conn.close()
        return historial
    
    def obtener_ultimo_precio(self, producto_id: int) -> Optional[float]:
        """
        Obtiene el último precio registrado de un producto.
        
        Args:
            producto_id: ID del producto
        
        Returns:
            Último precio o None si no hay historial
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT precio
            FROM historial_precios
            WHERE producto_id = ?
            ORDER BY fecha DESC
            LIMIT 1
        ''', (producto_id,))
        
        resultado = cursor.fetchone()
        conn.close()
        return resultado[0] if resultado else None
    
    def obtener_alertas(self) -> List[Tuple]:
        """
        Obtiene productos cuyo último precio está por debajo del precio objetivo.
        
        Returns:
            Lista de tuplas (id, nombre, precio_actual, precio_objetivo)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.id, p.nombre, h.precio, p.precio_objetivo
            FROM productos p
            INNER JOIN (
                SELECT producto_id, precio, MAX(fecha) as max_fecha
                FROM historial_precios
                GROUP BY producto_id
            ) h ON p.id = h.producto_id
            WHERE p.activo = 1 
            AND p.precio_objetivo IS NOT NULL
            AND h.precio <= p.precio_objetivo
        ''')
        
        alertas = cursor.fetchall()
        conn.close()
        return alertas
