import streamlit as st
import requests
from bs4 import BeautifulSoup

st.write("Hola querido Mundo")

# URL base con el ticker deseado
ticker = "NVDA"

url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"

# Cabeceras para evitar bloqueo por parte del servidor
headers = {
    "User-Agent": "Mozilla/5.0"
}

# Hacer la solicitud a la página
response = requests.get(url, headers=headers)
response.raise_for_status()  # Verifica que la solicitud fue exitosa

# Parsear el contenido HTML
soup = BeautifulSoup(response.text, "html.parser")

# Buscar el enlace que contiene los peers
peer_link = soup.find("a", text="Peers")

# Extraer los símbolos desde el atributo href
if peer_link and "href" in peer_link.attrs:
    href_value = peer_link["href"]
    # href_value = "screener.ashx?t=NVDA,INTC,QCOM,TXN,MRVL,MU,ADI,..."
    if "t=" in href_value:
        peer_symbols = href_value.split("t=")[1].split(",")
        st.write("Peers encontrados:", peer_symbols)
    else:
        st.write("No se encontraron símbolos de peers.")
else:
    st.write("No se encontró el enlace de peers.")

    #Buscar el enlace con texto "Held by"
held_by_link = soup. find("a", text="Held by")

# Extraer los símbolos del atributo href 
if held_by_link and "href" in held_by_link.attrs:
    href_value = held_by_link["href"]
    # href_value = "screener. ashx?t=VTI, VOO, 000, SPY, IVV,VUG, XLK, VGT, SMH, SOXX**
    if "t=" in href_value:
        held_by_symbols = href_value.split("t=")[1].split(",")
        st.write("ETFs que poseen la acción:", held_by_symbols)
    else:
        st.write("No se encontraron ETFs.")
else:
    st.write("No se encontró el enlace 'Held by'.")