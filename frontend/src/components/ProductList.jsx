import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { productosAPI } from '../services/api';
import { Package, RefreshCw, Bell, TrendingUp, ExternalLink } from 'lucide-react';

export default function ProductList() {
  const queryClient = useQueryClient();

  const { data: productos, isLoading } = useQuery({
    queryKey: ['productos'],
    queryFn: () => productosAPI.listar().then(res => res.data),
  });

  const actualizarTodosMutation = useMutation({
    mutationFn: () => productosAPI.actualizarTodos(),
    onSuccess: () => {
      queryClient.invalidateQueries(['productos']);
      queryClient.invalidateQueries(['alertas']);
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Productos</h1>
          <p className="text-sm sm:text-base text-gray-600 mt-1">Gestiona tus productos en seguimiento</p>
        </div>
        
        <button
          onClick={() => actualizarTodosMutation.mutate()}
          disabled={actualizarTodosMutation.isPending}
          className="btn-primary flex items-center justify-center space-x-2 min-h-[44px] w-full sm:w-auto"
        >
          <RefreshCw className={`w-5 h-5 ${actualizarTodosMutation.isPending ? 'animate-spin' : ''}`} />
          <span className="text-sm sm:text-base">{actualizarTodosMutation.isPending ? 'Actualizando...' : 'Actualizar Todos'}</span>
        </button>
      </div>

      {/* Lista de productos */}
      {productos && productos.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
          {productos.map((producto) => (
            <div key={producto.id} className="card hover:shadow-md transition-shadow">
              <div className="flex flex-col sm:flex-row sm:items-start justify-between mb-3 sm:mb-4 gap-2">
                <div className="flex-1">
                  <Link to={`/productos/${producto.id}`} className="hover:text-primary-600">
                    <h3 className="text-lg sm:text-xl font-bold text-gray-900">{producto.nombre}</h3>
                  </Link>
                  <a 
                    href={producto.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-xs sm:text-sm text-primary-600 hover:text-primary-700 flex items-center space-x-1 mt-1"
                  >
                    <span>Ver producto</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
                
                {producto.alerta && (
                  <div className="flex items-center space-x-1 bg-red-100 text-red-700 px-2 sm:px-3 py-1 rounded-full">
                    <Bell className="w-3 h-3 sm:w-4 sm:h-4" />
                    <span className="text-xs sm:text-sm font-medium">Alerta</span>
                  </div>
                )}
              </div>

              {/* Precio actual */}
              {producto.precio_actual ? (
                <div className="mb-3 sm:mb-4">
                  <p className="text-xs sm:text-sm text-gray-600">Precio Actual</p>
                  <p className="text-2xl sm:text-3xl font-bold text-gray-900">${producto.precio_actual.toFixed(2)}</p>
                </div>
              ) : (
                <div className="mb-3 sm:mb-4">
                  <p className="text-sm text-gray-500">Sin precio registrado</p>
                </div>
              )}

              {/* Estadísticas */}
              <div className="grid grid-cols-3 gap-2 sm:gap-4 pt-3 sm:pt-4 border-t border-gray-200">
                <div>
                  <p className="text-[10px] sm:text-xs text-gray-600">Mínimo</p>
                  <p className="text-sm sm:text-lg font-semibold text-green-600">
                    {producto.precio_min ? `$${producto.precio_min.toFixed(2)}` : 'N/A'}
                  </p>
                </div>
                <div>
                  <p className="text-[10px] sm:text-xs text-gray-600">Máximo</p>
                  <p className="text-sm sm:text-lg font-semibold text-red-600">
                    {producto.precio_max ? `$${producto.precio_max.toFixed(2)}` : 'N/A'}
                  </p>
                </div>
                <div>
                  <p className="text-[10px] sm:text-xs text-gray-600">Registros</p>
                  <p className="text-sm sm:text-lg font-semibold text-gray-900">{producto.num_registros}</p>
                </div>
              </div>

              {/* Objetivo */}
              {producto.precio_objetivo && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Precio Objetivo:</span>
                    <span className="text-lg font-semibold text-gray-900">
                      ${producto.precio_objetivo.toFixed(2)}
                    </span>
                  </div>
                </div>
              )}

              {/* Botón ver detalles */}
              <Link 
                to={`/productos/${producto.id}`}
                className="mt-3 sm:mt-4 w-full block text-center btn-secondary min-h-[44px] flex items-center justify-center text-sm sm:text-base"
              >
                Ver Detalles
              </Link>
            </div>
          ))}
        </div>
      ) : (
        <div className="card text-center py-8 sm:py-12">
          <Package className="w-12 h-12 sm:w-16 sm:h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-2">No hay productos</h3>
          <p className="text-sm sm:text-base text-gray-600 mb-4 sm:mb-6">Comienza añadiendo tu primer producto</p>
          <Link to="/agregar" className="btn-primary inline-block min-h-[44px] px-6 flex items-center text-sm sm:text-base">
            Añadir Producto
          </Link>
        </div>
      )}
    </div>
  );
}
