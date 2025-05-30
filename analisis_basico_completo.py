import streamlit as st
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime

def mostrar_analisis_basico(hist, rendimiento, std_anual, model):
    st.header("🔍 Análisis Básico de la Acción")

    st.markdown("ℹ️ Esta sección muestra una visión clara y visual del comportamiento de la acción. Cada gráfico incluye su interpretación para facilitar la comprensión, incluso si no tienes experiencia financiera.")

    # 📈 Evolución del Precio con Medias Móviles
    st.subheader("📈 Evolución del Precio con Medias Móviles")
    hist["MA20"] = hist["Close"].rolling(window=20).mean()
    hist["MA50"] = hist["Close"].rolling(window=50).mean()
    fig_ma = px.line(hist, x="Date", y=["Close", "MA20", "MA50"],
                     labels={"value": "Precio", "variable": "Serie"},
                     title="Precio de Cierre vs Medias Móviles 20 y 50 días")
    fig_ma.update_layout(legend_title_text='Líneas')
    st.plotly_chart(fig_ma, use_container_width=True)
    st.markdown("""
    💡 **Interpretación**:
    - `Close`: Precio de cierre del día, es decir, el valor al que se vendió la última acción.
    - `MA20` y `MA50`: Promedios móviles de los últimos 20 y 50 días. Ayudan a ver tendencias y suavizar fluctuaciones diarias.
    - Si el precio cruza la media móvil hacia arriba, puede indicar una tendencia alcista, y viceversa.
    """)

    # 📉 Volumen operado
    st.subheader("📉 Volumen operado")
    st.bar_chart(hist.set_index("Date")["Volume"])
    st.markdown("""
    🔍 **Interpretación**:
    - `Volume`: Cantidad de acciones negociadas en el día. Un volumen alto indica mayor interés de los inversionistas.
    - Puede anticipar movimientos fuertes en el precio.
    """)

    # 📈 Rentabilidad histórica
    st.subheader("📈 Rentabilidad histórica")
    st.line_chart(hist.set_index("Date")["Close"])
    st.markdown("""
    📈 **Interpretación**:
    - Muestra la evolución del precio con el tiempo.
    - Si la línea sube, la acción ha ganado valor. Si baja, ha perdido.
    - Permite ver la tendencia general del mercado respecto a esa acción.
    """)

    # 📊 Comparación apertura vs cierre
    st.subheader("📊 Comparación apertura vs cierre")
    st.area_chart(hist.set_index("Date")[["Open", "Close"]])
    st.markdown("""
    📌 **Interpretación**:
    - `Open`: Precio de inicio del día. `Close`: Precio al cierre.
    - Si `Close` > `Open`, fue un día positivo para la acción.
    - Este gráfico muestra visualmente el desempeño intradía.
    """)

    # 🔧 RSI y MACD
    st.subheader("🔧 Indicadores técnicos: RSI y MACD")
    try:
        st.line_chart(hist.set_index("Date")["RSI"])
        st.line_chart(hist.set_index("Date")[["MACD", "Signal"]])
        st.markdown("""
        🔎 **Interpretación**:
        - `RSI`: Índice de Fuerza Relativa. Sobrecompra (>70) o sobreventa (<30).
        - `MACD`: Cruces del MACD con la línea de señal indican cambios de tendencia.
        - Ayudan a identificar momentos para entrar o salir del mercado.
        """)
    except Exception as e:
        st.warning(f"⚠️ Error mostrando RSI o MACD: {e}")

    # 🟠 Dispersión Precio vs Volumen
    st.subheader("🟠 Precio vs Volumen")
    scatter = alt.Chart(hist).mark_circle(opacity=0.6, size=70).encode(
        x="Volume", y="Close", tooltip=["Date", "Close", "Volume"]
    )
    st.altair_chart(scatter, use_container_width=True)
    st.markdown("""
    📉 **Interpretación**:
    - Este gráfico muestra cómo se relaciona el precio con el volumen.
    - Sirve para detectar si un aumento en volumen corresponde a una variación fuerte en el precio.
    """)

    # 📈 Rendimiento porcentual acumulado
    st.subheader("📈 Rendimiento porcentual acumulado")
    hist["Acumulado"] = (hist["Close"] / hist["Close"].iloc[0]) * 100
    st.line_chart(hist.set_index("Date")["Acumulado"])
    st.markdown("""
    📈 **Interpretación**:
    - Indica cuánto ha crecido (o decrecido) la inversión desde el inicio.
    - Muy útil para evaluar el desempeño general de la acción.
    """)

    # 🔄 Volatilidad móvil de 30 días
    st.subheader("📉 Volatilidad móvil (30 días)")
    hist["Volatilidad 30d"] = hist["Close"].pct_change().rolling(window=30).std() * (252 ** 0.5)
    st.line_chart(hist.set_index("Date")["Volatilidad 30d"])
    st.markdown("""
    ⚠️ **Interpretación**:
    - Mide qué tanto varía el precio de la acción.
    - Alta volatilidad implica más riesgo, pero también más oportunidad de ganancia (o pérdida).
    """)

    # 💸 Burbuja Capitalización vs Volumen
    st.subheader("💸 Capitalización vs Volumen")
    hist["Cap"] = hist["Close"] * hist["Volume"]
    fig_bubble = px.scatter(hist, x="Volume", y="Close", size="Cap", color="Cap",
                            hover_name="Date", size_max=40)
    st.plotly_chart(fig_bubble, use_container_width=True)
    st.markdown("""
    🟣 **Interpretación**:
    - Cada punto es un día, y el tamaño refleja la capitalización (precio * volumen).
    - Días con burbujas grandes indican movimientos de mucho dinero.
    """)

    # 🕯️ Gráfico de velas japonesas
    st.subheader("🕯️ Velas japonesas")
    fig = go.Figure(data=[
        go.Candlestick(x=hist["Date"],
                       open=hist["Open"],
                       high=hist["High"],
                       low=hist["Low"],
                       close=hist["Close"],
                       increasing_line_color='green',
                       decreasing_line_color='red')
    ])
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color="#3e1f14"),
        hoverlabel=dict(bgcolor="#fff1dc", font_size=14, font_family="Arial")
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
    🕯️ **Interpretación**:
    - Cada vela resume un día: apertura, cierre, máximo y mínimo.
    - Verde = subió. Roja = bajó. Las sombras muestran los extremos del precio.
    """)

    # 📊 Mapa de correlaciones
    st.subheader("📊 Mapa de correlación")
    corr = hist[["Open", "High", "Low", "Close", "Volume"]].corr()
    fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r")
    st.plotly_chart(fig_corr, use_container_width=True)
    st.markdown("""
    🔍 **Interpretación**:
    - La correlación mide la relación entre variables.
    - Una correlación de 1 significa que se mueven igual, -1 que se mueven al revés.
    - Este gráfico permite ver si hay dependencias fuertes entre precios y volumen.
    """)

    # 📉 Histograma de retornos diarios
    st.subheader("📉 Histograma de rendimientos")
    hist["Daily Return"] = hist["Close"].pct_change()
    fig_hist = px.histogram(hist.dropna(), x="Daily Return", nbins=50)
    st.plotly_chart(fig_hist, use_container_width=True)
    st.markdown("""
    📊 **Interpretación**:
    - Muestra la frecuencia de los cambios diarios en el precio.
    - Sirve para ver si hay estabilidad o movimientos extremos.
    - Una campana centrada indica comportamiento estable.
    """)

    # 📌 Resumen general final
    st.markdown("---")
    st.subheader("📌 Resumen del comportamiento de la acción")
    st.markdown(f"""
    - El rendimiento acumulado fue del **{round(rendimiento, 2)}%**, lo que indica una evolución {'positiva' if rendimiento > 0 else 'negativa'} del precio durante el periodo analizado.
    - La **volatilidad anualizada** fue de **{round(std_anual * 100, 2)}%**, lo cual sugiere un nivel {'alto' if std_anual > 0.3 else 'moderado' if std_anual > 0.15 else 'bajo'} de riesgo.
    """)
