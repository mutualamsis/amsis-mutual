import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import os

# ==============================
# CONFIGURACIÓN GENERAL
# ==============================
st.set_page_config(
    page_title="Sistema de Gestión de Socios - A.M.S.I.S.",
    layout="wide",
    page_icon="💚"
)

DATA_FILE = "socios.csv"

# ==============================
# FUNCIONES AUXILIARES
# ==============================
def cargar_datos():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "ID", "Nombre", "Apellido", "DNI", "Teléfono", "Email",
            "SubNombre", "SubApellido", "SubDNI", "SubTeléfono", "SubEmail",
            "Fecha Suscripción", "Vencimiento", "Estado"
        ])

def guardar_datos(df):
    df.to_csv(DATA_FILE, index=False)

def generar_id(df):
    return len(df) + 1 if not df.empty else 1

# ==============================
# ESTILOS CSS
# ==============================
st.markdown("""
<style>
.centered { text-align: center; }
.menu-button {
    font-size: 18px;
    width: 220px;
    height: 60px;
    border-radius: 12px;
    background-color: #0b6623;
    color: white;
    border: none;
}
.menu-button:hover {
    background-color: #16a34a;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# CARGA DE DATOS
# ==============================
df = cargar_datos()

# ==============================
# CONTROL DE PANTALLAS
# ==============================
if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"

# ==============================
# PANTALLA DE INICIO
# ==============================
if st.session_state.pagina == "Inicio":
    st.markdown("<div class='centered'>", unsafe_allow_html=True)
    if os.path.exists("logo_amsis.png"):
        st.image("logo_amsis.png", width=250)
    st.markdown("<h1 style='color:#0b6623;'>Asociación Mutual A.M.S.I.S.</h1>", unsafe_allow_html=True)
    st.markdown("### Sistema de Gestión de Socios")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("👥 Gestión de Socios"):
            st.session_state.pagina = "Socios"
            st.rerun()
    with col2:
        if st.button("📊 Reportes"):
            st.session_state.pagina = "Reportes"
            st.rerun()
    with col3:
        if st.button("⚙️ Configuración"):
            st.session_state.pagina = "Configuración"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# GESTIÓN DE SOCIOS
# ==============================
elif st.session_state.pagina == "Socios":
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        if os.path.exists("logo_amsis.png"):
            st.image("logo_amsis.png", width=100)
    with col_titulo:
        st.markdown("<h2 style='color:#0b6623;'>Gestión de Socios</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # FORMULARIO NUEVO SOCIO
    st.sidebar.header("➕ Nuevo Socio")
    with st.sidebar.form("nuevo_socio_form"):
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
        dni = st.text_input("DNI")
        telefono = st.text_input("Teléfono")
        email = st.text_input("Email")

        st.markdown("**Datos del Sub-socio**")
        sub_nombre = st.text_input("Nombre (Sub-socio)")
        sub_apellido = st.text_input("Apellido (Sub-socio)")
        sub_dni = st.text_input("DNI (Sub-socio)")
        sub_telefono = st.text_input("Teléfono (Sub-socio)")
        sub_email = st.text_input("Email (Sub-socio)")

        fecha_suscripcion = st.date_input("Fecha de suscripción", datetime.date.today())
        vencimiento = fecha_suscripcion + datetime.timedelta(days=30)

        submit = st.form_submit_button("Guardar Socio")

        if submit:
            if nombre and apellido and dni:
                nuevo = {
                    "ID": generar_id(df),
                    "Nombre": nombre, "Apellido": apellido, "DNI": dni,
                    "Teléfono": telefono, "Email": email,
                    "SubNombre": sub_nombre, "SubApellido": sub_apellido,
                    "SubDNI": sub_dni, "SubTeléfono": sub_telefono, "SubEmail": sub_email,
                    "Fecha Suscripción": fecha_suscripcion,
                    "Vencimiento": vencimiento,
                    "Estado": "Activo"
                }
                df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
                guardar_datos(df)
                st.success("✅ Socio agregado correctamente.")
            else:
                st.warning("⚠️ Debes completar al menos nombre, apellido y DNI.")

    # Actualizar estado de vencimientos
    hoy = datetime.date.today()
    for i, row in df.iterrows():
        try:
            venc = pd.to_datetime(row["Vencimiento"]).date()
            if venc < hoy:
                df.at[i, "Estado"] = "Vencido"
            elif (venc - hoy).days <= 5:
                df.at[i, "Estado"] = "Por vencer"
            else:
                df.at[i, "Estado"] = "Activo"
        except:
            continue
    guardar_datos(df)

    # FILTROS Y BUSQUEDA
    col1, col2 = st.columns(2)
    with col1:
        filtro_estado = st.selectbox("Filtrar por estado", ["Todos", "Activo", "Por vencer", "Vencido"])
    with col2:
        busqueda = st.text_input("Buscar por nombre o DNI")

    df_filtrado = df.copy()
    if filtro_estado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Estado"] == filtro_estado]
    if busqueda:
        df_filtrado = df_filtrado[df_filtrado.apply(lambda x: busqueda.lower() in str(x).lower(), axis=1)]

    # Colores de estado
    def color_estado(val):
        if val == "Activo":
            return "background-color: #b6f2b6;"
        elif val == "Por vencer":
            return "background-color: #fff5b1;"
        elif val == "Vencido":
            return "background-color: #f8b6b6;"
        return ""

    st.dataframe(df_filtrado.style.applymap(color_estado, subset=["Estado"]))

    st.markdown("---")

    # ACCIONES
    col1, col2 = st.columns(2)
    with col1:
        renovar_id = st.number_input("ID de socio a renovar", min_value=1, step=1)
        if st.button("🔄 Renovar suscripción"):
            if renovar_id in df["ID"].values:
                df.loc[df["ID"] == renovar_id, "Vencimiento"] = (datetime.date.today() + datetime.timedelta(days=30))
                df.loc[df["ID"] == renovar_id, "Estado"] = "Activo"
                guardar_datos(df)
                st.success("✅ Suscripción renovada correctamente.")
            else:
                st.error("❌ ID no encontrado.")

    with col2:
        baja_id = st.number_input("ID de socio a dar de baja", min_value=1, step=1, key="baja")
        if st.button("🗑️ Dar de baja"):
            if baja_id in df["ID"].values:
                df = df[df["ID"] != baja_id]
                guardar_datos(df)
                st.warning("🗑️ Socio dado de baja.")
            else:
                st.error("❌ ID no encontrado.")

    st.markdown("---")
    if st.button("⬅️ Volver al inicio"):
        st.session_state.pagina = "Inicio"
        st.rerun()

# ==============================
# REPORTES
# ==============================
elif st.session_state.pagina == "Reportes":
    st.markdown("<h2 style='color:#0b6623;'>📊 Reportes y Estadísticas</h2>", unsafe_allow_html=True)
    st.markdown("---")

    if df.empty:
        st.info("No hay datos cargados aún.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            estado_count = df["Estado"].value_counts()
            fig, ax = plt.subplots()
            ax.pie(estado_count, labels=estado_count.index, autopct="%1.1f%%", startangle=90)
            ax.set_title("Distribución de estados de socios")
            st.pyplot(fig)

        with col2:
            df["Fecha Suscripción"] = pd.to_datetime(df["Fecha Suscripción"], errors="coerce")
            df["Mes"] = df["Fecha Suscripción"].dt.to_period("M")
            socios_por_mes = df.groupby("Mes").size()
            fig2, ax2 = plt.subplots()
            socios_por_mes.plot(kind="bar", ax=ax2)
            ax2.set_title("Altas de socios por mes")
            ax2.set_xlabel("Mes")
            ax2.set_ylabel("Cantidad")
            st.pyplot(fig2)

    st.markdown("---")
    if st.button("⬅️ Volver al inicio"):
        st.session_state.pagina = "Inicio"
        st.rerun()

# ==============================
# CONFIGURACIÓN
# ==============================
elif st.session_state.pagina == "Configuración":
    st.markdown("<h2 style='color:#0b6623;'>⚙️ Configuración del Sistema</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.info("Aquí podrás agregar opciones de configuración en el futuro, como cambiar logo, colores o exportar datos.")
    if st.button("⬅️ Volver al inicio"):
        st.session_state.pagina = "Inicio"
        st.rerun()

