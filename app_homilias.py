import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import date
import os

# Força o sistema a não usar conexões experimentais que causam erro 404
os.environ["GOOGLE_API_USE_MTLS"] = "never"

# ==========================================
# CONFIGURAÇÕES DE API (SEGURANÇA)
# ==========================================
if "MINHA_CHAVE" in st.secrets:
    API_KEY = st.secrets["MINHA_CHAVE"]
else:
    # COLE SUA CHAVE AQUI PARA TESTAR NO PC:
    API_KEY = "COLOQUE_SUA_CHAVE_AQUI"

genai.configure(api_key=API_KEY)

# ==========================================
# FUNÇÕES DE EXTRAÇÃO
# ==========================================

def extrair_texto_nellaparola():
    """Busca a liturgia exata de hoje no site italiano"""
    hoje = date.today()
    data_formatada = hoje.strftime("%Y-%m-%d")
    url = f"https://www.nellaparola.it/ldg/{data_formatada}"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            return f"Erro: Liturgia de hoje ({data_formatada}) ainda não disponível."
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        paragrafos = soup.find_all('p') 
        texto = "\n".join([p.get_text(strip=True) for p in paragrafos if len(p.get_text(strip=True)) > 20])
        return f"DATA: {data_formatada}\n\n" + texto[:3500]
    except Exception as e:
        return f"Erro na extração: {e}"

def gerar_homilia(texto_base):
    """Gera homilia com sistema de tentativa e erro para o modelo"""
    if "Erro" in texto_base or not texto_base:
        return texto_base

    # Tenta esses nomes em ordem até um funcionar
    modelos_para_testar = ["gemini-1.5-flash", "models/gemini-1.5-flash", "gemini-pro"]
    
    ultima_excecao = ""
    
    for nome_modelo in modelos_para_testar:
        try:
            model = genai.GenerativeModel(nome_modelo)
            
            prompt = f"""
            Você é um sacerdote católico experiente e zeloso. 
            Baseado nestes estudos teológicos: {texto_base}
            
            Escreva uma homilia original em português seguindo este MOLDE:
            1. INTRODUÇÃO: Saudação e tema central.
            2. DESENVOLVIMENTO: Reflexão profunda para a vida atual, sem citar fontes.
            3. CONCLUSÃO: Convite à ação e prece breve.
            
            Regra: Não mencione sites ou autores. Use tom pastoral e gramática impecável.
            """
            
            resposta = model.generate_content(prompt)
            return resposta.text # Se chegou aqui, funcionou!
            
        except Exception as e:
            ultima_excecao = str(e)
            continue # Tenta o próximo modelo da lista
            
    return f"Não foi possível conectar aos modelos do Gemini. Erro: {ultima_excecao}"

# ==========================================
# INTERFACE STREAMLIT
# ==========================================
st.set_page_config(page_title="Homilia Diária", page_icon="🕊️")

st.title("🕊️ Homilia Diária")
st.write("Reflexão original baseada na liturgia do dia.")

if st.button("Gerar Homilia de Hoje", type="primary"):
    with st.spinner("Meditando sobre as leituras..."):
        conteudo = extrair_texto_nellaparola()
        resultado = gerar_homilia(conte
