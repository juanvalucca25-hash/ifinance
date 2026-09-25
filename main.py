import streamlit as st
import sqlite3
import pandas as pd
import os
import base64
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="iFinance - Gastos Express", page_icon="💰", layout="centered")

# 🎨 INYECCIÓN DE ESTILOS FILTRADA MILIMÉTRICAMENTE (SOLO AFECTA A NUESTRAS BARRAS PREMIUM)
st.markdown(
    """
    <style>
    /* Fondo general de la app y tipografía Candara global */
    .stApp {
        background-color: #0D1617 !important;
        font-family: 'Candara', sans-serif !important;
    }
    
    /* 🟨 BARRA SUPERIOR AMARILLO DORADO (MARCA CENTRADA) */
    .top-banner {
        background-color: #F9D61C !important;
        width: 100% !important;
        padding: 20px 0 !important;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        border-radius: 12px !important;
        margin-bottom: 35px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
    }
    .header-logo {
        width: 45px !important;
        height: auto !important;
        display: inline-block;
    }
    .header-letras {
        height: 32px !important;
        width: auto !important;
        display: inline-block;
    }

    /* 🟩 CONTENEDOR DEL GRÁFICO (VERDE ESMERALDA CON BORDE REDONDEADO) */
    [data-testid="stMetricBlock"], .stPlotlyChart {
        background-color: #0F4643 !important;
        border-radius: 20px !important;
        padding: 20px !important;
        border: None !important;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.4);
    }
    
    /* Títulos principales afuera de los bloques (color amarillo) */
    h3, [data-testid="stMarkdownContainer"] h3 {
        color: #F9D61C !important;
        font-family: 'Candara', sans-serif !important;
        text-align: center !important;
    }
    
    /* Texto de etiqueta de la métrica mensual */
    .stMetric label {
        color: #F9D61C !important;
        font-family: 'Candara', sans-serif !important;
        font-weight: bold !important;
    }
    
    /* El número del total mensual grande */
    [data-testid="stMetricValue"] {
        color: #F3F4F6 !important;
        font-family: 'Candara', sans-serif !important;
        text-align: center !important;
        display: flex;
        justify-content: center;
    }
    
    /* Centrar contenedor del gráfico Plotly y Ocultar camarita */
    .stPlotlyChart {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        margin: 0 auto !important;
    }
    .modebar {
        display: none !important;
    }
    
    /* 🟨 NUEVO TRUCO: CLASE EXCLUSIVA PARA LOS 3 BOTONES DE iFINANCE */
    .boton-premium {
        background-color: #F9D61C !important; /* Fondo Amarillo */
        color: #0D1617 !important;            /* Letras Negras Internas */
        width: 100% !important;
        height: 50px !important;               /* Grosor táctil cómodo */
        border-radius: 12px !important;
        font-weight: bold !important;
        font-size: 18px !important;
        font-family: 'Candara', sans-serif !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        margin-top: 15px !important;
        margin-bottom: 10px !important;
        border: none !important;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2) !important;
        text-decoration: none !important;
    }
    .boton-premium:active {
        background-color: #E2C012 !important; /* Oscurece levemente al tocarlo */
    }
    
    /* ⬛ RESETEO MANDATORIO: Fuerza a las casillas y selectores nativos a ser negros puros */
    input[type="text"], input[type="number"], .stNumberInput input, .stSelectbox div {
        background-color: #0D1617 !important;
        color: #F9D61C !important;
        font-family: 'Candara', sans-serif !important;
    }
    
    /* Alertas internas adaptadas limpias */
    .stSuccess, .stError, .stWarning, .stInfo {
        background-color: #0D1617 !important;
        color: #F9D61C !important;
        border: 1px solid #F9D61C !important;
        font-family: 'Candara', sans-serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

DB_NAME = "mis_gastos_v2.db"

# --- BASE DE DATOS FIJA (RESGUARDADA) ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monto REAL,
            categoria TEXT,
            fecha TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE
        )
    """)
    try:
        cursor.executemany("INSERT INTO categorias (nombre) VALUES (?)", 
                           [("Comida",), ("Transporte",), ("Cigarrillos",), ("Golosinas",)])
    except sqlite3.IntegrityError:
        pass
    conn.commit()
    conn.close()

def obtener_categorias():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM categorias")
    filas = cursor.fetchall()
    conn.close()
    return [fila for fila in filas]
def guardar_gasto_db(monto, categoria):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Parche de seguridad para que la categoría entre limpia a la base de datos
    cat_limpia = str(categoria).replace("('", "").replace("',)", "").replace("(", "").replace(")", "").strip()
    
    cursor.execute("INSERT INTO gastos (monto, categoria, fecha) VALUES (?, ?, ?)", (float(monto), cat_limpia, fecha_actual))
    conn.commit()
    conn.close()

def agregar_categoria_db(nombre):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Limpieza estricta de texto antes de guardar
    nombre_limpio = str(nombre).replace("('", "").replace("',)", "").replace("(", "").replace(")", "").strip()
    cursor.execute("INSERT INTO categorias (nombre) VALUES (?)", (nombre_limpio,))
    conn.commit()
    conn.close()

def obtener_datos_mes_actual():
    conn = sqlite3.connect(DB_NAME)
    mes_actual = datetime.now().strftime("%Y-%m")
    query = f"SELECT monto, categoria FROM gastos WHERE fecha LIKE '{mes_actual}%'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def obtener_historial_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT monto, categoria, fecha FROM gastos ORDER BY id DESC LIMIT 10")
    filas = cursor.fetchall()
    conn.close()
    return filas

