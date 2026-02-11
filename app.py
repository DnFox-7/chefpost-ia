import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import streamlit.components.v1 as components

# --- 1. CONFIGURAÇÃO SUPABASE ---
SUPABASE_URL = "https://msitsrebkgekgqbuclqp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1zaXRzcmVia2dla2dxYnVjbHFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA3NDE3MzgsImV4cCI6MjA4NjMxNzczOH0.AXZbP1hoCMCIwfHBH6iX98jy4XB2FoJp7P6i73ssq2k"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. CONFIGURAÇÃO GEMINI (SUA CHAVE NOVA) ---
API_KEY = "AIzaSyBFg4D-C9kYpZVF8TYLDZFMwF_GnBc6y5k"
genai.configure(api_key=API_KEY)

# A FUNÇÃO MÁGICA QUE VOCÊ ME MANDOU:
def get_model():
    # Esta função varre os modelos disponíveis e pega o que funciona
    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    for m in modelos:
        if "flash" in m:
            return genai.GenerativeModel(m)
    return genai.GenerativeModel(modelos[0])

# --- 3. ESTILO VISUAL (SEU LAYOUT PRESERVADO) ---
st.set_page_config(page_title="ChefPost Pro", page_icon="🥘", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .item-card { background-color: rgba(255, 75, 43, 0.05); padding: 20px; border-radius: 15px; border: 1px solid #FF4B2B; margin-bottom: 20px; }
    .copy-area { background: #161b22; color: #c9d1d9; padding: 15px; border-radius: 8px; font-family: sans-serif; white-space: pre-wrap; margin-bottom: 10px; border: 1px solid #30363d; line-height: 1.6; }
    .stButton>button { background: linear-gradient(90deg, #FF4B2B 0%, #FF416C 100%); color: white !important; font-weight: bold; border-radius: 10px; height: 50px; width: 100%; border: none; }
    .strategy-card { background-color: #1e252e; padding: 20px; border-radius: 10px; border-left: 5px solid #25D366; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNÇÃO BOTÃO DE COPIAR ---
def copy_button(text, key):
    safe_text = text.replace("`", "'").replace("\n", "\\n").replace('"', '\\"')
    html_code = f"""
    <button id="btn-{key}" onclick="copyToClipboard('{key}')" style="width: 100%; background-color: #25D366; color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer;"> 📋 COPIAR TEXTO </button>
    <script>
    function copyToClipboard(key) {{
        const text = "{safe_text}";
        navigator.clipboard.writeText(text).then(() => {{
            const btn = document.getElementById('btn-' + key);
            btn.innerHTML = '✅ COPIADO!';
            setTimeout(() => {{ btn.innerHTML = '📋 COPIAR TEXTO'; }}, 2000);
        }});
    }}
    </script> """
    components.html(html_code, height=65)

# --- 5. LÓGICA DE LOGIN ---
if 'user' not in st.session_state: st.session_state.user = None
if st.session_state.user is None:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("🥘 ChefPost IA")
        aba_log, aba_cad = st.tabs(["Login", "Criar Conta"])
        with aba_log:
            e = st.text_input("E-mail", key="l_e")
            s = st.text_input("Senha", type="password", key="l_s")
            if st.button("Entrar"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": e, "password": s})
                    st.session_state.user = res
                    st.rerun()
                except: st.error("Dados incorretos.")
        with aba_cad:
            e_c = st.text_input("Novo E-mail", key="c_e")
            s_c = st.text_input("Senha", type="password", key="c_s")
            if st.button("Registrar"):
                try:
                    supabase.auth.sign_up({"email": e_c, "password": s_c})
                    st.success("Conta criada! Tente logar.")
                except Exception as ex: st.error(f"Erro: {ex}")
else:
    # --- 6. PAINEL DO CHEF ---
    with st.sidebar:
        st.header("👨‍🍳 Painel")
        restaurante = st.text_input("Nome da Loja", placeholder="Ex: Burguer House")
        tipo_comida = st.selectbox("Segmento", ["Hamburgueria", "Pizzaria", "Japonesa", "Marmitaria", "Doceria", "Italiana"])
        st.divider()
        destino = st.selectbox("Canal", ["Instagram", "WhatsApp", "iFood", "Facebook Ads"])
        estilo = st.select_slider("Estilo", options=["Descontraído", "Persuasivo", "Gourmet"])
        if st.button("Sair"):
            st.session_state.user = None
            st.rerun()

    tab_gerador, tab_estrategia = st.tabs(["🚀 Gerador de Legendas", "📊 Estratégia"])

    with tab_gerador:
        num = st.number_input("Quantos produtos?", 1, 10, 1)
        itens = []
        for i in range(num):
            st.markdown(f'<div class="item-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([3, 1])
            with c1: n = st.text_input(f"Produto {i+1}", key=f"n{i}")
            with c2: p = st.text_input(f"Preço", key=f"p{i}")
            d = st.text_area(f"O que tem nele?", key=f"d{i}", height=70)
            if n: itens.append({"nome": n, "preco": p, "desc": d})
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("✨ GERAR LEGENDAS"):
            if restaurante and itens:
                with st.spinner("Chef IA preparando..."):
                    try:
                        # USANDO A SUA LÓGICA QUE FUNCIONA:
                        model = get_model()
                        
                        lista_p = "".join([f"- {x['nome']} (R$ {x['preco']}): {x['desc']}\n" for x in itens])
                        prompt = (f"Atue como redator profissional. Gere legendas de venda para o restaurante {restaurante}. "
                                  f"Estilo: {estilo}. Canal: {destino}.\nProdutos:\n{lista_p}\n"
                                  f"Separe cada legenda estritamente com o marcador '---SEPARAR---'.")
                        
                        res = model.generate_content(prompt)
                        legendas = [l.strip() for l in res.text.split('---SEPARAR---') if l.strip()]
                        
                        for idx, texto in enumerate(legendas):
                            st.markdown(f"### 📦 Legenda {idx+1}")
                            st.markdown(f'<div class="copy-area">{texto}</div>', unsafe_allow_html=True)
                            copy_button(texto, f"btn_leg_{idx}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Erro ao acessar IA: {e}")

    with tab_estrategia:
        if st.button("📅 GERAR PLANO SEMANAL"):
            if restaurante:
                with st.spinner("Gerando planejamento..."):
                    try:
                        model = get_model()
                        res = model.generate_content(f"Crie um calendário de posts para {restaurante} ({tipo_comida}).")
                        st.markdown('<div class="strategy-card">', unsafe_allow_html=True)
                        st.write(res.text)
                        st.markdown('</div>', unsafe_allow_html=True)
                        copy_button(res.text, "plan_sem")
                    except Exception as e:
                        st.error(f"Erro ao gerar estratégia: {e}")
