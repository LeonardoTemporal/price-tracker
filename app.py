"""
Aplicación Streamlit para el Price Tracker.
Interfaz gráfica del usuario.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Añade el directorio padre al path para importar los módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tracker import Tracker


# Configuración de la página
st.set_page_config(
    page_title="Price Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializa el tracker
@st.cache_resource
def get_tracker():
    """Crea una instancia única del tracker."""
    return Tracker()

tracker = get_tracker()


# Estilos CSS personalizados
st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .alert-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        margin-bottom: 1rem;
    }
    .success-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)


def pagina_inicio():
    """Página principal con resumen y alertas."""
    st.title("💰 Price Tracker")
    st.markdown("### Bienvenido a tu rastreador de precios personal")
    
    # Obtiene alertas
    alertas = tracker.obtener_alertas()
    
    # Muestra alertas si existen
    if alertas:
        st.markdown("## 🔔 Alertas de Precio")
        for alerta in alertas:
            st.markdown(f"""
                <div class="alert-card">
                    <h3>🎯 {alerta['nombre']}</h3>
                    <p><strong>Precio actual:</strong> ${alerta['precio_actual']:.2f}</p>
                    <p><strong>Precio objetivo:</strong> ${alerta['precio_objetivo']:.2f}</p>
                    <p><strong>¡Ahorro:</strong> ${alerta['ahorro']:.2f} ({alerta['porcentaje_ahorro']:.1f}%)</p>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("---")
    
    # Resumen de productos
    st.markdown("## 📊 Resumen de Productos")
    resumen = tracker.obtener_resumen_productos()
    
    if not resumen:
        st.info("No hay productos en seguimiento. ¡Añade tu primer producto!")
    else:
        # Crea un DataFrame para mostrar
        df_data = []
        for producto in resumen:
            df_data.append({
                'ID': producto['id'],
                'Producto': producto['nombre'],
                'Precio Actual': f"${producto['precio_actual']:.2f}" if producto['precio_actual'] else "N/A",
                'Precio Objetivo': f"${producto['precio_objetivo']:.2f}" if producto['precio_objetivo'] else "N/A",
                'Precio Mín': f"${producto['precio_min']:.2f}" if producto['precio_min'] else "N/A",
                'Precio Máx': f"${producto['precio_max']:.2f}" if producto['precio_max'] else "N/A",
                'Registros': producto['num_registros'],
                '🔔': '✅' if producto['alerta'] else ''
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Botón para actualizar todos los precios
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("🔄 Actualizar Todos los Precios", type="primary"):
                with st.spinner("Actualizando precios..."):
                    resultados = tracker.actualizar_todos_los_precios()
                    
                    exitos = sum(1 for r in resultados if r['exito'])
                    st.success(f"✅ Se actualizaron {exitos} de {len(resultados)} productos")
                    
                    # Recarga la página
                    st.rerun()


def pagina_agregar_producto():
    """Página para añadir nuevos productos."""
    st.title("➕ Añadir Nuevo Producto")
    
    with st.form("form_nuevo_producto"):
        nombre = st.text_input("Nombre del producto", placeholder="Ej: Laptop Dell XPS 13")
        url = st.text_input("URL del producto", placeholder="https://...")
        precio_objetivo = st.number_input(
            "Precio objetivo (opcional)", 
            min_value=0.0, 
            value=0.0, 
            step=0.01,
            help="Recibirás una alerta cuando el precio baje a este nivel"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("Añadir Producto", type="primary")
        
        with col2:
            test_url = st.form_submit_button("Probar URL")
        
        if test_url and url:
            with st.spinner("Probando URL..."):
                resultado = tracker.probar_url(url)
                
                if resultado['accesible']:
                    if resultado['precio']:
                        st.success(f"✅ URL válida. Precio detectado: ${resultado['precio']:.2f}")
                    else:
                        st.warning(f"⚠️ URL accesible pero no se pudo extraer el precio. {resultado['error']}")
                else:
                    st.error(f"❌ No se pudo acceder a la URL. {resultado['error']}")
        
        if submitted:
            if not nombre or not url:
                st.error("Por favor completa todos los campos obligatorios")
            else:
                with st.spinner("Añadiendo producto..."):
                    precio_obj = precio_objetivo if precio_objetivo > 0 else None
                    resultado = tracker.agregar_producto(nombre, url, precio_obj)
                    
                    if resultado['exito']:
                        st.success(resultado['mensaje'])
                        st.balloons()
                    else:
                        st.error(resultado['mensaje'])


def pagina_productos_seguidos():
    """Página para ver productos en seguimiento y su historial."""
    st.title("📦 Productos Seguidos")
    
    resumen = tracker.obtener_resumen_productos()
    
    if not resumen:
        st.info("No hay productos en seguimiento")
        return
    
    # Selector de producto
    nombres_productos = [f"{p['nombre']} (ID: {p['id']})" for p in resumen]
    producto_seleccionado = st.selectbox("Selecciona un producto", nombres_productos)
    
    if producto_seleccionado:
        # Extrae el ID del producto
        producto_id = int(producto_seleccionado.split("ID: ")[1].rstrip(")"))
        
        # Busca el producto en el resumen
        producto = next(p for p in resumen if p['id'] == producto_id)
        
        # Información del producto
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Precio Actual", f"${producto['precio_actual']:.2f}" if producto['precio_actual'] else "N/A")
        
        with col2:
            st.metric("Precio Objetivo", f"${producto['precio_objetivo']:.2f}" if producto['precio_objetivo'] else "N/A")
        
        with col3:
            st.metric("Precio Mínimo", f"${producto['precio_min']:.2f}" if producto['precio_min'] else "N/A")
        
        with col4:
            st.metric("Precio Máximo", f"${producto['precio_max']:.2f}" if producto['precio_max'] else "N/A")
        
        st.markdown(f"**URL:** [{producto['url']}]({producto['url']})")
        
        # Botones de acción
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("🔄 Actualizar Precio"):
                with st.spinner("Actualizando..."):
                    resultado = tracker.actualizar_precio(producto_id)
                    
                    if resultado['exito']:
                        st.success(f"✅ Precio actualizado: ${resultado['precio_actual']:.2f}")
                        st.rerun()
                    else:
                        st.error(resultado['mensaje'])
        
        # Historial de precios
        st.markdown("### 📈 Historial de Precios")
        
        historial = tracker.db.obtener_historial(producto_id)
        
        if historial:
            # Prepara datos para el gráfico
            fechas = [datetime.fromisoformat(fecha) for fecha, _ in historial]
            precios = [precio for _, precio in historial]
            
            # Crea gráfico con Plotly
            fig = go.Figure()
            
            # Línea de precios
            fig.add_trace(go.Scatter(
                x=fechas,
                y=precios,
                mode='lines+markers',
                name='Precio',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=8)
            ))
            
            # Línea de precio objetivo si existe
            if producto['precio_objetivo']:
                fig.add_trace(go.Scatter(
                    x=[fechas[0], fechas[-1]],
                    y=[producto['precio_objetivo'], producto['precio_objetivo']],
                    mode='lines',
                    name='Precio Objetivo',
                    line=dict(color='#ff7f0e', width=2, dash='dash')
                ))
            
            fig.update_layout(
                title="Evolución del Precio",
                xaxis_title="Fecha",
                yaxis_title="Precio ($)",
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla de historial
            st.markdown("### 📋 Tabla de Registros")
            df_historial = pd.DataFrame({
                'Fecha': [fecha for fecha, _ in historial],
                'Precio': [f"${precio:.2f}" for _, precio in historial]
            })
            st.dataframe(df_historial, use_container_width=True, hide_index=True)
        else:
            st.info("No hay historial de precios para este producto")


def main():
    """Función principal de la aplicación."""
    # Sidebar para navegación
    st.sidebar.title("🧭 Navegación")
    
    pagina = st.sidebar.radio(
        "Ir a:",
        ["🏠 Inicio", "➕ Añadir Producto", "📦 Productos Seguidos"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Acerca de")
    st.sidebar.info(
        "**Price Tracker** te ayuda a seguir los precios de productos "
        "en línea y recibir alertas cuando bajen de precio."
    )
    
    # Renderiza la página seleccionada
    if pagina == "🏠 Inicio":
        pagina_inicio()
    elif pagina == "➕ Añadir Producto":
        pagina_agregar_producto()
    elif pagina == "📦 Productos Seguidos":
        pagina_productos_seguidos()


if __name__ == "__main__":
    main()
