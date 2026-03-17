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

def descobrir_modelo_liberado(chave):
    """Pergunta ao Google qual modelo está disponível para esta chave"""
    url_lista = f"https://generativelanguage.googleapis.com/v1beta/models?key={chave}"
    try:
        req = requests.get(url_lista)
        if req.status_code == 200:
            modelos = req.json().get('models', [])
            for m in modelos:
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    return m['name'] # Ele acha o nome certo sozinho!
    except:
        pass
    return "models/gemini-pro" # Fallback de segurança

def gerar_homilia(texto_base):
    if "Erro" in texto_base or not texto_base:
        return texto_base

    # A IA descobre o nome correto do modelo e cria o link
    nome_do_modelo = descobrir_modelo_liberado(API_KEY)
    url = f"https://generativelanguage.googleapis.com/v1beta/{nome_do_modelo}:generateContent?key={API_KEY}"
    
    prompt = f"""
    Você é um sacerdote católico zeloso. 
    Estude estes comentários teológicos: {texto_base}
    
    Escreva uma homilia original em português seguindo este molde, a partir dos comentário de Roberto Pasolini, Luigi Maria Epicoco e MichaelDavide Semeraro:
    - INTRODUÇÃO: Saudação e tema central, estritamente ligado ao tema do dia.
    - DESENVOLVIMENTO: Reflexão profundamente teológica e eloquente para hoje, sem citar fontes.
    - CONCLUSÃO: Convite à ação e prece breve.
    
    Use tom pastoral, poético, simples, profundo e gramática correta. Jamais mencione o site de origem. Utilize todos os comentários presentes no site para a liturgia do dia. Quando utilizar os pronomes Ele, Seu(a), referindo-se a Deus ou a Jesus Cristo, faça-o em letras minúsculas. Exceto quando o nome de Deus ou de Jesus Cristo não forem citados no texto ou não estejam evidentes. Tabmbém evite usat travessões, prefira ponto ou vírgula.
    """

    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() 
        dados = response.json()
        return dados['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        detalhes = response.text if 'response' in locals() else "Sem detalhes"
        return f"Erro na conexão. \nModelo tentado: {nome_do_modelo}\nDetalhes: {detalhes}"

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
st.caption("Site: nellaparola.it | IA: Google Gemini API Autônoma")
