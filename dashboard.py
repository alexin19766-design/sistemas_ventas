import streamlit as st
import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Dashboard Inteligente", page_icon="🧠", layout="wide")
st.title("🧠 Centro de Inteligencia de Ventas")

URL_BACKEND = "https://api-ventas-backend-2rq9.onrender.com" 

# --- CONTROL INTERACTIVO EN LA BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    margen_estimado = st.slider(
        "Margen de Ganancia (%)", 
        min_value=1, 
        max_value=99, 
        value=30, 
        help="Ajusta este valor para calcular tu margen de ganancia estimado."
    )
    st.info(f"Calculando un margen del **{margen_estimado}%**.")

if st.button("🔄 Actualizar Datos"):
    st.rerun()

try:
    respuesta = requests.get(f"{URL_BACKEND}/api/ventas")
    
    if respuesta.status_code == 200:
        datos = respuesta.json()
        
        if len(datos) > 0:
            df = pd.DataFrame(datos)
            df['fecha'] = pd.to_datetime(df['fecha'])
            df['mes'] = df['fecha'].dt.strftime('%B')
            
            df['costo'] = df['monto'] * (1 - (margen_estimado / 100))
            df['margen'] = df['monto'] - df['costo']

            # --- TARJETAS KPI GLOBALES ---
            col1, col2, col3 = st.columns(3)
            col1.metric("Ingresos Totales", f"Q {df['monto'].sum():,.2f}")
            col2.metric(f"Ganancia ({margen_estimado}%)", f"Q {df['margen'].sum():,.2f}")
            col3.metric("Ventas Realizadas", len(df))

            # --- CREACIÓN DE PESTAÑAS ---
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Ventas", "📈 Pronóstico (IA)", "💰 Márgenes", "🏆 Rendimiento"])

            # PESTAÑA 1: VENTAS
            with tab1:
                st.subheader("Ventas por Producto (Unidades)")
                ventas_unidades = df["producto"].value_counts()
                st.bar_chart(ventas_unidades)
                
                st.subheader("Ingresos por Producto (Dinero)")
                ingresos_producto = df.groupby("producto")["monto"].sum().sort_values(ascending=False)
                st.bar_chart(ingresos_producto)
                
                st.subheader("Ingresos por Día")
                ventas_dia = df.groupby(df['fecha'].dt.date)["monto"].sum()
                st.line_chart(ventas_dia)

            # PESTAÑA 2: PRONÓSTICO
            with tab2:
                st.subheader("🔮 Pronóstico de Ventas (Próximos 7 días)")
                df_diario = df.groupby(df['fecha'].dt.date)["monto"].sum().reset_index()
                
                if len(df_diario) >= 3:
                    df_diario['dia_num'] = np.arange(len(df_diario))
                    X = df_diario[['dia_num']]
                    y = df_diario['monto']
                    modelo = LinearRegression()
                    modelo.fit(X, y)
                    
                    dias_futuros = np.arange(len(df_diario), len(df_diario) + 7).reshape(-1, 1)
                    prediccion = modelo.predict(dias_futuros)
                    
                    fechas_futuras = pd.date_range(start=df_diario['fecha'].max() + pd.Timedelta(days=1), periods=7)
                    df_pred = pd.DataFrame({'fecha': fechas_futuras, 'monto_predicho': prediccion})
                    
                    st.line_chart(df_pred.set_index('fecha')['monto_predicho'])
                    st.info(f"💡 **Orientación:** La IA estima que podrías facturar **Q {prediccion.sum():,.2f}**.")
                else:
                    st.warning("⚠️ Necesitas al menos 3 días de ventas para generar un pronóstico.")

            # PESTAÑA 3: MÁRGENES
            with tab3:
                st.subheader(f"Margen de Ganancia por Producto (al {margen_estimado}%)")
                margen_prod = df.groupby("producto")["margen"].sum().sort_values(ascending=False)
                st.bar_chart(margen_prod, color="#00FF00")

            # PESTAÑA 4: RENDIMIENTO
            with tab4:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.subheader("🏆 Mejor Vendedor")
                    mejor_vendedor = df.groupby("vendedor")["monto"].sum().idxmax()
                    st.success(f"**{mejor_vendedor}** es el que más ha vendido.")
                    
                    st.subheader("📅 Mejor Mes")
                    mejor_mes = df.groupby("mes")["monto"].sum().idxmax()
                    st.success(f"El mes con más ventas ha sido **{mejor_mes}**.")

                with col_b:
                    st.subheader("📉 Peor Mes")
                    peor_mes = df.groupby("mes")["monto"].sum().idxmin()
                    st.warning(f"El mes con menos ventas ha sido **{peor_mes}**.")
                    
                    st.subheader("Ventas por Vendedor")
                    ventas_vend = df.groupby("vendedor")["monto"].sum()
                    st.bar_chart(ventas_vend)

        else:
            st.info("Aún no hay ventas registradas.")
    else:
        st.error("No se pudo conectar a la base de datos.")
except Exception as e:
    st.error(f"Error de conexión: {e}")
