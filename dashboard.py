import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Dashboard en Vivo", page_icon="📈")
st.title("📈 Panel de Control en Tiempo Real")

# ⚠️ OJO: Aquí también debes pegar el link de tu backend en Render
URL_BACKEND = "https://TU-LINK-DE-RENDER.onrender.com"

if st.button("🔄 Actualizar Datos"):
    st.rerun()

try:
    respuesta = requests.get(f"{URL_BACKEND}/api/ventas")
    
    if respuesta.status_code == 200:
        datos = respuesta.json()
        
        if len(datos) > 0:
            df = pd.DataFrame(datos)
            
            # KPIs (Tarjetas de resumen)
            col1, col2 = st.columns(2)
            col1.metric("Ingresos Totales", f"Q {df['monto'].sum():,.2f}")
            col2.metric("Ventas Realizadas", len(df))
            
            # Gráfico de Demanda
            st.subheader("Demanda por Producto")
            demanda = df.groupby("producto")["monto"].sum().sort_values(ascending=True)
            st.bar_chart(demanda)
            
            # Tabla detallada
            st.subheader("Últimas ventas")
            st.dataframe(df.sort_values(by="id", ascending=False))
        else:
            st.info("Aún no hay ventas registradas.")
    else:
        st.error("No se pudo conectar a la base de datos central.")
except Exception as e:
    st.error(f"Error de conexión: {e}")
