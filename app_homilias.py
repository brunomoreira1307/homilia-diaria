import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import date

# ==========================================
# CONFIGURAÇÕES DE SEGURANÇA (Para Publicação)
# ==========================================
# Se estiver rodando no seu PC, ele tenta pegar a chave do código. 
# Se estiver no Streamlit Cloud, ele pega do "Secrets" (Cofre).
if "MINHA_CHAVE" in st.secrets:
    API_KEY = st.secrets["MINHA_CHAVE"]
else:
    # Se ainda estiver testando no PC, cole sua chave entre as aspas abaixo:
    API_KEY = "COLOQUE_SUA_CHAVE_AQUI"

genai.configure(api_key=API_KEY)

# ==========================================
# FUNÇÕES DO APLICATIVO
# ==========================================

def extrair_texto_nellaparola():
    """Busca o conteúdo do nellaparola.it com a liturgia exata de hoje"""
    hoje = date.today()
    data_formatada = hoje.strftime("%Y-%m-%d")
    url = f"https://www.nellaparola.it/ldg/{data_formatada}"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            return f"Erro: A liturgia de hoje ({data_formatada}) ainda não foi publicada."
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        paragrafos = soup.find_all('p') 
        texto_extraido = "\n".join([p.get_text(strip=True) for p in paragrafos if len(p.get_text(strip=True)) > 20])
        return f"Data: {data_formatada}\n\n" + texto_extraido[:3500]
    except Exception as e:
        return f"Erro ao acessar o site: {e}"

def gerar_homilia(texto_base):
    """Gera a homilia usando o modelo mais compatível com a API v1beta"""
    if "Erro" in texto_base or not texto_base:
        return texto_base

    # NOME DO MODELO ATUALIZADO PARA EVITAR ERRO 404
    # Este é o nome oficial para a versão v1beta que você está usando
    modelo_final = "gemini-1.5-flash-latest"

    try:
        model = genai.GenerativeModel(modelo_final)
        
        prompt = f"""
        Você é um sacerdote católico sábio e acolhedor.
        Estude o material teológico abaixo (em italiano):
        
        {texto_base}
        
        Sua tarefa:
        Escreva uma homilia em português do Brasil que seja original e profunda.
        
        REGRAS:
        1. NUNCA mencione o site 'nellaparola' ou que está traduzindo algo.
        2. Escreva como se fosse uma reflexão própria, saída do coração.
        3. Use um tom de conversa pastoral, com excelente gramática.

        ESTRUTURA:
        - Uma introdução calorosa apresentando o tema central.
        - Um desenvolvimento que conecte o Evangelho aos desafios de hoje.
        - Uma conclusão com um convite à oração ou ação prática.
        """
        
        resposta = model.generate_content(prompt)
        return resposta.text
    except Exception as e:
        return f"Erro ao gerar homilia: {e}"

# ==========================================
# INTERFACE
# ==========================================
st.set_page_config(page_title="Homilia Diária", page_icon="🕊️")

st.title("🕊️ Homilia Diária")
st.write("Reflexões baseadas nos comentários do *nellaparola.it*.")

if st.button("Gerar Homilia de Hoje", type="primary"):
    with st.spinner("Preparando a reflexão espiritual..."):
        conteudo = extrair_texto_nellaparola()
        resultado = gerar_homilia(conteudo)
        st.subheader("Sua reflexão para hoje:")
        st.write(resultado)

st.divider()
st.caption("Desenvolvido com IA e devoção.")
