/**
 * API Service - Cliente para comunicación con el backend
 * Incluye interceptores para autenticación JWT
 * 
 * Author: HellSpawn
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para añadir token a todas las peticiones
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token inválido o expirado
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Autenticación
export const authAPI = {
  login: (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    return api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  register: (email, username, password) => 
    api.post('/auth/register', { email, username, password }),
  me: () => api.get('/auth/me'),
  logout: () => {
    localStorage.removeItem('token');
  },
};

// Productos
export const productosAPI = {
  listar: () => api.get('/productos/'),
  obtener: (id) => api.get(`/productos/${id}`),
  crear: (data) => api.post('/productos/', data),
  actualizar: (id, data) => api.put(`/productos/${id}`, data),
  eliminar: (id) => api.delete(`/productos/${id}`),
  actualizarPrecio: (id) => api.post(`/productos/${id}/actualizar-precio`),
  actualizarTodos: () => api.post('/productos/actualizar-todos'),
  testUrl: (url) => api.post('/productos/test-url', { url }),
  estadisticas: () => api.get('/productos/estadisticas/resumen'),
};

// Historial
export const historialAPI = {
  obtener: (productoId) => api.get(`/historial/${productoId}`),
};

// Alertas
export const alertasAPI = {
  listar: () => api.get('/alertas/'),
};

export default api;
