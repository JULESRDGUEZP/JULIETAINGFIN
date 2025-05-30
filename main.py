import streamlit as st
st.set_page_config(page_title="📊 Explorador Financiero", layout="wide")

from streamlit_option_menu import option_menu
import yfinance as yf
import pandas as pd
import numpy as np
import os
from datetime import datetime
from pandas.tseries.offsets import DateOffset
import google.generativeai as genai

from analisis_basico_completo import mostrar_analisis_basico
from portafolio import mostrar_portafolio
from mercado import mostrar_panorama
from estilo import aplicar_estilo

# Configurar API Key de Gemini
token = os.getenv("TOKEN_GENAI")
if token:
    genai.configure(api_key=token)
    model = genai.GenerativeModel("models/gemini-1.5-pro")
else:
    model = None

# Aplicar estilo visual personalizado
aplicar_estilo()

# Menú lateral de navegación
with st.sidebar:
    seleccion = option_menu("💻 Menú Principal", 
                            options=["🔍 Análisis de Empresa", "💼 Portafolio", "🌍 Panorama del Mercado"],
                            icons=["search", "briefcase", "globe2"],
                            menu_icon="laptop", default_index=0)

# Lógica de navegación
if seleccion == "🔍 Análisis de Empresa":
    st.title("🔍 Análisis de Empresa")
    ticker = st.text_input("Escribe el ticker de la empresa:", value="AAPL").upper()

    if ticker:
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period="5y").reset_index()

            if hist.empty:
                st.error("No se encontraron datos históricos para este ticker.")
            else:
                delta = hist["Close"].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                hist["RSI"] = 100 - (100 / (1 + rs))

                exp1 = hist["Close"].ewm(span=12, adjust=False).mean()
                exp2 = hist["Close"].ewm(span=26, adjust=False).mean()
                hist["MACD"] = exp1 - exp2
                hist["Signal"] = hist["MACD"].ewm(span=9, adjust=False).mean()

                hoy = hist["Date"].max()
                rendimiento_data = []

                def calcular_cagr(p0, pf, a):
                    if p0 > 0 and a > 0:
                        return (pf / p0) ** (1 / a) - 1
                    return None

                for a in [1, 3, 5]:
                    inicio = hoy - DateOffset(years=a)
                    df = hist[hist["Date"] >= inicio]
                    if not df.empty:
                        p0, pf = df.iloc[0]["Close"], df.iloc[-1]["Close"]
                        cagr = calcular_cagr(p0, pf, a)
                        rendimiento_data.append((a, cagr * 100 if cagr else None))

                rendimiento_df = pd.DataFrame(rendimiento_data, columns=["Periodo", "CAGR"])
                rendimiento_promedio = rendimiento_df["CAGR"].dropna().mean()

                std_anual = np.std(hist["Close"].pct_change()) * np.sqrt(252)

                mostrar_analisis_basico(hist, rendimiento_promedio, std_anual, model)

        except Exception as e:
            st.error(f"❌ Error al obtener datos: {e}")

elif seleccion == "💼 Portafolio":
    mostrar_portafolio()

elif seleccion == "🌍 Panorama del Mercado":
    mostrar_panorama()
