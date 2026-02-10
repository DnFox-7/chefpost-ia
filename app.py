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
    .copy-area { background: #0d1117; color: #c9d1d9; padding: 15px; border-radius: 5px; font-family: sans-serif; white-space: pre-wrap; margin-bottom: 10px; border: 1px solid #30363d; line-height: 1.5; }
    .stButton>button { background: linear-gradient(90deg, #FF4B2B 0%, #FF416C 100%); color: white !important; font-weight: bold; border-radius: 10px; height: 50px; width: 100%; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNÇÕES AUXILIARES ---
def copy_button(text, key):
    safe_text = text.replace("`", "'").replace("\n", "\\n").replace('"', '\\"')
    html_code = f"""
    <button id="btn-{key}" onclick="copyToClipboard('{key}')" style="
        width: 100%; background-color: #25D366; color: white; border: none; padding: 12px;
        border-radius: 8px; font-weight: bold; cursor: pointer; display: flex;
        align-items: center; justify-content: center; gap: 10px; font-family: sans-serif;
    "> 📋 COPIAR LEGENDA </button>
    <script>
    function copyToClipboard(key) {{
        const text = "{safe_text}";
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
    </script> """
    components.html(html_code, height=65)

def verificar_plano(email):
    try:
        res = supabase.table("perfis_clientes").select("plano_ativo").eq("email", email).execute()
        return res.data[0]['plano_ativo'] if res.data else False
    except: return False

def cadastrar_perfil(email):
    try: supabase.table("perfis_clientes").insert({"email": email, "plano_ativo": False}).execute()
    except: pass

# --- 5. SISTEMA DE LOGIN / CADASTRO ---
if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("🥘 ChefPost IA")
        aba_login, aba_cadastro = st.tabs(["Login", "Criar Conta"])
        
        with aba_login:
            e = st.text_input("E-mail", key="login_e")
            s = st.text_input("Senha", type="password", key="login_s")
            if st.button("Entrar"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": e, "password": s})
                    if verificar_plano(e):
                        st.session_state.user = res
                        st.rerun()
                    else:
                        st.warning("⚠️ Conta aguardando ativação. PIX: danillo.lima328@gmail.com")
                except: st.error("E-mail ou senha incorretos.")

        with aba_cadastro:
            e_c = st.text_input("Novo E-mail", key="cad_e")
            s_c = st.text_input("Crie uma Senha", type="password", key="cad_s")
            if st.button("Criar Minha Conta"):
                try:
                    supabase.auth.sign_up({"email": e_c, "password": s_c})
                    cadastrar_perfil(e_c)
                    st.success("✅ Conta criada com sucesso! Agora faça o login.")
                except Exception as ex: st.error(f"Erro ao cadastrar: {ex}")

else:
    # --- 6. APP LOGADO ---
    with st.sidebar:
        st.header("👨‍🍳 Painel")
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

    if st.button("✨ GERAR LEGENDAS SEPARADAS"):
        if restaurante and itens:
            with st.spinner("Chef IA escrevendo..."):
                try:
                    model = genai.GenerativeModel('gemini-3-flash-preview')
                    for idx, item in enumerate(itens):
                        prompt = (f"Crie uma legenda para {item['nome']} (R$ {item['preco']}). "
                                  f"Descrição: {item['desc']}. Restaurante: {restaurante}. "
                                  f"Estilo: {estilo}. Canal: {destino}. Taxa: {taxa}. Tempo: {tempo}. "
                                  f"{f'Horário: {dias} - {horas}' if dias else ''}")
                        
                        res = model.generate_content(prompt)
                        legenda = res.text
                        
                        st.markdown(f"### 📦 {item['nome']}")
                        st.markdown(f'<div class="copy-area">{legenda}</div>', unsafe_allow_html=True)
                        copy_button(legenda, f"btn_{idx}")
                        st.divider()
                    st.balloons()
                except Exception as e: st.error(f"Erro: {e}")
