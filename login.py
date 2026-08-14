###############################
# El bueno

import streamlit as st
import psycopg
import streamlit_authenticator as stauth


def to_plain_dict(obj):
    if hasattr(obj, "items"):
        return {k: to_plain_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_plain_dict(x) for x in obj]
    return obj


def get_authenticator():
    with psycopg.connect(st.secrets["supabase"]["DATABASE_URL"]) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT username, password_hash, name
                FROM public.usuarios
            """)
            usuarios = cur.fetchall()

    credenciales = {
        "usernames": {
            username: {
                "name": name,
                "password": password_hash
            }
            for username, password_hash, name in usuarios
        }
    }

    cookie_config = to_plain_dict(st.secrets["auth"]["cookie"])

    return stauth.Authenticate(
        credenciales,
        cookie_config["name"],
        cookie_config["key"],
        cookie_config["expiry_days"],
    )