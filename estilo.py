import streamlit as st

def aplicar_estilo():
    fondo_oscuro = "#0d0d0d"
    texto_claro = "#f5f5f5"
    acento = "#f3c1c6"
    rosa_suave = "#f7d6db"
    borde = "#a1887f"
    tipografia = "'DM Sans', sans-serif"

    estilo = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;700&display=swap');

    html, body, [class*="css"] {{
        background-color: {fondo_oscuro};
        color: {texto_claro};
        font-family: {tipografia};
        font-size: 16px;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: {acento};
        font-weight: 700;
    }}

    .stButton>button {{
        background-color: {acento};
        color: {fondo_oscuro};
        border: none;
        padding: 0.6em 1.2em;
        border-radius: 8px;
        font-weight: bold;
        transition: 0.3s;
    }}

    .stButton>button:hover {{
        background-color: {rosa_suave};
        color: {fondo_oscuro};
    }}

    .stTextInput>div>input, .stDateInput>div>input, .stSelectbox>div>div {{
        background-color: #1e1e1e;
        color: {texto_claro};
        border: 1px solid {borde};
        border-radius: 8px;
        padding: 0.5em;
    }}

    .stSidebar {{
        background-color: #1a1a1a;
    }}

    .stRadio>div>label, .stSelectbox>div>div>div {{
        color: {texto_claro};
    }}

    .stDataFrame, .stTable {{
        background-color: #1e1e1e;
        color: {texto_claro};
    }}

    .element-container:has([data-testid="stPlotlyChart"]),
    .element-container:has([data-testid="stAltairChart"]),
    .element-container:has([data-testid="stPyplotChart"]) {{
        margin-bottom: 40px;
    }}

    .stExpander {{
        background-color: #111111;
        border: 1px solid {borde};
        border-radius: 10px;
        padding: 0.6em;
    }}

    .stExpander > div {{
        color: {texto_claro};
        font-weight: 600;
    }}

    [data-testid="stMetricDelta"] {{
        color: {acento};
    }}

    ::placeholder {{
        color: {rosa_suave};
        opacity: 0.7;
    }}
    </style>
    """

    st.markdown(estilo, unsafe_allow_html=True)