# Inicialización de la base de datos v2
init_db()

df_mes = obtener_datos_mes_actual()
total_mes = df_mes["monto"].sum() if not df_mes.empty else 0.0

# --- INTERFAZ VISUAL NATIVA ---

carpeta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_logo = os.path.join(carpeta_actual, "logo.png")
ruta_letras = os.path.join(carpeta_actual, "letras.png")

# RENDERIZADO DEL ENCABEZADO
if os.path.exists(ruta_logo) and os.path.exists(ruta_letras):
    def obtener_base64_imagen(ruta):
        with open(ruta, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
            
    logo_b64 = obtener_base64_imagen(ruta_logo)
    letras_b64 = obtener_base64_imagen(ruta_letras)
    
    st.markdown(
        f"""
        <div class="top-banner">
            <img src="data:image/png;base64,{logo_b64}" class="header-logo">
            <img src="data:image/png;base64,{letras_b64}" class="header-letras">
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.title("iFinance")

st.markdown("### Resumen Mensual")
nombre_mes_actual = datetime.now().strftime("%B %Y").capitalize()
st.metric(label=f"Total Gastado en {nombre_mes_actual}", value=f"${total_mes:,.2f}")

# Gráfico de Pizza Centrado y Estable
if not df_mes.empty:
    df_pizza = df_mes.groupby("categoria")["monto"].sum().reset_index()
    colores_gajos = ["#F9D61C", "#0F4643", "#D9B814", "#1b635f", "#A68D11"]
    
    st.plotly_chart(
        {
            "data": [{
                "values": df_pizza["monto"],
                "labels": df_pizza["categoria"],
                "type": "pie",
                "hole": 0.4,
                "textinfo": "percent+label",
                "textfont": {"color": "#F3F4F6", "size": 13},
                "marker": {"colors": colores_gajos}
            }],
            "layout": {
                "showlegend": True,
                "legend": {
                    "orientation": "h",
                    "yanchor": "bottom",
                    "y": -0.25,
                    "xanchor": "center",
                    "x": 0.5,
                    "font": {"color": "#F9D61C"}
                },
                "margin": {"l": 10, "r": 10, "t": 10, "b": 10},
                "height": 360,
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)"
            }
        },
        use_container_width=True,
        config={"displayModeBar": False}
    )
else:
    st.info("Todavía no registraste gastos este mes.")

st.markdown("---")

# --- FORMULARIO DE ACCIÓN DE CARGA ---
st.markdown("### Anotar Gasto")

col1, col2 = st.columns(2)
with col1:
    monto = st.number_input("Monto ($)", min_value=0.0, step=50.0, format="%.2f")
with col2:
    lista_cats = obtener_categorias()
    lista_limpia = [str(c).replace("('", "").replace("',)", "").replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("'", "").strip() for c in lista_cats]
    categoria_seleccionada = st.selectbox("Categoria", options=lista_limpia)

# Botón 1 Aislado con HTML Seguro (Anotar Gasto)
btn_anotar = st.html('<button class="boton-premium">Anotar Gasto</button>')
if btn_anotar:
    if monto > 0:
        guardar_gasto_db(monto, categoria_seleccionada)
        st.success(f"Anotado ${monto:.2f} en {categoria_seleccionada}")
        st.rerun()


# --- BOTONES DE DESPLIEGUE VERTICAL AISLADOS ---

if "mostrar_historial" not in st.session_state:
    st.session_state.mostrar_historial = False
if "mostrar_config" not in st.session_state:
    st.session_state.mostrar_config = False

# Botón 2 Aislado con HTML Seguro (Historial)
if st.html('<button class="boton-premium">Ver Ultimos Movimientos</button>'):
    st.session_state.mostrar_historial = not st.session_state.mostrar_historial

if st.session_state.mostrar_historial:
    st.markdown("<br>", unsafe_allow_html=True)
    registros = obtener_historial_db()
    if not registros:
        st.info("No hay movimientos registrados.")
    else:
        for m, c, f in registros:
            c_limpia = str(c).replace("('", "").replace("',)", "").replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("'", "").strip()
            st.info(f"${m:,.2f} — {c_limpia} \n {f}")

# Botón 3 Aislado con HTML Seguro (Configuración)
if st.html('<button class="boton-premium">Configurar Categorias</button>'):
    st.session_state.mostrar_config = not st.session_state.mostrar_config

if st.session_state.mostrar_config:
    st.markdown("<br>", unsafe_allow_html=True)
    nueva_cat = st.text_input("Nombre de la nueva categoria (Ej: Entretenimiento)").strip()
    
    # Este botón interno de confirmación sí es estándar y seguro
    if st.button("Crear Nueva Categoria", type="primary", use_container_width=True):
        if not nueva_cat:
            st.warning("Escribi un nombre.")
        else:
            lista_cats_actuales = obtener_categorias()
            lista_actuales_limpias = [str(c).replace("('", "").replace("',)", "").replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("'", "").strip() for c in lista_cats_actuales]
            
            if nueva_cat in lista_actuales_limpias:
                st.error("Esa categoria ya existe.")
            else:
                agregar_categoria_db(nueva_cat)
                st.success(f"Categoria '{nueva_cat}' agregada con éxito.")
                st.rerun()
