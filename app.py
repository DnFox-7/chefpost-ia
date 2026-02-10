import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import streamlit.components.v1 as components

# --- 1. CONFIGURAÇÃO SUPABASE ---
SUPABASE_URL = "https://msitsrebkgekgqbuclqp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1zaXRzcmVia2dla2dxYnVjbHFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA3NDE3MzgsImV4cCI6MjA4NjMxNzczOH0.AXZbP1hoCMCIwfHBH6iX98jy4XB2FoJp7P6i73ssq2k"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. CONFIGURAÇÃO GEMINI ---
API_KEY_GEMINI = "AIzaSyBNI6HOmI4YPCO88XCxdDl4krCwuGR_fSU"
genai.configure(api_key=API_KEY_GEMINI)

# --- 3. DESIGN ---
st.set_page_config(page_title="ChefPost Pro", page_icon="🥘", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .item-card { background-color: rgba(255, 75, 43, 0.05); padding: 20px; border-radius: 15px; border: 1px solid #FF4B2B; margin-bottom: 20px; }
    .copy-area { background: #161b22; color: #c9d1d9; padding: 15px; border-radius: 8px; font-family: sans-serif; white-space: pre-wrap; margin-bottom: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNÇÃO BOTÃO DE COPIAR ---
def copy_button(text, key):
    safe_text = text.replace("`", "'").replace("\n", "\\n").replace('"', '\\"')
    html_code = f"""
    <button id="btn-{key}" onclick="copyToClipboard('{key}')" style="
        width: 100%; background-color: #25D366; color: white; border: none; padding: 12px;
        border-radius: 8px; font-weight: bold; cursor: pointer; display: flex;
        align-items: center; justify-content: center; gap: 10px; font-family: sans-serif;
    "> 📋 COPIAR TEXTO </button>
    <script>
    function copyToClipboard(key) {{
        const text = "{safe_text}";
        navigator.clipboard.writeText(text).then(() => {{
            const btn = document.getElementById('btn-' + key);
            btn.innerHTML = '✅ COPIADO!';
            btn.style.backgroundColor = '#128C7E';
            setTimeout(() => {{ btn.innerHTML = '📋 COPIAR TEXTO'; btn.style.backgroundColor = '#25D366'; }}, 2000);
        }});
    }}
    </script> """
    components.html(html_code, height=65)

# --- 5. LOGIN ---
if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("🥘 ChefPost IA")
        e = st.text_input("E-mail")
        s = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e, "password": s})
                st.session_state.user = res
                st.rerun()
            except: st.error("Erro no login.")
else:
    # --- 6. APP ---
    with st.sidebar:
        restaurante = st.text_input("Nome da Loja")
        tipo_comida = st.selectbox("Segmento", ["Hamburgueria", "Pizzaria", "Japonesa", "Marmitaria"])
        if st.button("Sair"):
            st.session_state.user = None
            st.rerun()

    tab1, tab2 = st.tabs(["🚀 Legendas", "📊 Estratégia"])

    with tab1:
        num = st.number_input("Produtos", 1, 5, 1)
        itens = []
        for i in range(num):
            n = st.text_input(f"Nome {i+1}", key=f"n{i}")
            p = st.text_input(f"Preço {i+1}", key=f"p{i}")
            if n: itens.append({"nome": n, "preco": p})

        if st.button("✨ GERAR"):
            try:
                # Mudança para o modelo PRO que é mais aceito em versões antigas de biblioteca
                model = genai.GenerativeModel('gemini-1.5-pro')
                
                lista = "".join([f"- {x['nome']} (R$ {x['preco']})\n" for x in itens])
                res = model.generate_content(f"Crie legendas separadas por '---' para: {lista} do restaurante {restaurante}")
                
                legendas = res.text.split('---')
                for idx, txt in enumerate(legendas):
                    if txt.strip():
                        st.markdown(f'<div class="copy-area">{txt.strip()}</div>', unsafe_allow_html=True)
                        copy_button(txt.strip(), f"b{idx}")
            except Exception as e:
                st.error(f"Erro: {e}")

    with tab2:
        if st.button("📅 PLANO SEMANAL"):
            try:
                model = genai.GenerativeModel('gemini-1.5-pro')
                res = model.generate_content(f"Plano de posts para {restaurante}")
                st.write(res.text)
                copy_button(res.text, "strat")
            except Exception as e:
                st.error(f"Erro: {e}")
