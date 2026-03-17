import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import date

# ==========================================
# CONFIGURAÇÕES DA API
# ==========================================
# Insira sua API Key do Google AI Studio entre as aspas
API_KEY = "AIzaSyBWqyLvz1XdmOU1opKDzshbactH_-DBgew"
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
            return f"Erro: A liturgia de hoje ({data_formatada}) ainda não foi publicada no site."
            
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        paragrafos = soup.find_all('p') 
        texto_extraido = "\n".join([p.get_text(strip=True) for p in paragrafos if len(p.get_text(strip=True)) > 20])
        
        return f"Liturgia da data: {data_formatada}\n\n" + texto_extraido[:3500]
        
    except Exception as e:
        return f"Erro ao acessar o site: {e}"

def gerar_homilia(texto_base):
    """Usa o Gemini para ler os comentários e criar uma homilia original"""
    if "Erro ao acessar" in texto_base or "ainda não foi publicada" in texto_base or not texto_base:
        return texto_base

    # RADAR DE MODELOS: Busca automaticamente o modelo correto liberado
    modelo_escolhido = "gemini-1.5-pro"
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                modelo_escolhido = m.name 
                break
    except Exception:
        pass 

    model = genai.GenerativeModel(modelo_escolhido)
    
    prompt = f"""
    Você é um sacerdote católico sábio, acolhedor e com o dom da palavra, preparando sua homilia diária.
    
    Abaixo estão as leituras bíblicas e os comentários teológicos de apoio para o dia de hoje:
    
    [MATERIAL DE ESTUDO]
    {texto_base}
    [FIM DO MATERIAL DE ESTUDO]
    
    Sua tarefa:
    Escreva uma homilia diária em português do Brasil, inspirada na essência espiritual do material acima, mas seguindo ESTRITAMENTE as regras e o molde abaixo. O texto deve ter uma fluidez natural, ser profundamente teológico, poético, como uma conversa escrita.
    
    REGRAS INEGOCIÁVEIS:
    1. JAMAIS mencione a fonte das informações (site nellaparola.it, autores italianos, etc.).
    2. NÃO use frases como "o texto diz", "o comentário aponta" ou "como lemos". A homilia deve parecer uma reflexão 100% original e pessoal.
    3. Una as ideias do texto de apoio de forma fluida, reescrevendo-as com suas próprias palavras, com originalidade e profundidade teológica.
    4. Cuidado redobrado com a gramática (ex: se usar a segunda pessoa do singular, conjugue corretamente com o 's' no final, etc). Ao se referir a Deus com os pronomes Ele, Seu, etc. utilize-os em minúsculas caso o nome de Deus ou de Jesus Cristo já tenham sido citados.

    MOLDE DA HOMILIA (Siga esta estrutura rigorosamente):
    - Introdução: Uma saudação calorosa e a apresentação do tema central da liturgia de forma cativante.
    - Desenvolvimento: Uma reflexão profunda e natural, trazendo a mensagem para a vida cotidiana e os desafios espirituais da atualidade.
    - Conclusão: Um convite prático à contemplação ou ação para o dia de hoje, encerrando com uma breve prece.
    
    Escreva a homilia agora:
    """
    
    try:
        resposta = model.generate_content(prompt)
        return resposta.text
    except Exception as e:
        return f"Erro ao gerar a homilia com o modelo {modelo_escolhido}: {e}"

# ==========================================
# INTERFACE COM STREAMLIT
# ==========================================

st.set_page_config(page_title="Homilia Diária", page_icon="🕊️")

st.title("🕊️ Homilia Diária")
st.write("Reflexões diárias geradas de forma original a partir da liturgia do dia.")

st.divider()

if st.button("Gerar Homilia de Hoje", type="primary"):
    with st.spinner("Buscando as leituras e preparando a reflexão..."):
        texto_site = extrair_texto_nellaparola()
        
        if "Erro" in texto_site:
            st.error(texto_site)
        else:
            homilia = gerar_homilia(texto_site)
            st.subheader("Sua reflexão para hoje:")
            st.write(homilia)

st.divider()
st.caption("Desenvolvido com Python, Streamlit e Google Gemini API.")