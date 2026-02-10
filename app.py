import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client

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
    .stButton>button { background: linear-gradient(90deg, #FF4B2B 0%, #FF416C 100%); color: white !important; font-weight: bold; border: none; width: 100%; border-radius: 10px; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIN ---
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
            except: st.error("Login inválido ou conta não ativada.")
else:
    # --- 5. PAINEL LATERAL ---
    with st.sidebar:
        st.header("👨‍🍳 Configurações")
        restaurante = st.text_input("Restaurante", placeholder="Nome da Loja")
        
        st.divider()
        destino = st.selectbox("Onde vai postar?", ["Instagram (Feed/Reels)", "WhatsApp (Cardápio)", "iFood", "Ads"])
        
        # Campos de Cardápio para WhatsApp
        dias, horas = "", ""
        if "WhatsApp" in destino:
            dias = st.multiselect("Dias", ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"], default=["Sex", "Sáb", "Dom"])
            horas = st.text_input("Horário", "18h às 23h")
        
        st.divider()
        
        # --- A MUDANÇA SOLICITADA ---
        estilo = st.select_slider(
            "Personalidade do Post", 
            options=["Descontraída", "Vendedora", "Elegante"]
        )
        
        taxa = st.text_input("Taxa de Entrega", "Grátis")
        tempo = st.text_input("Tempo", "30-50 min")
        
        if st.button("Sair"):
            st.session_state.user = None
            st.rerun()

    # --- 6. ÁREA CENTRAL ---
    st.title("🚀 Gerador de Conteúdo")
    num = st.number_input("Produtos", 1, 10, 1)
    
    itens = []
    for i in range(num):
        st.markdown(f'<div class="item-card">', unsafe_allow_html=True)
        c1, c2 = st.columns([3, 1])
        with c1: n = st.text_input(f"Produto {i+1}", key=f"n{i}")
        with c2: p = st.text_input(f"Preço", key=f"p{i}")
        d = st.text_area(f"Descrição", key=f"d{i}", height=70)
        if n: itens.append({"nome": n, "preco": p, "desc": d})
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("✨ GERAR TEXTO PARA " + destino.upper()):
        if restaurante and itens:
            with st.spinner("Chef IA preparando..."):
                try:
                    # Usando o modelo confirmado na sua lista (Gemini 3 Flash)
                    model = genai.GenerativeModel('gemini-3-flash-preview')
                    
                    prod_text = "".join([f"- {x['nome']} (R$ {x['preco']}): {x['desc']}\n" for x in itens])
                    contexto_whats = f"\nFuncionamento: {', '.join(dias)} - {horas}" if dias else ""
                    
                    prompt = (
                        f"Crie um post gourmet para {destino} do {restaurante}. "
                        f"Personalidade da escrita: {estilo}. Taxa: {taxa}. Tempo: {tempo}. {contexto_whats}\n"
                        f"Produtos:\n{prod_text}"
                        f"\nInstruções: Se for 'Descontraída', use gírias leves. 'Vendedora', foque em urgência. 'Elegante', seja refinado."
                    )
                    
                    res = model.generate_content(prompt)
                    st.subheader("✅ Resultado:")
                    st.text_area("Copie aqui:", value=res.text, height=400)
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro: {e}")
