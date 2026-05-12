import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productosAPI } from '../services/api';
import {
  ArrowLeft, RefreshCw, ExternalLink, TrendingDown,
  TrendingUp, Bell, Trash2, Loader
} from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';
import { useTheme } from '../contexts/ThemeContext';

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { isDark } = useTheme();

  const { data: producto, isLoading } = useQuery({
    queryKey: ['producto', id],
    queryFn: () => productosAPI.obtener(id).then(res => res.data),
  });

  const actualizarMutation = useMutation({
    mutationFn: () => productosAPI.actualizarPrecio(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['producto', id]);
      queryClient.invalidateQueries(['productos']);
    },
  });

  const eliminarMutation = useMutation({
    mutationFn: () => productosAPI.eliminar(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['productos']);
      navigate('/productos');
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (!producto) {
    return (
      <div className="card text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Producto no encontrado</h2>
        <Link to="/productos" className="text-primary-600 hover:text-primary-700">
          Volver a productos
        </Link>
      </div>
    );
  }

  // Preparar datos para el grafico
  const chartData = producto.historial.map(item => ({
    fecha: format(parseISO(item.fecha), 'dd/MM', { locale: es }),
    fechaCompleta: format(parseISO(item.fecha), 'dd MMM yyyy HH:mm', { locale: es }),
    precio: item.precio,
  }));

  const precioMin = producto.precio_min || 0;
  const precioMax = producto.precio_max || 100;
  const margen = (precioMax - precioMin) * 0.1;

  // Colores del grafico segun tema
  const gridColor = isDark ? '#374151' : '#e5e7eb';
  const axisColor = isDark ? '#9ca3af' : '#6b7280';
  const tooltipBg = isDark ? '#1f2937' : '#ffffff';
  const tooltipBorder = isDark ? '#374151' : '#e5e7eb';
  const tooltipText = isDark ? '#e5e7af' : '#111827';

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="space-y-3 sm:space-y-0">
        <Link
          to="/productos"
          className="inline-flex items-center space-x-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white text-sm sm:text-base"
        >
          <ArrowLeft className="w-4 h-4 sm:w-5 sm:h-5" />
          <span>Volver a productos</span>
        </Link>

        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
          <div className="flex-1">
            <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white break-words">{producto.nombre}</h1>

            <a
              href={producto.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-2 text-primary-600 hover:text-primary-700 mt-2 text-sm sm:text-base"
            >
              <span>Ver en tienda</span>
              <ExternalLink className="w-3 h-3 sm:w-4 sm:h-4" />
            </a>
          </div>

          <div className="flex gap-2 sm:flex-shrink-0">
            <button
              onClick={() => actualizarMutation.mutate()}
              disabled={actualizarMutation.isPending}
              className="btn-secondary flex items-center justify-center space-x-2 flex-1 sm:flex-initial min-h-[44px] text-sm sm:text-base"
            >
              <RefreshCw className={`w-4 h-4 sm:w-5 sm:h-5 ${actualizarMutation.isPending ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">Actualizar</span>
            </button>

            <button
              onClick={() => {
                if (confirm('Estas seguro de eliminar este producto?')) {
                  eliminarMutation.mutate();
                }
              }}
              disabled={eliminarMutation.isPending}
              className="px-3 sm:px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium flex items-center justify-center space-x-2 min-h-[44px] min-w-[44px]"
              title="Eliminar producto"
            >
              <Trash2 className="w-4 h-4 sm:w-5 sm:h-5" />
              <span className="hidden sm:inline">Eliminar</span>
            </button>
          </div>
        </div>
      </div>

      {/* Alerta */}
      {producto.alerta && (
        <div className="card border-red-200 bg-red-50 dark:bg-red-900/20 dark:border-red-800">
          <div className="flex items-center space-x-2 sm:space-x-3">
            <Bell className="w-5 h-5 sm:w-6 sm:h-6 text-red-600 flex-shrink-0" />
            <div>
              <h3 className="text-sm sm:text-base font-bold text-red-900 dark:text-red-200">Alerta de Precio</h3>
              <p className="text-xs sm:text-sm text-red-700 dark:text-red-300">Este producto ha alcanzado tu precio objetivo</p>
            </div>
          </div>
        </div>
      )}

      {/* Metricas */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-6">
        <div className="card">
          <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-300 mb-1">Precio Actual</p>
          <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white">
            {producto.precio_actual ? `$${producto.precio_actual.toFixed(2)}` : 'N/A'}
          </p>
        </div>

        <div className="card">
          <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-300 mb-1">Precio Minimo</p>
          <div className="flex items-center space-x-1 sm:space-x-2">
            <TrendingDown className="w-4 h-4 sm:w-5 sm:h-5 lg:w-6 lg:h-6 text-green-600 flex-shrink-0" />
            <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-green-600">
              {producto.precio_min ? `$${producto.precio_min.toFixed(2)}` : 'N/A'}
            </p>
          </div>
        </div>

        <div className="card">
          <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-300 mb-1">Precio Maximo</p>
          <div className="flex items-center space-x-1 sm:space-x-2">
            <TrendingUp className="w-4 h-4 sm:w-5 sm:h-5 lg:w-6 lg:h-6 text-red-600 flex-shrink-0" />
            <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-red-600">
              {producto.precio_max ? `$${producto.precio_max.toFixed(2)}` : 'N/A'}
            </p>
          </div>
        </div>

        <div className="card">
          <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-300 mb-1">Precio Objetivo</p>
          <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-primary-600">
            {producto.precio_objetivo ? `$${producto.precio_objetivo.toFixed(2)}` : 'N/A'}
          </p>
        </div>
      </div>

      {/* Grafico */}
      {chartData.length > 0 ? (
        <div className="card">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white mb-4 sm:mb-6">Historial de Precios</h2>

          <ResponsiveContainer width="100%" height={300} className="sm:h-[400px]">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
              <XAxis
                dataKey="fecha"
                stroke={axisColor}
                style={{ fontSize: '12px' }}
              />
              <YAxis
                stroke={axisColor}
                style={{ fontSize: '12px' }}
                domain={[precioMin - margen, precioMax + margen]}
                tickFormatter={(value) => `$${value.toFixed(0)}`}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload[0]) {
                    return (
                      <div className="p-3 rounded-lg shadow-lg border" style={{ backgroundColor: tooltipBg, borderColor: tooltipBorder }}>
                        <p className="text-sm text-gray-600 dark:text-gray-300">{payload[0].payload.fechaCompleta}</p>
                        <p className="text-lg font-bold" style={{ color: tooltipText }}>
                          ${payload[0].value.toFixed(2)}
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />

              {/* Linea de precio objetivo */}
              {producto.precio_objetivo && (
                <ReferenceLine
                  y={producto.precio_objetivo}
                  stroke="#f97316"
                  strokeDasharray="5 5"
                  label={{ value: 'Objetivo', position: 'right', fill: '#f97316' }}
                />
              )}

              <Line
                type="monotone"
                dataKey="precio"
                stroke="#0ea5e9"
                strokeWidth={3}
                dot={{ fill: '#0ea5e9', r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="card text-center py-12">
          <p className="text-gray-600 dark:text-gray-300">No hay datos de historial disponibles</p>
        </div>
      )}

      {/* Tabla de historial */}
      {producto.historial.length > 0 && (
        <div className="card">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white mb-3 sm:mb-4">Registros</h2>

          <div className="-mx-4 sm:-mx-6 overflow-x-auto">
            <div className="inline-block min-w-full align-middle">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="text-left py-2 sm:py-3 px-3 sm:px-4 text-xs sm:text-sm font-semibold text-gray-700 dark:text-gray-200 whitespace-nowrap">Fecha</th>
                    <th className="text-right py-2 sm:py-3 px-3 sm:px-4 text-xs sm:text-sm font-semibold text-gray-700 dark:text-gray-200 whitespace-nowrap">Precio</th>
                    <th className="text-right py-2 sm:py-3 px-3 sm:px-4 text-xs sm:text-sm font-semibold text-gray-700 dark:text-gray-200 whitespace-nowrap">Cambio</th>
                  </tr>
                </thead>
              <tbody>
                {producto.historial.slice().reverse().map((item, index, arr) => {
                  const cambio = index < arr.length - 1
                    ? item.precio - arr[index + 1].precio
                    : 0;

                  return (
                    <tr key={index} className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                      <td className="py-2 sm:py-3 px-3 sm:px-4 text-xs sm:text-sm text-gray-900 dark:text-white whitespace-nowrap">
                        {format(parseISO(item.fecha), 'dd MMM yyyy HH:mm', { locale: es })}
                      </td>
                      <td className="py-2 sm:py-3 px-3 sm:px-4 text-right text-xs sm:text-sm font-semibold text-gray-900 dark:text-white whitespace-nowrap">
                        ${item.precio.toFixed(2)}
                      </td>
                      <td className="py-2 sm:py-3 px-3 sm:px-4 text-right text-xs sm:text-sm whitespace-nowrap">
                        {index < arr.length - 1 ? (
                          <span className={cambio > 0 ? 'text-red-600' : cambio < 0 ? 'text-green-600' : 'text-gray-500 dark:text-gray-400'}>
                            {cambio > 0 ? '+' : ''}{cambio.toFixed(2)}
                          </span>
                        ) : (
                          <span className="text-gray-400 dark:text-gray-500">-</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
