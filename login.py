import streamlit as st
import streamlit_authenticator as stauth

# from supabase import create_client, Client

# @st.cache_resource
# def init_supabase() -> Client:
#     return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# supabase = init_supabase()

# def cargar_credenciales_desde_supabase():
#     response = supabase.table("usuarios").select("*").execute()
    
#     # Estructura requerida por streamlit-authenticator
#     credentials = {"usernames": {}}
    
#     for row in response.data:
#         credentials["usernames"][row["username"]] = {
#             "email": row["email"],
#             "name": row["name"],
#             "password": row["password_hash"] # Ya viene encriptada desde la DB
#         }
#     return credentials

# credenciales = cargar_credenciales_desde_supabase()

# try:
#     if authenticator.reset_password(st.session_state["username"]):
#         # Si el usuario cambia la contraseña, actualizamos Supabase
#         nuevo_hash = credentials["usernames"][st.session_state["username"]]["password"]
#         supabase.table("usuarios").update({"password_hash": nuevo_hash}).eq("username", st.session_state["username"]).execute()
#         st.success('Contraseña actualizada en la base de datos.')
# except Exception as e:
#     st.error(e)

def get_authenticator():
    def to_plain_dict(obj):
        if hasattr(obj, "items"):
            return {k: to_plain_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [to_plain_dict(x) for x in obj]
        return obj
    # 1. Cargar las credenciales y configuración desde los secretos
    credenciales = to_plain_dict(st.secrets["auth"]["credentials"])
    cookie_config = to_plain_dict(st.secrets["auth"]["cookie"])
    # print(f"credenciales login: {credenciales}")
    # print("Credenciales cargadas:", credenciales)
    return  stauth.Authenticate(
        credenciales,
        cookie_config["name"],
        cookie_config["key"],
        cookie_config["expiry_days"],
    )


