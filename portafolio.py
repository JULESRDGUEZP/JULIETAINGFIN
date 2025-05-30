import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pandas.tseries.offsets import DateOffset
import plotly.express as px
import base64


def mostrar_portafolio():
    st.title("💼 Portafolio de Inversión")
    st.markdown("Este módulo te permite analizar un portafolio de activos y evaluar su rendimiento y riesgo histórico.")

    tickers = st.text_input("📥 Ingresa los tickers separados por comas (ej. AAPL, MSFT, TSLA):", value="AAPL, MSFT, TSLA")
    tickers = [t.strip().upper() for t in tickers.split(",") if t.strip()]

    fecha_inicio = st.date_input("📅 Fecha de inicio del análisis:", value=datetime(2020, 1, 1))

    if not tickers:
        st.warning("Por favor, ingresa al menos un ticker válido.")
        return

    precios = pd.DataFrame()
    errores = []
    for ticker in tickers:
        data = yf.download(ticker, start=fecha_inicio)
        if not data.empty and "Close" in data.columns:
            precios[ticker] = data["Close"]
        else:
            errores.append(ticker)

    if errores:
        st.warning(f"No se pudo obtener información válida para: {', '.join(errores)}")

    if precios.empty:
        st.error("No se pudo obtener información para los tickers proporcionados.")
        return

    st.subheader("📊 Precios históricos de cierre")
    st.line_chart(precios)
    st.markdown("**Interpretación:** Aquí se muestran los precios de los activos seleccionados desde la fecha indicada. Esto permite ver la evolución individual de cada activo en tu portafolio.")

    rendimientos = precios.pct_change().dropna()

    st.subheader("📈 Rendimiento acumulado desde inicio")
    rendimiento_acumulado = (1 + rendimientos).cumprod()
    st.line_chart(rendimiento_acumulado)
    st.markdown("**Interpretación:** Este gráfico muestra el crecimiento hipotético de $1 invertido en cada activo. Permite comparar el desempeño acumulado relativo entre ellos.")

    st.subheader("📉 Matriz de correlación")
    fig_corr, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(rendimientos.corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig_corr)
    st.markdown("**Interpretación:** La correlación indica qué tan sincronizados están los movimientos de los activos. Idealmente, se busca baja correlación para diversificar.")

    st.subheader("📊 Riesgo y retorno")
    media_rend = rendimientos.mean() * 252
    volatilidad = rendimientos.std() * np.sqrt(252)
    resumen = pd.DataFrame({
        "Rendimiento Anual (%)": media_rend * 100,
        "Volatilidad Anual (%)": volatilidad * 100
    })
    st.dataframe(resumen.style.format("{:.2f}"))
    st.markdown("**Interpretación:** Esta tabla compara el rendimiento promedio anual y la volatilidad de cada activo. Ayuda a entender el equilibrio riesgo-retorno.")

    st.subheader("🎯 Frontera eficiente (simulación de portafolios aleatorios)")
    num_portafolios = 5000
    pesos_portafolio = []
    rend_esperados = []
    vols_esperadas = []

    for _ in range(num_portafolios):
        pesos = np.random.random(len(tickers))
        pesos /= np.sum(pesos)
        rendimiento = np.dot(pesos, media_rend)
        volatilidad_p = np.sqrt(np.dot(pesos.T, np.dot(rendimientos.cov() * 252, pesos)))
        pesos_portafolio.append(pesos)
        rend_esperados.append(rendimiento)
        vols_esperadas.append(volatilidad_p)

    df_portafolios = pd.DataFrame({
        "Rendimiento": rend_esperados,
        "Volatilidad": vols_esperadas
    })

    fig_frontera = px.scatter(df_portafolios, x="Volatilidad", y="Rendimiento",
                              labels={"Volatilidad": "Riesgo (Volatilidad)", "Rendimiento": "Retorno Esperado"},
                              title="Frontera Eficiente", opacity=0.5)
    st.plotly_chart(fig_frontera)
    st.markdown("**Interpretación:** Cada punto representa una combinación distinta de pesos. Buscar el punto más alto y a la izquierda indica el mejor retorno con menor riesgo.")

    st.subheader("📥 Descargar datos")
    precios_reset = precios.reset_index()
    csv = precios_reset.to_csv(index=False).encode('utf-8')
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="precios_portafolio.csv">Descargar precios históricos en CSV</a>'
    st.markdown(href, unsafe_allow_html=True)

    st.markdown("**Resumen:** Este análisis permite entender cómo han evolucionado tus activos, qué tan correlacionados están, cómo se comportan en términos de riesgo-retorno y qué combinaciones serían óptimas para maximizar tu inversión según el modelo de frontera eficiente.")
