import streamlit as st
import requests

st.set_page_config(page_title="Registro de Ventas", page_icon="🛒")
st.title("🛒 Registrar Nueva Venta")

# ⚠️ OJO: Aquí debes pegar el link de tu backend en Render cuando lo crees más adelante
URL_BACKEND = "https://TU-LINK-DE-RENDER.onrender.com"

with st.form("formulario_venta"):
    producto = st.text_input("Nombre del Producto")
    monto = st.number_input("Monto de la venta (Q)", min_value=0.0)
    vendedor = st.text_input("Tu Nombre")
    
    boton_enviar = st.form_submit_button("Registrar Venta")

if boton_enviar:
    datos = {"producto": producto, "monto": monto, "vendedor": vendedor}
    try:
        respuesta = requests.post(f"{URL_BACKEND}/api/ventas", json=datos)
        if respuesta.status_code == 200:
            st.success("¡Venta registrada en tiempo real!")
            st.balloons() # Animación de celebración
        else:
            st.error(f"Error del servidor: {respuesta.status_code}")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
