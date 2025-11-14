import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { productosAPI, alertasAPI } from '../services/api';
import { Bell, Package, RefreshCw, TrendingUp, TrendingDown } from 'lucide-react';

export default function Dashboard() {
  const { data: productos, isLoading: loadingProductos } = useQuery({
    queryKey: ['productos'],
    queryFn: () => productosAPI.listar().then(res => res.data),
  });

  const { data: alertas, isLoading: loadingAlertas } = useQuery({
    queryKey: ['alertas'],
    queryFn: () => alertasAPI.listar().then(res => res.data),
  });

  const { data: stats, isLoading: loadingStats } = useQuery({
    queryKey: ['estadisticas'],
    queryFn: () => productosAPI.estadisticas().then(res => res.data),
  });

  if (loadingProductos || loadingAlertas || loadingStats) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm sm:text-base text-gray-600 mt-1">Resumen de tu rastreador de precios</p>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs sm:text-sm text-gray-600">Total Productos</p>
              <p className="text-2xl sm:text-3xl font-bold text-gray-900 mt-1">{stats?.total_productos || 0}</p>
            </div>
            <Package className="w-10 h-10 sm:w-12 sm:h-12 text-primary-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs sm:text-sm text-gray-600">Alertas Activas</p>
              <p className="text-2xl sm:text-3xl font-bold text-gray-900 mt-1">{stats?.alertas_activas || 0}</p>
            </div>
            <Bell className="w-10 h-10 sm:w-12 sm:h-12 text-yellow-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs sm:text-sm text-gray-600">Ahorro Potencial</p>
              <p className="text-2xl sm:text-3xl font-bold text-green-600 mt-1">
                ${stats?.ahorro_potencial?.toFixed(2) || '0.00'}
              </p>
            </div>
            <TrendingDown className="w-10 h-10 sm:w-12 sm:h-12 text-green-600" />
          </div>
        </div>
      </div>

      {/* Alertas */}
      {alertas && alertas.length > 0 && (
        <div className="card border-red-200 bg-red-50">
          <div className="flex items-center space-x-2 mb-3 sm:mb-4">
            <Bell className="w-5 h-5 sm:w-6 sm:h-6 text-red-600" />
            <h2 className="text-lg sm:text-xl font-bold text-red-900">Alertas de Precio</h2>
          </div>
          
          <div className="space-y-3">
            {alertas.map((alerta) => (
              <div key={alerta.id} className="bg-white p-3 sm:p-4 rounded-lg border border-red-200">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 text-sm sm:text-base">{alerta.nombre}</h3>
                    <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-4 mt-2 text-xs sm:text-sm space-y-1 sm:space-y-0">
                      <span className="text-gray-600">
                        Precio actual: <span className="font-semibold text-green-600">${alerta.precio_actual.toFixed(2)}</span>
                      </span>
                      <span className="text-gray-600">
                        Objetivo: <span className="font-semibold">${alerta.precio_objetivo.toFixed(2)}</span>
                      </span>
                    </div>
                  </div>
                  <div className="text-left sm:text-right">
                    <p className="text-xl sm:text-2xl font-bold text-green-600">-${alerta.ahorro.toFixed(2)}</p>
                    <p className="text-xs sm:text-sm text-green-600">{alerta.porcentaje_ahorro.toFixed(1)}% ahorro</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Lista de productos recientes */}
      <div className="card">
        <div className="flex items-center justify-between mb-3 sm:mb-4">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900">Productos Recientes</h2>
          <Link to="/productos" className="text-sm sm:text-base text-primary-600 hover:text-primary-700 font-medium">
            Ver todos →
          </Link>
        </div>

        {productos && productos.length > 0 ? (
          <div className="space-y-3">
            {productos.slice(0, 5).map((producto) => (
              <Link
                key={producto.id}
                to={`/productos/${producto.id}`}
                className="block p-3 sm:p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-all"
              >
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 text-sm sm:text-base">{producto.nombre}</h3>
                    <p className="text-xs sm:text-sm text-gray-500 mt-1">{producto.num_registros} registros</p>
                  </div>
                  <div className="text-left sm:text-right">
                    {producto.precio_actual ? (
                      <>
                        <p className="text-xl sm:text-2xl font-bold text-gray-900">${producto.precio_actual.toFixed(2)}</p>
                        <div className="flex items-center sm:justify-end space-x-2 text-xs sm:text-sm text-gray-600 mt-1">
                          <span>Min: ${producto.precio_min?.toFixed(2)}</span>
                          <span>•</span>
                          <span>Max: ${producto.precio_max?.toFixed(2)}</span>
                        </div>
                      </>
                    ) : (
                      <p className="text-gray-500 text-sm">Sin datos</p>
                    )}
                  </div>
                </div>
                {producto.alerta && (
                  <div className="mt-2 flex items-center space-x-1 text-red-600">
                    <Bell className="w-4 h-4" />
                    <span className="text-xs sm:text-sm font-medium">Precio objetivo alcanzado</span>
                  </div>
                )}
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 sm:py-12">
            <Package className="w-12 h-12 sm:w-16 sm:h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-sm sm:text-base text-gray-600">No hay productos en seguimiento</p>
            <Link to="/agregar" className="btn-primary mt-4 inline-block text-sm sm:text-base px-4 py-2 sm:px-6 sm:py-3">
              Añadir tu primer producto
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
