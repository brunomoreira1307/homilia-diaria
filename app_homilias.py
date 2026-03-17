import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import date
import os

# Força o uso da conexão estável
os.environ["GOOGLE_API_USE_MTLS"] = "never"

# ==========================================
# CONFIGURAÇÕES DE API
# ==========================================
if "MINHA_CHAVE" in st.secrets:
    API_KEY = st.secrets["AIzaSyBWqyLvz1XdmOU1opKDzshbactH_-DBgew"]
else:
    API_KEY = "AIzaSyBWqyLvz1XdmOU1opKDzshbactH_-DBgew"

genai.configure(api_key=API_KEY)

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

    # Nomes estáveis para a versão v1 da API
    modelos_para_testar = ["gemini-1.5-flash", "gemini-1.5-pro"]
    
    erro_final = ""
    for nome in modelos_para_testar:
        try:
            model = genai.GenerativeModel(nome)
            prompt = f"""
            Você é um sacerdote católico zeloso. 
            Estude estes comentários teológicos: {texto_base}
            
            Escreva uma homilia original em português seguindo este molde:
            - INTRODUÇÃO: Saudação e tema central.
            - DESENVOLVIMENTO: Reflexão profunda para hoje, sem citar fontes.
            - CONCLUSÃO: Convite à ação e prece breve.
            
            Use tom pastoral e gramática correta. Jamais mencione o site de origem.
            """
            resposta = model.generate_content(prompt)
            return resposta.text
        except Exception as e:
            erro_final = str(e)
            continue
            
    return f"Erro de conexão com a IA: {erro_final}"

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
st.caption("Site: nellaparola.it | IA: Google Gemini")
