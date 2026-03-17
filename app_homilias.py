import streamlit as st
import google.generativeai as genai

st.title("🔎 Raio-X do Gemini")

# Puxa a sua chave do cofre do Streamlit
if "MINHA_CHAVE" in st.secrets:
    genai.configure(api_key=st.secrets["MINHA_CHAVE"])
    st.success("✅ Chave de API lida com sucesso do painel Secrets!")
else:
    st.error("❌ A chave não foi encontrada no painel Secrets.")

st.write("### Modelos que o Google liberou para esta chave:")

try:
    # Pergunta direto para o servidor do Google quais modelos existem para você
    modelos_encontrados = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            st.code(m.name) # Imprime o nome exato na tela
            modelos_encontrados = True
            
    if not modelos_encontrados:
        st.warning("A chave conectou, mas o Google diz que não há modelos de texto liberados para ela.")

except Exception as e:
    st.error(f"Erro ao tentar listar os modelos: {e}")
