import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client

# --- 1. CONFIGURAÇÃO SUPABASE ---
SUPABASE_URL = "https://msitsrebkgekgqbuclqp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1zaXRzcmVia2dla2dxYnVjbHFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA3NDE3MzgsImV4cCI6MjA4NjMxNzczOH0.AXZbP1hoCMCIwfHBH6iX98jy4XB2FoJp7P6i73ssq2k"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. CONFIGURAÇÃO GEMINI ---
API_KEY_GEMINI = "AIzaSyAWeO6CpkGvhghUZa_T5FY2o8Jw2fcRzL8"
genai.configure(api_key=API_KEY_GEMINI)

# --- 3. DESIGN E CSS ---
st.set_page_config(page_title="ChefPost Pro", page_icon="🥘", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .item-card { background-color: rgba(128, 128, 128, 0.1); padding: 20px; border-radius: 15px; border: 2px solid #FF4B2B; margin-bottom: 25px; }
    .stButton>button { background: linear-gradient(90deg, #FF4B2B 0%, #FF416C 100%); color: white !important; font-weight: bold; height: 50px; width: 100%; border-radius: 10px; }
    .stTextArea textarea { background-color: #111 !important; color: #FFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNÇÕES DE SEGURANÇA ---
def verificar_plano(email):
    try:
        res = supabase.table("perfis_clientes").select("plano_ativo").eq("email", email).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]['plano_ativo']
        return False
    except:
        return False

def cadastrar_no_banco(email):
    try:
        supabase.table("perfis_clientes").insert({"email": email, "plano_ativo": False}).execute()
    except:
        pass

# --- 5. SISTEMA DE LOGIN / CADASTRO ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("🥘 ChefPost IA")
        aba_log, aba_cad = st.tabs(["Login", "Criar Conta"])
        
        with aba_log:
            e = st.text_input("E-mail")
            s = st.text_input("Senha", type="password")
            if st.button("Entrar"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": e, "password": s})
                    if verificar_plano(e):
                        st.session_state.user = res
                        st.rerun()
                    else:
                        st.error("🚫 Acesso Pendente. Realize o pagamento para ativar sua conta.")
                except:
                    st.error("E-mail ou senha incorretos.")

        with aba_cad:
            e_c = st.text_input("Seu melhor e-mail")
            s_c = st.text_input("Crie uma senha (mín. 6 dígitos)", type="password")
            if st.button("Registrar"):
                try:
                    supabase.auth.sign_up({"email": e_c, "password": s_c})
                    cadastrar_no_banco(e_c)
                    st.success("✅ Conta criada! Após o pagamento, seu acesso será liberado.")
                except Exception as ex:
                    st.error(f"Erro ao cadastrar: {ex}")

else:
    # --- 6. O APLICATIVO ---
    with st.sidebar:
        st.header("👨‍🍳 Painel")
        st.write(f"Logado como: {st.session_state.user.user.email}")
        if st.button("Sair"):
            st.session_state.user = None
            st.rerun()
        
        st.divider()
        restaurante = st.text_input("Restaurante")
        formato = st.radio("Formato", ["Individual", "Cardápio WhatsApp"])
        taxa = st.text_input("Taxa Entrega", "Grátis")
        tempo = st.text_input("Tempo de Espera", "30-50 min")
        
        dia, horario = "", ""
        if formato == "Cardápio WhatsApp":
            dia = st.selectbox("📅 Dia", ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"])
            horario = st.text_input("⌚ Horário", "18h às 23h")

    st.title("🚀 Gerador de Conteúdo")
    num = st.number_input("Quantos produtos?", 1, 10, 1)
    
    itens = []
    for i in range(num):
        st.markdown(f'<div class="item-card"><b>PRODUTO #{i+1}</b>', unsafe_allow_html=True)
        c1, c2 = st.columns([3, 1])
        with c1: 
            n = st.text_input("Nome", key=f"n{i}")
        with c2: 
            p = st.text_input("Preço", key=f"p{i}")
        d = st.text_input("Ingredientes/Descrição", key=f"d{i}")
        
        if n:
            itens.append({"nome": n, "preco": p, "desc": d})
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 GERAR AGORA"):
        if restaurante and itens:
            with st.spinner("Chef preparando..."):
                try:
                    # ALTERAÇÃO PARA ESTABILIDADE: Nome limpo do modelo
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    p_text = "".join([f"- {x['nome']} (R$ {x['preco']}): {x['desc']}\n" for x in itens])
                    
                    prompt = (
                        f"Atue como um redator publicitário de alto nível especializado em gastronomia. "
                        f"Crie um post para o restaurante {restaurante}. "
                        f"Formato solicitado: {formato}. "
                        f"Itens do cardápio: {p_text}. "
                        f"Detalhes: Entrega {taxa}, Tempo {tempo}. {dia} {horario}. "
                        f"Use uma linguagem que desperte o apetite, emojis e hashtags estratégicas."
                    )
                    
                    res = model.generate_content(prompt)
                    
                    if res.text:
                        st.text_area("Copiado com Sucesso:", value=res.text, height=400)
                    else:
                        st.warning("A IA não gerou texto. Tente clicar no botão novamente.")

                except Exception as e:
                    st.error(f"Erro na IA: {e}")
                    st.info("Dica: Se o erro for 404, tente reiniciar o App no painel do Streamlit.")
        else:
            st.warning("Preencha o nome do restaurante e adicione pelo menos um produto.")
