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
    .result-box { background-color: #161b22; padding: 15px; border-radius: 10px; border-left: 5px solid #FF4B2B; margin-bottom: 30px; }
    .stButton>button { background: linear-gradient(90deg, #FF4B2B 0%, #FF416C 100%); color: white !important; font-weight: bold; border-radius: 10px; height: 50px; width: 100%; }
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
            except: st.error("Login inválido.")
else:
    # --- 5. PAINEL LATERAL ---
    with st.sidebar:
        st.header("👨‍🍳 Configurações")
        restaurante = st.text_input("Restaurante", placeholder="Ex: Burguer House")
        destino = st.selectbox("Onde vai postar?", ["Instagram (Feed/Reels)", "WhatsApp (Cardápio)", "iFood", "Facebook Ads"])
        
        dias, horas = "", ""
        if "WhatsApp" in destino:
            dias = st.multiselect("Dias", ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"], default=["Sex", "Sáb", "Dom"])
            horas = st.text_input("Horário", "18h às 23h")
        
        estilo = st.select_slider("Estilo da Escrita", options=["Descontraído", "Persuasivo", "Gourmet"])
        taxa = st.text_input("Taxa de Entrega", "A consultar")
        tempo = st.text_input("Tempo Estimado", "30-50 min")
        
        if st.button("Sair"):
            st.session_state.user = None
            st.rerun()

    # --- 6. ENTRADA DE PRODUTOS ---
    st.title("🚀 Gerador de Legendas Individuais")
    num = st.number_input("Quantos produtos?", 1, 10, 1)
    
    itens = []
    for i in range(num):
        st.markdown(f'<div class="item-card">', unsafe_allow_html=True)
        c1, c2 = st.columns([3, 1])
        with c1: n = st.text_input(f"Nome do Produto {i+1}", key=f"n{i}")
        with c2: p = st.text_input(f"Preço", key=f"p{i}")
        d = st.text_area(f"O que tem nele?", key=f"d{i}", height=70)
        if n: itens.append({"nome": n, "preco": p, "desc": d})
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 7. GERAÇÃO INDIVIDUAL ---
    if st.button("✨ GERAR LEGENDAS SEPARADAS"):
        if restaurante and itens:
            with st.spinner("O Chef IA está preparando as legendas separadamente..."):
                try:
                    model = genai.GenerativeModel('gemini-3-flash-preview')
                    st.divider()
                    
                    for idx, item in enumerate(itens):
                        # Prompt focado apenas no item do loop
                        prompt = (
                            f"Você é um copywriter gastronômico experiente. Crie uma legenda exclusiva para o produto: {item['nome']}. "
                            f"Valor: R$ {item['preco']}. Ingredientes/Descrição: {item['desc']}. "
                            f"Restaurante: {restaurante}. Canal: {destino}. Estilo: {estilo}. "
                            f"Taxa: {taxa}. Tempo: {tempo}. "
                            f"{f'Funcionamento: {dias} - {horas}' if dias else ''}\n"
                            f"Instrução: Foque 100% neste produto. Use emojis adequados e finalize com uma CTA (chamada para ação)."
                        )
                        
                        res = model.generate_content(prompt)
                        
                        # --- EXIBIÇÃO INDIVIDUAL COM BOTÃO DE COPIAR ---
                        st.markdown(f"### 📦 Legenda: {item['nome']}")
                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                        
                        # O st.code gera automaticamente o botão de cópia no canto superior direito
                        st.code(res.text, language=None)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.balloons()
                    st.success("✅ Legendas geradas! Use o ícone no canto superior direito de cada caixa para copiar.")
                except Exception as e:
                    st.error(f"Erro ao gerar: {e}")
        else:
            st.warning("Preencha o nome do restaurante e adicione os produtos!")
