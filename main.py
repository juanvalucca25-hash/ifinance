import streamlit as st
import sqlite3
import pandas as pd
import os
import base64
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="iFinance - Gastos Express", page_icon="💰", layout="centered")

# 🎨 INYECCIÓN DE ESTILOS DEFINITIVA (MANTIENE TUS 6 ÍTEMS DE ILLUSTRATOR)
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
    
    /* CONTENEDOR DE FORMULARIO */
    .bloque-formulario, .bloque-seccion {
        background-color: transparent !important;
        margin-top: 20px !important;
    }
    
    /* 🟨 FORZADO DE BOTONES NATIVOS (AMARILLOS CON LETRAS NEGRAS) */
    div.stButton > button {
        background-color: #F9D61C !important; 
        color: #0D1617 !important;            
        width: 100% !important;
        height: 50px !important;               
        border-radius: 12px !important;
        font-weight: bold !important;
        font-size: 18px !important;
        font-family: 'Candara', sans-serif !important;
        border: none !important;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2) !important;
        transition: background-color 0.2s ease;
    }
    
    /* Efecto al tocar o hacer clic */
    div.stButton > button:hover, div.stButton > button:active, div.stButton > button:focus {
        background-color: #E2C012 !important;
        color: #0D1617 !important;
        border: none !important;
    }
    
    /* ⬛ PROTECCIÓN DE CASILLAS INTERNAS */
    input[type="text"], input[type="number"], input[type="password"], .stNumberInput input, .stSelectbox div {
        background-color: #0D1617 !important;
        color: #F9D61C !important;
        font-family: 'Candara', sans-serif !important;
    }
    .stSelectbox button, .stNumberInput button {
        background-color: #0D1617 !important;
        color: #F9D61C !important;
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

DB_SISTEMA = "sistema_usuarios_v3.db"

# --- CORE DE AUTENTICACIÓN AVANZADA ---
def init_sistema_db():
    conn = sqlite3.connect(DB_SISTEMA)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            apellido TEXT,
            email TEXT UNIQUE,
            password TEXT,
            db_name TEXT
        )
    """)
    conn.commit()
    conn.close()

init_sistema_db()

if "usuario_autenticado" not in st.session_state:
    st.session_state.usuario_autenticado = False
if "db_usuario" not in st.session_state:
    st.session_state.db_usuario = ""
if "nombre_usuario" not in st.session_state:
    st.session_state.nombre_usuario = ""

# PANTALLA DE ACCESO PROFESIONAL NATIVA
if not st.session_state.usuario_autenticado:
    st.markdown("### Control de Acceso iFinance")
    
    opcion_login = st.radio("¿Qué deseas hacer?", options=["Iniciar Sesión", "Registrar Nueva Cuenta"])
    
    if opcion_login == "Iniciar Sesión":
        login_email = st.text_input("Correo Electrónico (Mail)").strip().lower()
        login_pass = st.text_input("Contraseña", type="password", placeholder="******")
        
        if st.button("Ingresar a mi Cuenta", use_container_width=True):
            if not login_email or not login_pass:
                st.warning("Por favor, completá ambos campos.")
            else:
                conn = sqlite3.connect(DB_SISTEMA)
                cursor = conn.cursor()
                cursor.execute("SELECT nombre, apellido, db_name FROM usuarios WHERE email = ? AND password = ?", (login_email, login_pass))
                resultado = cursor.fetchone()
                conn.close()
                
                if resultado:
                    nom, ape, archivo_db = resultado
                    st.session_state.usuario_autenticado = True
                    st.session_state.nombre_usuario = f"{nom} {ape}"
                    st.session_state.db_usuario = str(archivo_db)
                    st.success(f"¡Bienvenido de vuelta, {nom}!")
                    st.rerun()
                else:
                    st.error("Mail o contraseña incorrectos.")
                    
    else:
        reg_nombre = st.text_input("Nombre").strip()
        reg_apellido = st.text_input("Apellido").strip()
        reg_email = st.text_input("Correo Electrónico (Mail)").strip().lower()
        reg_pass = st.text_input("Elegí tu Contraseña", type="password", placeholder="Mínimo 6 caracteres").strip()
        
        if st.button("Crear Cuenta iFinance", use_container_width=True):
            if not reg_nombre or not reg_apellido or not reg_email or not reg_pass:
                st.warning("Por favor, completá todos los casilleros vacíos.")
            elif "@" not in reg_email or "." not in reg_email:
                st.error("Ingresá un formato de mail válido (ejemplo@gmail.com).")
            elif len(reg_pass) < 6:
                st.error("La contraseña tiene que tener un mínimo de 6 caracteres.")
            else:
                try:
                    id_mail_limpio = "".join(c for c in reg_email if c.isalnum())
                    nombre_db_generado = f"gastos_privados_{id_mail_limpio}.db"
                    
                    conn = sqlite3.connect(DB_SISTEMA)
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO usuarios (nombre, apellido, email, password, db_name) VALUES (?, ?, ?, ?, ?)", 
                                   (reg_nombre, reg_apellido, reg_email, reg_pass, nombre_db_generado))
                    conn.commit()
                    conn.close()
                    st.success(f"¡Excelente registro, {reg_nombre}! Cuenta creada con éxito. Pasá a la pestaña de 'Iniciar Sesión' para ingresar.")
                except sqlite3.IntegrityError:
                    st.error("Ese correo electrónico ya está registrado por otro usuario.")
    st.stop()

def obtener_db_actual():
    return st.session_state.db_usuario

# --- BASE DE DATOS MODULAR INDEPENDIENTE ---
def init_db():
    conn = sqlite3.connect(obtener_db_actual())
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
    conn = sqlite3.connect(obtener_db_actual())
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM categorias")
    filas = cursor.fetchall()
    conn.close()
    return [fila for fila in filas]
def guardar_gasto_db(monto, categoria):
    conn = sqlite3.connect(obtener_db_actual())
    cursor = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Parche de seguridad para que la categoría entre limpia a la base de datos
    cat_limpia = str(categoria).replace("('", "").replace("',)", "").replace("(", "").replace(")", "").strip()
    
    cursor.execute("INSERT INTO gastos (monto, categoria, fecha) VALUES (?, ?, ?)", (float(monto), cat_limpia, fecha_actual))
    conn.commit()
    conn.close()

def agregar_categoria_db(nombre):
    conn = sqlite3.connect(obtener_db_actual())
    cursor = conn.cursor()
    # Limpieza estricta de texto antes de guardar
    nombre_limpio = str(nombre).replace("('", "").replace("',)", "").replace("(", "").replace(")", "").strip()
    cursor.execute("INSERT INTO categorias (nombre) VALUES (?)", (nombre_limpio,))
    conn.commit()
    conn.close()

def obtener_datos_mes_actual():
    conn = sqlite3.connect(obtener_db_actual())
    mes_actual = datetime.now().strftime("%Y-%m")
    query = f"SELECT monto, categoria FROM gastos WHERE fecha LIKE '{mes_actual}%'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def obtener_historial_db():
    conn = sqlite3.connect(obtener_db_actual())
    cursor = conn.cursor()
    cursor.execute("SELECT monto, categoria, fecha FROM gastos ORDER BY id DESC LIMIT 10")
    filas = cursor.fetchall()
    conn.close()
    return filas


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

# Inicializar o cargar de forma segura la base de datos del usuario autenticado
init_db()

# 🧲 DETECTOR INTELIGENTE DE ATAJO MÓVIL: Lee si se disparó el modo ultra rápido
parametros_url = st.query_params
es_modo_rapido = parametros_url.get("modo") == "rapido"

# SI ES MODO RÁPIDO: Oculta todo el panel pesado y va directo al grano
if es_modo_rapido:
    st.write(f"⚡ Carga rápida para: **{st.session_state.nombre_usuario}**")
    
    monto = st.number_input("Monto ($)", value=None, placeholder="Introduce un número", format="%.2f", key="monto_fijo_fast")
    lista_cats = obtener_categorias()
    lista_limpia = [str(c).replace("('", "").replace("',)", "").replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("'", "").strip() for c in lista_cats]
    categoria_seleccionada = st.selectbox("Categoria", options=lista_limpia, key="cat_fast")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Cargar", key="btn_cargar_fast", use_container_width=True):
        if monto is None or monto <= 0:
            st.error("El monto tiene que ser mayor a 0.")
        else:
            guardar_gasto_db(monto, categoria_seleccionada)
            st.success(f"¡Anotado ${monto:.2f}!")
            st.info("Ya podés cerrar este panel.")
            st.stop()
            
    st.stop() # Frena la ejecución del código acá para no dibujar el resto de la app pesada

# --- MODO NORMAL COMERCIAL: (Se ejecuta si abrís la app desde el escritorio) ---

st.write(f"🔒 Cuenta activa: **{st.session_state.nombre_usuario}**")

df_mes = obtener_datos_mes_actual()
total_mes = df_mes["monto"].sum() if not df_mes.empty else 0.0

st.markdown("### Resumen Mensual")
nombre_mes_actual = datetime.now().strftime("%B %Y").capitalize()
st.metric(label=f"Total Gastado en {nombre_mes_actual}", value=f"${total_mes:,.2f}")

# Gráfico de Pizza Centrado y Estable con Paleta de 5 Colores
if not df_mes.empty:
    df_pizza = df_mes.groupby("categoria")["monto"].sum().reset_index()
    colores_gajos = ["#F9D61C", "#1B9E7D", "#0D1617", "#000000", "#0F1D3D"]
    
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
    monto = st.number_input("Monto ($)", value=None, placeholder="Introduce un número", format="%.2f", key="monto_fijo_v9")
with col2:
    lista_cats = obtener_categorias()
    lista_limpia = [str(c).replace("('", "").replace("',)", "").replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("'", "").strip() for c in lista_cats]
    categoria_seleccionada = st.selectbox("Categoria", options=lista_limpia)

# Botón Oficial de "Cargar"
st.markdown("<br>", unsafe_allow_html=True)
if st.button("Cargar", key="btn_forzado_cargar", use_container_width=True):
    if monto is None or monto <= 0:
        st.error("El monto tiene que ser mayor a 0.")
    else:
        guardar_gasto_db(monto, categoria_seleccionada)
        st.success(f"Anotado ${monto:.2f} en {categoria_seleccionada}")
        st.rerun()


# --- BOTONES DE DESPLIEGUE VERTICAL INTERACTIVOS ---

if "mostrar_historial" not in st.session_state:
    st.session_state.mostrar_historial = False
if "mostrar_config" not in st.session_state:
    st.session_state.mostrar_config = False

# Botón 2 Oficial (Historial)
st.markdown("<br>", unsafe_allow_html=True)
if st.button("Ver Ultimos Movimientos", key="btn_ver_historial", use_container_width=True):
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

# Botón 3 Oficial (Configuración)
st.markdown("<br>", unsafe_allow_html=True)
if st.button("Configurar Categorias", key="btn_ver_config", use_container_width=True):
    st.session_state.mostrar_config = not st.session_state.mostrar_config

if st.session_state.mostrar_config:
    st.markdown("<br>", unsafe_allow_html=True)
    nueva_cat = st.text_input("Nombre de la nueva categoria (Ej: Entretenimiento)").strip()
    
    if st.button("Crear Nueva Categoria", key="btn_crear_nueva_cat_final", use_container_width=True):
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

# --- BOTÓN DE SALIDA SEGURO ---
st.markdown("---")
if st.button("🔒 Cerrar Sesión Privada", use_container_width=True):
    st.session_state.usuario_autenticado = False
    st.session_state.db_usuario = ""
    st.session_state.nombre_usuario = ""
    st.rerun()
