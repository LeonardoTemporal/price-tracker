import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { productosAPI } from '../services/api';
import { PlusCircle, TestTube, CheckCircle, XCircle, Loader } from 'lucide-react';

export default function AddProduct() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState({
    nombre: '',
    url: '',
    precio_objetivo: '',
  });
  
  const [testResult, setTestResult] = useState(null);

  const testUrlMutation = useMutation({
    mutationFn: (url) => productosAPI.testUrl(url),
    onSuccess: (response) => {
      setTestResult(response.data);
    },
  });

  const crearProductoMutation = useMutation({
    mutationFn: (data) => productosAPI.crear(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['productos']);
      navigate('/productos');
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const data = {
      nombre: formData.nombre,
      url: formData.url,
      precio_objetivo: formData.precio_objetivo ? parseFloat(formData.precio_objetivo) : null,
    };
    
    crearProductoMutation.mutate(data);
  };

  const handleTestUrl = () => {
    if (formData.url) {
      setTestResult(null);
      testUrlMutation.mutate(formData.url);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Añadir Producto</h1>
        <p className="text-gray-600 mt-1">Añade un nuevo producto para rastrear su precio</p>
      </div>

      {/* Formulario */}
      <form onSubmit={handleSubmit} className="card space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nombre del Producto *
          </label>
          <input
            type="text"
            value={formData.nombre}
            onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
            className="input"
            placeholder="Ej: Laptop Dell XPS 13"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            URL del Producto *
          </label>
          <div className="flex space-x-2">
            <input
              type="url"
              value={formData.url}
              onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              className="input flex-1"
              placeholder="https://..."
              required
            />
            <button
              type="button"
              onClick={handleTestUrl}
              disabled={!formData.url || testUrlMutation.isPending}
              className="btn-secondary flex items-center space-x-2 whitespace-nowrap"
            >
              {testUrlMutation.isPending ? (
                <Loader className="w-5 h-5 animate-spin" />
              ) : (
                <TestTube className="w-5 h-5" />
              )}
              <span>Probar</span>
            </button>
          </div>
          
          {/* Resultado del test */}
          {testResult && (
            <div className={`mt-3 p-4 rounded-lg ${
              testResult.accesible && testResult.precio
                ? 'bg-green-50 border border-green-200'
                : 'bg-yellow-50 border border-yellow-200'
            }`}>
              <div className="flex items-start space-x-2">
                {testResult.accesible && testResult.precio ? (
                  <>
                    <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                    <div>
                      <p className="font-medium text-green-900">URL válida</p>
                      <p className="text-sm text-green-700 mt-1">
                        Precio detectado: <span className="font-semibold">${testResult.precio.toFixed(2)}</span>
                      </p>
                    </div>
                  </>
                ) : (
                  <>
                    <XCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
                    <div>
                      <p className="font-medium text-yellow-900">
                        {testResult.accesible ? 'URL accesible pero sin precio' : 'Error al acceder'}
                      </p>
                      {testResult.error && (
                        <p className="text-sm text-yellow-700 mt-1">{testResult.error}</p>
                      )}
                    </div>
                  </>
                )}
              </div>
            </div>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Precio Objetivo (opcional)
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">$</span>
            <input
              type="number"
              step="0.01"
              min="0"
              value={formData.precio_objetivo}
              onChange={(e) => setFormData({ ...formData, precio_objetivo: e.target.value })}
              className="input pl-8"
              placeholder="0.00"
            />
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Recibirás una alerta cuando el precio baje a este nivel
          </p>
        </div>

        {/* Error message */}
        {crearProductoMutation.isError && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-700">
              {crearProductoMutation.error?.response?.data?.detail || 'Error al crear el producto'}
            </p>
          </div>
        )}

        {/* Botones */}
        <div className="flex space-x-3 pt-4">
          <button
            type="submit"
            disabled={crearProductoMutation.isPending}
            className="btn-primary flex-1 flex items-center justify-center space-x-2"
          >
            {crearProductoMutation.isPending ? (
              <Loader className="w-5 h-5 animate-spin" />
            ) : (
              <PlusCircle className="w-5 h-5" />
            )}
            <span>{crearProductoMutation.isPending ? 'Añadiendo...' : 'Añadir Producto'}</span>
          </button>
          
          <button
            type="button"
            onClick={() => navigate('/productos')}
            className="btn-secondary"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
}
