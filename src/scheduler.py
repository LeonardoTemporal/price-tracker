"""
Módulo de automatización para el Price Tracker.
Programa actualizaciones automáticas de precios.

Author: HellSpawn
"""
import schedule
import time
from datetime import datetime
import sys
import os

# Añade el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tracker import Tracker


class AutoUpdater:
    """Clase para automatizar actualizaciones de precios."""
    
    def __init__(self, intervalo_horas: int = 6, db_path: str = "price_tracker.db"):
        """
        Inicializa el actualizador automático.
        
        Args:
            intervalo_horas: Intervalo en horas entre actualizaciones
            db_path: Ruta a la base de datos
        """
        self.tracker = Tracker(db_path)
        self.intervalo_horas = intervalo_horas
        self.ejecutando = False
    
    def actualizar_precios(self):
        """Actualiza todos los precios y muestra resultados."""
        print(f"\n{'='*60}")
        print(f"Iniciando actualización de precios - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        resultados = self.tracker.actualizar_todos_los_precios()
        
        # Muestra resultados
        exitos = 0
        fallos = 0
        
        for resultado in resultados:
            if resultado['exito']:
                exitos += 1
                print(f"[OK] {resultado['nombre']}: ${resultado['precio_actual']:.2f}", end="")
                
                if resultado['alerta']:
                    print(f" [ALERTA] Precio objetivo alcanzado")
                else:
                    print()
            else:
                fallos += 1
                print(f"[ERROR] Error en producto ID {resultado['producto_id']}: {resultado['mensaje']}")
        
        print(f"\nResumen: {exitos} exitosos, {fallos} fallos")
        
        # Muestra alertas activas
        alertas = self.tracker.obtener_alertas()
        if alertas:
            print(f"\nAlertas activas: {len(alertas)}")
            for alerta in alertas:
                print(f"   - {alerta['nombre']}: ${alerta['precio_actual']:.2f} "
                      f"(objetivo: ${alerta['precio_objetivo']:.2f}, ahorro: ${alerta['ahorro']:.2f})")
        
        print(f"\n{'='*60}\n")
    
    def iniciar(self):
        """Inicia el programador de actualizaciones."""
        self.ejecutando = True
        
        # Programa la actualización
        schedule.every(self.intervalo_horas).hours.do(self.actualizar_precios)
        
        print(f"Actualizador automático iniciado")
        print(f"Intervalo: cada {self.intervalo_horas} horas")
        print(f"Próxima actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nPresiona Ctrl+C para detener\n")
        
        # Ejecuta una actualización inmediata
        self.actualizar_precios()
        
        # Loop principal
        try:
            while self.ejecutando:
                schedule.run_pending()
                time.sleep(60)  # Verifica cada minuto
        except KeyboardInterrupt:
            print("\n\nDeteniendo actualizador automático...")
            self.ejecutando = False
    
    def detener(self):
        """Detiene el actualizador."""
        self.ejecutando = False
        schedule.clear()


def main():
    """Función principal para ejecutar el actualizador."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Actualizador automático de precios")
    parser.add_argument(
        '--intervalo',
        type=int,
        default=6,
        help='Intervalo en horas entre actualizaciones (default: 6)'
    )
    parser.add_argument(
        '--db',
        type=str,
        default='price_tracker.db',
        help='Ruta a la base de datos (default: price_tracker.db)'
    )
    parser.add_argument(
        '--una-vez',
        action='store_true',
        help='Ejecuta una sola actualización y termina'
    )
    
    args = parser.parse_args()
    
    updater = AutoUpdater(intervalo_horas=args.intervalo, db_path=args.db)
    
    if args.una_vez:
        print("Ejecutando actualización única...\n")
        updater.actualizar_precios()
    else:
        updater.iniciar()


if __name__ == "__main__":
    main()
