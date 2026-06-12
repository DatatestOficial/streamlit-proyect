from login import login_page
from dashboard import dashboard_page

import streamlit as st
# import base64
# import plotly.express as px
# import plotly.graph_objects as go
# import pandas as pd
# import numpy as np
# import polars as pl
# import datetime
# from datetime import date
# import json

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN INICIAL
# ═══════════════════════════════════════════════════════════════════════════════
# st.set_page_config(
#     page_title="PROBIEN",
#     page_icon="🌽",
#     layout="wide"
# )

# --- Control de flujo principal ---
def main():
    # Inicializar estado de sesión
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    # Mostrar página según autenticación
    if st.session_state["authenticated"]:
        dashboard_page()
    else:
        login_page()


if __name__ == "__main__":
    main()
