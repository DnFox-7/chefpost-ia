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
genai.configure(api_key=API_KEY_GEMINI, transport='rest')

# --- 3. DESIGN ---
st.set_page_config(page_title="ChefPost Pro", page_icon="🥘", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .item-card { background-color: rgba(255, 75, 43, 0.05); padding: 20px; border-radius: 15px; border: 1px solid #FF4B2B; margin-bottom: 20px; }
    .result-container { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 30px; position: relative; }
    .copy-area { background: #0d1117; color: #c9d1d9; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; margin-bottom: 15px; border: 1px solid #30363d; }
    .stButton>button { background: linear-gradient(90deg, #FF4B2B 0%, #FF416C 100%); color: white !important; font-weight: bold; border-radius: 10px; height: 50px; width: 100%; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNÇÃO PARA O BOTÃO DE COPIAR (JS) ---
def copy_button(text, key):
    # Escapa quebras de linha para o JS não quebrar
    safe_text = text.replace("`", "'").replace("\n", "\\n")
    html_code = f"""
    <button id="btn-{key}" onclick="copyToClipboard('{key}')" style="
        width: 100%;
        background-color: #25D366;
        color: white;
        border: none;
        padding: 12px;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        font-family: sans-serif;
    ">
        📋 COPIAR LEGENDA
    </button>

    <script>
    function copyToClipboard(key) {{
        const text = `{safe_text}`;
        navigator.clipboard.writeText(text).then(() => {{
            const btn = document.getElementById('btn-' + key);
            btn.innerHTML = '✅ COPIADO!';
            btn.style.backgroundColor = '#128C7E';
            setTimeout(() => {{
                btn.innerHTML = '📋 COPIAR LEGENDA';
                btn.style.backgroundColor = '#25D366';
            }}, 2000);
        }});
    }}
    </script>
    """
    components.html(html_code, height=60)

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
    # --- 6. PAINEL LATERAL ---
    with st.sidebar:
        st.header("👨‍🍳 Configurações")
        restaurante = st.text_input("Restaurante", placeholder="Ex: Burger King")
        destino = st.selectbox("Canal", ["Instagram", "WhatsApp", "iFood", "Facebook Ads"])
        
        dias, horas = "", ""
        if "WhatsApp" in destino:
            dias = st.multiselect("Dias", ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"], default=["Sex", "Sáb", "Dom"])
            horas = st.text_input("Horário", "18h às 23h")
            
        estilo = st.select_slider("Estilo", options=["Descontraído", "Persuasivo", "Gourmet"])
        taxa = st.text_input("Taxa de Entrega", "A consultar")
        tempo = st.text_input("Tempo Estimado", "30-50 min")
        
        if st.button("Sair"):
            st.session_state.user = None
            st.rerun()

    # --- 7. ENTRADA DE PRODUTOS ---
    st.title("🚀 Gerador de Legendas Individuais")
    num = st.number_input("Quantos produtos?", 1, 10, 1)
    
    itens = []
    for i in range(num):
        st.markdown(f'<div class="item-card">', unsafe_allow_html=True)
        c1, c2 = st.columns([3, 1])
        with c1: n = st.text_input(f"Produto {i+1}", key=f"n{i}")
        with c2: p = st.text_input(f"Preço", key=f"p{i}")
        d = st.text_area(f"Descrição", key=f"d{i}", height=70)
        if n: itens.append({"nome": n, "preco": p, "desc": d})
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 8. GERAÇÃO E EXIBIÇÃO ---
    if st.button("✨ GERAR LEGENDAS SEPARADAS"):
        if restaurante and itens:
            with st.spinner("O Chef IA está escrevendo..."):
                try:
                    model = genai.GenerativeModel('gemini-3-flash-preview')
                    st.divider()
                    
                    for idx, item in enumerate(itens):
                        prompt = (
                            f"Crie uma legenda para {item['nome']} (R$ {item['preco']}). "
                            f"Descrição: {item['desc']}. Restaurante: {restaurante}. "
                            f"Estilo: {estilo}. Canal: {destino}. Taxa: {taxa}. Tempo: {tempo}. "
                            f"{f'Horário: {dias} - {horas}' if dias else ''}"
                        )
                        
                        res = model.generate_content(prompt)
                        legenda = res.text
                        
                        # --- BOX DE RESULTADO COM BOTÃO VERDE ---
                        st.markdown(f"### 📦 {item['nome']}")
                        st.markdown(f'<div class="copy-area">{legenda}</div>', unsafe_allow_html=True)
                        
                        # Chama a função do botão de copiar personalizado
                        copy_button(legenda, f"copy_{idx}")
                        
                        st.divider()
                    
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro: {e}")
