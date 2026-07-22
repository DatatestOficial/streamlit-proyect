import streamlit as st
import streamlit_authenticator as stauth
from login import get_authenticator

authenticator = get_authenticator()
st.session_state.authenticator = authenticator

# CONFIGURACIÓN INICIAL
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.get("authentication_status"):
    st.set_page_config(page_title="PROBIEN",page_icon="🌽",layout="wide")
else:
    st.set_page_config(page_title="PROBIEN",page_icon="🌽",layout="centered")

try:
    authenticator.login(location='main',
            fields={
            'Form name': 'Iniciar sesión', # Título del formulario
            'Username': 'Usuario',# Texto sobre el campo de usuario
            'Password': 'Contraseña',# Texto sobre el campo de contraseña
            'Login': 'Entrar'# Texto del botón de envío
        }
    )

except Exception as e:
    st.error(str(e))
    st.stop()

dashboard_page = st.Page("dashboard.py", title="Dashboard", icon="📊",default=True)

if st.session_state.get("authentication_status"):
    st.navigation([dashboard_page]).run()

elif st.session_state.get("authentication_status") is False:
    st.error("❌ Usuario o contraseña incorrectos")

elif st.session_state.get("authentication_status") is None:
    st.info("🔐 Bienvenido al panel de seguimiento")

