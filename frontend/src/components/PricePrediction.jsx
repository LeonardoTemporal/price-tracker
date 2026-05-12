import { useQuery } from '@tanstack/react-query';
import { productosAPI } from '../services/api';
import { TrendingDown, TrendingUp, Minus, Brain, AlertTriangle, CheckCircle } from 'lucide-react';

export default function PricePrediction({ productoId, precioObjetivo }) {
  const { data: prediction, isLoading } = useQuery({
    queryKey: ['prediction', productoId],
    queryFn: () => productosAPI.predict(productoId).then(res => res.data),
    enabled: !!productoId,
  });

  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
        <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-2"></div>
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
      </div>
    );
  }

  if (!prediction || !prediction.datos_suficientes) {
    return (
      <div className="card border-yellow-200 bg-yellow-50 dark:bg-yellow-900/20 dark:border-yellow-800">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 text-yellow-600" />
          <h3 className="text-lg font-bold text-yellow-900 dark:text-yellow-200">Prediccion de Precio (IA)</h3>
        </div>
        <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-2">
          {prediction?.mensaje || 'No hay suficientes datos para predecir. Se necesitan al menos 3 registros de precio.'}
        </p>
      </div>
    );
  }

  const { tendencia, prediccion_siguiente, confianza, dias_estimados_objetivo } = prediction;

  const getTrendIcon = () => {
    if (tendencia === 'subiendo') return <TrendingUp className="w-6 h-6 text-red-500" />;
    if (tendencia === 'bajando') return <TrendingDown className="w-6 h-6 text-green-500" />;
    return <Minus className="w-6 h-6 text-gray-500" />;
  };

  const getTrendText = () => {
    if (tendencia === 'subiendo') return 'El precio esta subiendo';
    if (tendencia === 'bajando') return 'El precio esta bajando';
    return 'El precio es estable';
  };

  const getTrendColor = () => {
    if (tendencia === 'subiendo') return 'text-red-600';
    if (tendencia === 'bajando') return 'text-green-600';
    return 'text-gray-600';
  };

  const getConfidenceColor = () => {
    if (confianza >= 0.7) return 'text-green-600';
    if (confianza >= 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="card border-primary-200 dark:border-primary-800">
      <div className="flex items-center space-x-2 mb-4">
        <Brain className="w-5 h-5 text-primary-600" />
        <h3 className="text-lg font-bold text-gray-900 dark:text-white">Prediccion de Precio (IA)</h3>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Prediccion siguiente */}
        <div className="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4">
          <p className="text-sm text-gray-600 dark:text-gray-300">Proximo precio estimado</p>
          <p className="text-2xl font-bold text-primary-600">
            ${prediccion_siguiente?.toFixed(2) || 'N/A'}
          </p>
        </div>

        {/* Tendencia */}
        <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            {getTrendIcon()}
            <div>
              <p className={`text-sm font-semibold ${getTrendColor()}`}>
                {getTrendText()}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Basado en {prediction.historial_usado} registros
              </p>
            </div>
          </div>
        </div>

        {/* Confianza */}
        <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
          <p className="text-sm text-gray-600 dark:text-gray-300">Confianza del modelo</p>
          <div className="flex items-center space-x-2">
            <div className="flex-1 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
              <div
                className="bg-primary-500 h-2 rounded-full transition-all"
                style={{ width: `${confianza * 100}%` }}
              ></div>
            </div>
            <span className={`text-sm font-bold ${getConfidenceColor()}`}>
              {(confianza * 100).toFixed(0)}%
            </span>
          </div>
        </div>

        {/* Estimacion precio objetivo */}
        {dias_estimados_objetivo !== null && precioObjetivo && (
          <div className={`rounded-lg p-4 ${
            dias_estimados_objetivo === 0
              ? 'bg-green-50 dark:bg-green-900/20'
              : 'bg-primary-50 dark:bg-primary-900/20'
          }`}>
            <div className="flex items-center space-x-2">
              {dias_estimados_objetivo === 0 ? (
                <CheckCircle className="w-5 h-5 text-green-600" />
              ) : (
                <Brain className="w-5 h-5 text-primary-600" />
              )}
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-300">Precio objetivo</p>
                <p className={`text-lg font-bold ${
                  dias_estimados_objetivo === 0 ? 'text-green-600' : 'text-primary-600'
                }`}>
                  {dias_estimados_objetivo === 0
                    ? 'Precio objetivo alcanzado pronto'
                    : `~${dias_estimados_objetivo} dias estimados`
                  }
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      <p className="text-xs text-gray-500 dark:text-gray-400 mt-4">
        La prediccion se calcula usando regresion lineal sobre el historial de precios.
        No es una garantia de precios futuros.
      </p>
    </div>
  );
}
