import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
import plotly.express as px
import google.generativeai as genai
from datetime import datetime
from pandas.tseries.offsets import DateOffset
import numpy as np
import requests
from bs4 import BeautifulSoup
import os

# --- Configuración de API Key ---
genai.configure(api_key=os.getenv("TOKEN_GENAI"))
model = genai.GenerativeModel("models/gemini-1.5-pro")

# --- Estilos y tema personalizado ---
st.set_page_config(page_title="🌸 Exploradora de Acciones", layout="wide")
theme_css = """
<style>
body, .main, .block-container {
   background-color: #fff5e6;
   color: #3e1f14;
}
h1, h2, h3, h4, h5, h6, p, li, span, div, label, table, th, td {
   color: #3e1f14 !important;
}
[data-testid="stSidebar"] {
   background-color: #fff1dc;
}
.stButton > button {
   background-color: #e88f9c;
   color: white;
   border: 2px solid #3e1f14;
   font-weight: bold;
   border-radius: 10px;
}
.stButton > button:hover {
   background-color: #f7d6db;
   color: #3e1f14;
}
</style>
"""
st.markdown(theme_css, unsafe_allow_html=True)

# --- Menú ---
menu = st.sidebar.radio("🌟 Menú", ["🔍 Análisis de empresa", "📰 Buscar noticias"])

# --- Análisis de empresa ---
if menu == "🔍 Análisis de empresa":
    st.title("💗 Exploradora de Acciones para Mujeres Inversionistas")
    st.markdown("Analiza empresas con estilo, claridad y seguridad 💖")

    ticker_input = st.text_input("🔍 Símbolo bursátil (Ej. AAPL, MSFT...):", placeholder="Ej. AAPL")
    periodo = st.selectbox("🕒 Periodo:", ["6mo", "1y", "5y", "max"], index=0)

    if st.button("✨ Analizar empresa"):
        if ticker_input:
            try:
                ticker = yf.Ticker(ticker_input.upper())
                info = ticker.info
                if not info or info.get("regularMarketPrice") is None:
                    st.warning("🚫 No encontramos ese símbolo. Revisa que esté bien escrito.")
                else:
                    nombre = info.get("longName", "Nombre no disponible")
                    descripcion = info.get("longBusinessSummary", "Descripción no disponible")
                    logo = info.get("logo_url", "")
                    st.markdown(f"## 💼 {nombre}")
                    if logo: st.image(logo, width=120)

                    prompt = f"""Traduce y adapta al español de forma cálida, simple y profesional para mujeres nuevas en finanzas:\n\n{descripcion}"""
                    try: respuesta = model.generate_content(prompt).text
                    except: respuesta = descripcion
                    st.markdown("### 🌷 ¿Qué hace esta empresa?")
                    st.write(respuesta)

                    st.subheader("📊 Datos clave")
                    claves = {
                        "📈 Precio actual": f"${info.get('regularMarketPrice', 'NA')}",
                        "🔄 Cambio diario": f"{info.get('regularMarketChangePercent', 0):.2f}%",
                        "🏢 Market Cap": info.get("marketCap", "NA"),
                        "📦 Volumen hoy": info.get("volume", "NA"),
                        "📚 P/E Ratio": info.get("trailingPE", "NA"),
                        "💵 EPS": info.get("trailingEps", "NA"),
                        "📉 Beta": info.get("beta", "NA"),
                    }
                    st.table(pd.DataFrame.from_dict(claves, orient="index", columns=["Valor estimado"]))

                    hist = ticker.history(period=periodo).reset_index()
                    hist["MA20"] = hist["Close"].rolling(window=20).mean()

                    st.subheader("📈 Precio y promedio móvil")
                    c1 = alt.Chart(hist).mark_line(color="#e88f9c").encode(x="Date:T", y="Close:Q")
                    c2 = alt.Chart(hist).mark_line(strokeDash=[4,4], color="#d4a373").encode(x="Date:T", y="MA20:Q")
                    st.altair_chart(c1 + c2, use_container_width=True)
                    st.markdown("💬 **Interpretación:** La línea rosita es el precio. La línea dorada es el promedio de 20 días. Si el precio va por encima del promedio, suele ser buena señal. ✨")

                    st.subheader("📆 CAGR - Rendimiento anual")
                    hoy = hist["Date"].max()
                    def calcular_cagr(p0, pf, años):
                        return (pf / p0) ** (1 / años) - 1 if p0 > 0 and años > 0 else None

                    cagr_data = []
                    for años in [1, 3, 5]:
                        fecha_inicio = hoy - DateOffset(years=años)
                        datos = hist[hist["Date"] >= fecha_inicio]
                        if not datos.empty:
                            cagr = calcular_cagr(datos.iloc[0]["Close"], datos.iloc[-1]["Close"], años)
                            cagr_data.append((f"{años} año(s)", f"{cagr*100:.2f}%" if cagr else "ND"))
                        else:
                            cagr_data.append((f"{años} año(s)", "ND"))
                    st.table(pd.DataFrame(cagr_data, columns=["Periodo", "CAGR"]))
                    st.markdown("💬 **Interpretación:** El CAGR te dice cuánto ha crecido en promedio la acción cada año. Ideal para ver si ha sido una buena inversión a largo plazo. 📈")

                    st.subheader("💫 Volatilidad")
                    rend = hist["Close"].pct_change()
                    std_anual = np.std(rend) * np.sqrt(252)
                    st.metric("Desviación estándar anualizada", f"{std_anual*100:.2f}%")
                    st.markdown("💬 **¿Qué significa?** Si es alta, el precio cambia mucho (más riesgoso). Si es baja, la acción es más estable.")

                    st.subheader("📉 Precio histórico")
                    fig = px.line(hist, x="Date", y="Close", title="Precio de cierre")
                    fig.update_traces(line=dict(color="#e88f9c"))
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")
        else:
            st.warning("🔔 Ingresa un símbolo válido para analizar.")

# --- Noticias ---
elif menu == "📰 Buscar noticias":
    st.title("📰 Buscador de Noticias Financieras")
    query = st.text_input("🔍 Tema o empresa:", placeholder="Ej. Apple, Tesla, inflación...")
    if st.button("Buscar Noticias"):
        if query.strip():
            try:
                url = f"https://news.google.com/search?q={query}+when:7d&hl=es-419&gl=MX&ceid=MX%3Aes-419"
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.content, "html.parser")
                noticias = soup.select("article")
                if noticias:
                    st.markdown("### 🗞️ Últimas noticias:")
                    for n in noticias[:5]:
                        titulo = n.text.strip()
                        enlace = n.find("a")
                        if enlace:
                            href = "https://news.google.com" + enlace["href"][1:]
                            st.markdown(f"- [{titulo}]({href})")
                else:
                    st.warning("No se encontraron noticias recientes.")
            except:
                st.error("Hubo un error al buscar noticias.")
        else:
            st.warning("Por favor ingresa un tema.")