import streamlit as st
import hashlib

# --- Configuración de la página ---
st.set_page_config(
    page_title="Login",
    page_icon="🔐",
    layout="centered"
)   

# --- Base de datos simulada de usuarios ---
# En producción, usar una base de datos real
USERS_DB = {
    "admin": {
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "nombre": "Administrador",
        "email": "admin@ejemplo.com"
    },
    "usuario": {
        "password": hashlib.sha256("user123".encode()).hexdigest(),
        "nombre": "Usuario Demo",
        "email": "usuario@ejemplo.com"
    }
}


def hash_password(password: str) -> str:
    """Hashea la contraseña con SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verificar_credenciales(username: str, password: str) -> bool:
    """Verifica si las credenciales son correctas."""
    if username in USERS_DB:
        return USERS_DB[username]["password"] == hash_password(password)
    return False


def login_page():
    """Muestra la página de login."""
    st.markdown(
        """
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
        }
        .stButton > button {
            width: 100%;
            background-color: #4CAF50;
            color: white;
            padding: 0.5rem;
            border-radius: 5px;
            border: none;
            font-size: 16px;
        }
        .stButton > button:hover {
            background-color: #45a049;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --- Header ---
    st.markdown("🔐 Iniciar Sesión", unsafe_allow_html=True)
    st.markdown("Ingresa usuario y contraseña para acceder", unsafe_allow_html=True)
    st.markdown("---")

    # --- Formulario de login ---
    with st.form("login_form"):
        username = st.text_input(
            "👤 Usuario",
            placeholder="Ingresa tu usuario"
        )
        password = st.text_input(
            "🔑 Contraseña",
            type="password",
            placeholder="Ingresa tu contraseña"
        )

        submit = st.form_submit_button("Iniciar Sesión")

        if submit:
            if not username or not password:
                st.error("⚠️ Por favor, completa todos los campos.")
            elif verificar_credenciales(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["nombre"] = USERS_DB[username]["nombre"]
                st.session_state["email"] = USERS_DB[username]["email"]
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos.")

    # --- Info de demo ---
    with st.expander("ℹ️ Credenciales de prueba"):
        st.markdown("""
* Usuario: admin | Contraseña: admin123
- Usuario: usuario | Contraseña: user123
        """)


# def dashboard_page():
#     """Muestra la página principal después del login."""
#     # --- Sidebar ---
#     with st.sidebar:
#         st.markdown(f"### 👋 Hola, {st.session_state['nombre']}")
#         st.markdown(f"📧 {st.session_state['email']}")
#         st.markdown("---")

#         if st.button("🚪 Cerrar Sesión"):
#             st.session_state["authenticated"] = False
#             st.session_state["username"] = None
#             st.session_state["nombre"] = None
#             st.session_state["email"] = None
#             st.rerun()

#     # --- Contenido principal ---
#     st.markdown("🎉 ¡Bienvenido!", unsafe_allow_html=True)
#     st.markdown(f"Has iniciado sesión como: {st.session_state['username']}", unsafe_allow_html=True)

#     st.markdown("---")

#     # --- Dashboard de ejemplo ---
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         st.metric("📊 Visitas", "1,234", "+12%")
#     with col2:
#         st.metric("👥 Usuarios", "567", "+5%")
#     with col3:
#         st.metric("💰 Ventas", "$8,901", "+8%")

#     st.markdown("---")
#     st.success("✅ Esta es tu área protegida. Solo usuarios autenticados pueden ver esto.")

#     st.balloons()
#     st.snow()
#     st.toast(  
#         "¡Has accedido al dashboard!",
#         icon="🎉",
#         duration=3000
#     )


# # --- Control de flujo principal ---
# def main():
#     # Inicializar estado de sesión
#     if "authenticated" not in st.session_state:
#         st.session_state["authenticated"] = False

#     # Mostrar página según autenticación
#     if st.session_state["authenticated"]:
#         dashboard_page()
#     else:
#         login_page()


# if __name__ == "__main__":
#     main()