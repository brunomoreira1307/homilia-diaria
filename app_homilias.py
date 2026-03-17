import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import date

# ==========================================
# CONFIGURAÇÕES DE API
# ==========================================
if "MINHA_CHAVE" in st.secrets:
    API_KEY = st.secrets["MINHA_CHAVE"]
else:
    API_KEY = "COLOQUE_SUA_CHAVE_AQUI"

# ==========================================
# FUNÇÕES
# ==========================================

def extrair_texto_nellaparola():
    hoje = date.today()
    data_formatada = hoje.strftime("%Y-%m-%d")
    url = f"https://www.nellaparola.it/ldg/{data_formatada}"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            return f"Liturgia de hoje ({data_formatada}) ainda não disponível no site."
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        paragrafos = soup.find_all('p') 
        texto = "\n".join([p.get_text(strip=True) for p in paragrafos if len(p.get_text(strip=True)) > 20])
        return f"DATA: {data_formatada}\n\n" + texto[:3500]
    except Exception as e:
        return f"Erro na extração: {e}"

def gerar_homilia(texto_base):
    if "Erro" in texto_base or not texto_base:
        return texto_base

    # Conexão DIRETA com o Google, sem usar a biblioteca problemática
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    prompt = f"""
    Você é um sacerdote católico zeloso. 
    Estude estes comentários teológicos: {texto_base}
    
    Escreva uma homilia original em português seguindo este molde:
    - INTRODUÇÃO: Saudação e tema central.
    - DESENVOLVIMENTO: Reflexão profunda para hoje, sem citar fontes.
    - CONCLUSÃO: Convite à ação e prece breve.
    
    Use tom pastoral e gramática correta. Jamais mencione o site de origem.
    """

    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # Verifica se deu algum erro de servidor
        dados = response.json()
        return dados['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        detalhes = response.text if 'response' in locals() else "Sem detalhes"
        return f"Erro na conexão direta com o Google: {e}\nDetalhes: {detalhes}"

# ==========================================
# INTERFACE
# ==========================================
st.set_page_config(page_title="Homilia Diária", page_icon="🕊️")

st.title("🕊️ Homilia Diária")
st.write("Reflexão original baseada na liturgia do dia.")

if st.button("Gerar Homilia de Hoje", type="primary"):
    with st.spinner("Meditando sobre as leituras..."):
        conteudo = extrair_texto_nellaparola()
        resultado = gerar_homilia(conteudo)
        st.subheader("Sua reflexão:")
        st.write(resultado)

st.divider()
st.caption("Site: nellaparola.it | IA: Google Gemini API Direta")
