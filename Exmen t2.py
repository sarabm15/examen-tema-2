import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import random

st.title("Sistema de Gestión de Inventario - TechZone S.R.L.")

# Pregunta 1 - cargar el archivo
try:
    df = pd.read_excel("InventarioTechZone.xlsx")
except FileNotFoundError:
    st.error("No se encontró el archivo InventarioTechZone.xlsx, revisa que esté en la carpeta.")
    st.stop()
except Exception as e:
    st.error("Ocurrió un problema al cargar el archivo: " + str(e))
    st.stop()


# Pregunta 2 - convertir fecha y mostrar tabla
df["FechaIngreso"] = pd.to_datetime(df["FechaIngreso"])

st.header("Inventario completo")
st.dataframe(df)


# Pregunta 3 a 7 - filtros
st.header("Filtros")

categorias = df["Categoria"].unique()
categorias_elegidas = st.multiselect("Categoría del producto", categorias, default=list(categorias))

estados = ["Disponible", "Agotado", "Descontinuado", "Crítico"]
estados_elegidos = st.multiselect("Estado del producto", estados, default=estados)

precio_min = int(df["Precio"].min())
precio_max = int(df["Precio"].max())
rango_precio = st.slider("Rango de precios", precio_min, precio_max, (precio_min, precio_max))

busqueda = st.text_input("Buscar por nombre o palabra clave")

usar_stock_min = st.checkbox("Filtrar por stock mínimo")
if usar_stock_min:
    stock_min = st.number_input("Stock mínimo", min_value=0, value=5)

# aplicamos los filtros
df_filtrado = df[df["Categoria"].isin(categorias_elegidas)]
df_filtrado = df_filtrado[df_filtrado["Estado"].isin(estados_elegidos)]
df_filtrado = df_filtrado[(df_filtrado["Precio"] >= rango_precio[0]) & (df_filtrado["Precio"] <= rango_precio[1])]

if busqueda:
    df_filtrado = df_filtrado[df_filtrado["Producto"].str.contains(busqueda, case=False, na=False)]

if usar_stock_min:
    df_filtrado = df_filtrado[df_filtrado["Stock"] >= stock_min]

st.subheader("Resultado del filtro")
st.dataframe(df_filtrado)


# funcion para generar el codigo unico (se reutiliza en la pregunta 8)
def generar_codigo():
    ahora = datetime.datetime.now().strftime("%y%m%d-%H%M%S")
    numero = random.randint(0, 999)
    return "PR-" + ahora + "-" + str(numero)


# Pregunta 8 - formulario de registro
st.header("Registrar nuevo producto")

with st.form("form_producto"):
    nombre_producto = st.text_input("Nombre del producto")
    categoria_producto = st.selectbox("Categoría", ["Laptop", "Monitor", "Accesorio", "Periférico", "Componente"])
    precio_producto = st.number_input("Precio unitario", min_value=0.0, step=1.0)
    stock_producto = st.number_input("Stock disponible", min_value=0, step=1)
    fecha_producto = st.date_input("Fecha de ingreso", value=datetime.date.today())
    descontinuado_manual = st.checkbox("Marcar como descontinuado")

    enviar = st.form_submit_button("Guardar producto")

    if enviar:
        errores = []
        if nombre_producto.strip() == "":
            errores.append("El nombre no puede estar vacío.")
        if precio_producto <= 0:
            errores.append("El precio debe ser mayor que 0.")
        if stock_producto < 0:
            errores.append("El stock no puede ser negativo.")
        if fecha_producto > datetime.date.today():
            errores.append("La fecha no puede ser futura.")

        if errores:
            for e in errores:
                st.error(e)
        else:
            # Pregunta 9 - estado automatico segun el stock
            if descontinuado_manual:
                estado_nuevo = "Descontinuado"
            elif stock_producto == 0:
                estado_nuevo = "Agotado"
            elif stock_producto < 5:
                estado_nuevo = "Crítico"
            else:
                estado_nuevo = "Disponible"

            nuevo_codigo = generar_codigo()

            nuevo_producto = {
                "Codigo": nuevo_codigo,
                "Producto": nombre_producto,
                "Categoria": categoria_producto,
                "Precio": precio_producto,
                "Stock": stock_producto,
                "FechaIngreso": pd.to_datetime(fecha_producto),
                "Estado": estado_nuevo
            }

            df.loc[len(df)] = nuevo_producto
            st.success("Producto guardado con código " + nuevo_codigo + " - Estado: " + estado_nuevo)


# Pregunta 10 - metricas avanzadas
st.header("Métricas del inventario")

df["ValorTotal"] = df["Precio"] * df["Stock"]
df["MargenGanancia"] = df["Precio"] * 0.12
df["DiasEnInventario"] = (pd.Timestamp.today() - df["FechaIngreso"]).dt.days

st.dataframe(df)


# Pregunta 11 - graficos
st.header("Gráficos")

productos_por_categoria = df.groupby("Categoria")["Producto"].count()
valor_por_categoria = df.groupby("Categoria")["ValorTotal"].sum()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.bar(productos_por_categoria.index, productos_por_categoria.values)
ax1.set_title("Cantidad de productos por categoría")
ax1.set_xlabel("Categoría")
ax1.set_ylabel("Cantidad")
ax1.tick_params(axis="x", rotation=45)

ax2.pie(valor_por_categoria, labels=valor_por_categoria.index, autopct="%1.1f%%")
ax2.set_title("Valor total por categoría")

st.pyplot(fig)

st.subheader("Top 5 productos más valiosos")
top5 = df.sort_values("ValorTotal", ascending=False).head(5)

fig2, ax3 = plt.subplots()
ax3.barh(top5["Producto"], top5["ValorTotal"])
ax3.set_xlabel("Valor total")
ax3.set_title("Top 5 productos con mayor valor")
st.pyplot(fig2)