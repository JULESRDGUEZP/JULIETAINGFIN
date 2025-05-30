import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px


def obtener_datos(tickers, start):
    precios = []
    for nombre, ticker in tickers.items():
        data = yf.download(ticker, start=start)
        if not data.empty and "Close" in data.columns:
            serie = data["Close"].squeeze()
            precios.append(pd.Series(serie.values, index=serie.index, name=nombre))

    if precios:
        return pd.concat(precios, axis=1)
    else:
        return pd.DataFrame()


def mostrar_panorama():
    st.title("🌍 Panorama del Mercado")
    st.markdown("Explora el estado actual del mercado global: índices bursátiles, commodities, divisas y un resumen interpretativo del entorno financiero actual.")

    fecha_inicio = datetime.today() - timedelta(days=365)

    indices = {
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "Dow Jones": "^DJI"
    }

    commodities = {
        "Oro": "GC=F",
        "Petróleo": "CL=F",
        "Gas Natural": "NG=F"
    }

    divisas = {
        "EUR/USD": "EURUSD=X",
        "JPY/USD": "JPY=X",
        "MXN/USD": "MXN=X"
    }

    def calcular_tabla(tickers: dict, nombre_col: str):
        df = obtener_datos(tickers, fecha_inicio)
        if df.empty:
            return pd.DataFrame(columns=[nombre_col, "Variación %"]), df
        variacion = ((df.iloc[-1] / df.iloc[0]) - 1) * 100
        tabla = pd.DataFrame({nombre_col: variacion.index, "Variación %": variacion.values}).sort_values("Variación %", ascending=False)
        return tabla, variacion

    with st.expander("📊 Tabla Comparativa de Índices", expanded=True):
        tabla_indices, variacion_indices = calcular_tabla(indices, "Índice")
        st.dataframe(tabla_indices.style.format({"Variación %": "{:.2f}"}))
        if not variacion_indices.empty:
            fig = px.bar(tabla_indices, x="Índice", y="Variación %", color="Índice", title="Variación Anual de Índices")
            st.plotly_chart(fig, use_container_width=True)

    with st.expander("🛢️ Tabla Comparativa de Commodities"):
        tabla_commodities, variacion_commodities = calcular_tabla(commodities, "Commodity")
        st.dataframe(tabla_commodities.style.format({"Variación %": "{:.2f}"}))
        if not variacion_commodities.empty:
            fig = px.bar(tabla_commodities, x="Commodity", y="Variación %", color="Commodity", title="Variación Anual de Commodities")
            st.plotly_chart(fig, use_container_width=True)

    with st.expander("💱 Tabla Comparativa de Divisas"):
        tabla_divisas, variacion_divisas = calcular_tabla(divisas, "Divisa")
        st.dataframe(tabla_divisas.style.format({"Variación %": "{:.2f}"}))
        if not variacion_divisas.empty:
            fig = px.bar(tabla_divisas, x="Divisa", y="Variación %", color="Divisa", title="Variación Anual de Divisas")
            st.plotly_chart(fig, use_container_width=True)

    with st.expander("🏆 Ranking de Ganadores y Perdedores"):
        all_assets = {**indices, **commodities, **divisas}
        df_all = obtener_datos(all_assets, fecha_inicio)
        if not df_all.empty:
            variacion = ((df_all.iloc[-1] / df_all.iloc[0]) - 1) * 100
            ganadores = variacion.sort_values(ascending=False).head(3)
            perdedores = variacion.sort_values().head(3)
            st.markdown("🔼 Top 3 Ganadores")
            st.dataframe(ganadores.rename("Variación %").to_frame().style.format("{:.2f}"))
            st.markdown("🔽 Top 3 Perdedores")
            st.dataframe(perdedores.rename("Variación %").to_frame().style.format("{:.2f}"))
        else:
            st.warning("No se pudieron obtener datos para el ranking.")

    with st.expander("🧠 Interpretación del Entorno Financiero"):
        st.markdown("""
        - **Índices bursátiles:** Muestran la dirección general del mercado.
        - **Commodities:** Representan la evolución de recursos esenciales.
        - **Divisas:** Revelan la fortaleza relativa entre economías.
        - **Ranking:** Identifica qué activos están sobresaliendo o quedándose atrás.
        """)
