import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import streamlit.components.v1 as components

# --- 1. CONFIGURAÇÃO SUPABASE ---
SUPABASE_URL = "https://msitsrebkgekgqbuclqp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1zaXRzcmVia2dla2dxYnVjbHFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA3NDE3MzgsImV4cCI6MjA4NjMxNzczOH0.AXZbP1hoCMCIwfHBH6iX98jy4XB2FoJp7P6i73ssq2k"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. CONFIGURAÇÃO GEMINI ---
API_KEY = "AIzaSyBFg4D-C9kYpZVF8TYLDZFMwF_GnBc6y5k"
genai.configure(api_key=API_KEY)

def get_model():
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m in modelos:
            if "flash" in m: return genai.GenerativeModel(m)
        return genai.GenerativeModel(modelos[0])
    except: return genai.GenerativeModel('gemini-1.5-flash')

# --- 3. UI/UX DESIGN PREMIUM (GLASSMORPHISM) ---
st.set_page_config(page_title="ChefPost Pro", page_icon="🥘", layout="wide")

st.markdown("""
    <style>
    /* Fundo principal com degradê moderno */
    .stApp {
        background: radial-gradient(circle at top right, #1e1e2e, #0e1117);
        color: #e0e0e0;
    }
    
    /* Estilização dos Cards (Efeito Vidro) */
    .item-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        border-radius: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease;
    }
    .item-card:hover {
        transform: translateY(-5px);
        border: 1px solid #FF4B2B;
    }
    
    /* Área de Texto Gerado */
    .copy-area {
        background: rgba(0, 0, 0, 0.3);
        color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #FF4B2B;
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
        margin-bottom: 15px;
    }
    
    /* Botões Customizados com Gradiente */
    .stButton>button {
        background: linear-gradient(135deg, #FF4B2B 0%, #FF416C 100%);
        color: white !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-radius: 12px;
        border: none;
        padding: 0.6rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 75, 43, 0.3);
    }
    .stButton>button:hover {
        box-shadow: 0 6px 20px rgba(255, 75, 43, 0.5);
        transform: scale(1.02);
    }
    
    /* Inputs Estilizados */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 10px !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #11141a;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Títulos */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        background: -webkit-linear-gradient(#eee, #777);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNÇÃO BOTÃO DE COPIAR ---
def copy_button(text, key):
    safe_text = text.replace("`", "'").replace("\n", "\\n").replace('"', '\\"')
    html_code = f"""
    <button id="btn-{key}" onclick="copyToClipboard('{key}')" style="
        width: 100%; background: #25D366; color: white; border: none; padding: 14px;
        border-radius: 10px; font-weight: bold; cursor: pointer; transition: 0.3s;
        box-shadow: 0 4px 10px rgba(37, 211, 102, 0.2);
    "> 📋 COPIAR CONTEÚDO </button>
    <script>
    function copyToClipboard(key) {{
        const text = "{safe_text}";
        navigator.clipboard.writeText(text).then(() => {{
            const btn = document.getElementById('btn-' + key);
            btn.innerHTML = '✅ COPIADO COM SUCESSO!';
            btn.style.background = '#128C7E';
            setTimeout(() => {{ 
                btn.innerHTML = '📋 COPIAR CONTEÚDO'; 
                btn.style.background = '#25D366';
            }}, 2000);
        }});
    }}
    </script> """
    components.html(html_code, height=70)

# --- 5. LÓGICA DE LOGIN ---
if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("<h1 style='text-align: center;'>🥘 ChefPost IA</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>Sua inteligência gastronômica para redes sociais</p>", unsafe_allow_html=True)
        
        aba_log, aba_cad = st.tabs(["🔒 Entrar", "✨ Nova Conta"])
        with aba_log:
            e = st.text_input("E-mail", key="l_e")
            s = st.text_input("Senha", type="password", key="l_s")
            if st.button("Acessar Plataforma"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": e, "password": s})
                    st.session_state.user = res
                    st.rerun()
                except: st.error("Credenciais inválidas.")
        with aba_cad:
            e_c = st.text_input("E-mail de Cadastro", key="c_e")
            s_c = st.text_input("Escolha uma Senha", type="password", key="c_s")
            if st.button("Criar Minha Conta"):
                try:
                    supabase.auth.sign_up({"email": e_c, "password": s_c})
                    st.success("Conta criada! Já pode fazer login.")
                except Exception as ex: st.error(f"Erro: {ex}")
else:
    # --- 6. PAINEL DO CHEF ---
    with st.sidebar:
        st.markdown("### 👨‍🍳 Seu Perfil")
        restaurante = st.text_input("Nome do Restaurante")
        tipo_comida = st.selectbox("Segmento", ["Hamburgueria", "Pizzaria", "Japonesa", "Marmitaria", "Doceria", "Italiana", "Petiscaria"])
        
        st.divider()
        st.markdown("### 📅 Funcionamento")
        dias_semana = st.multiselect("Dias de Operação", ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"], default=["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"])
        horario = st.text_input("Horário de Atendimento", placeholder="Ex: 18h às 23:30h")
        entrega = st.text_input("Taxa de Entrega", placeholder="Ex: Grátis ou R$ 7,00")

        st.divider()
        destino = st.selectbox("Onde vai postar?", ["Instagram", "WhatsApp", "iFood", "Google Meu Negócio"])
        estilo = st.select_slider("Estilo da Cópia", options=["Descontraído", "Persuasivo", "Gourmet"])
        
        if st.button("🚪 Sair"):
            st.session_state.user = None
            st.rerun()

    tab_gerador, tab_estrategia = st.tabs(["🚀 Gerador de Posts", "📊 Planejamento Estratégico"])

    with tab_gerador:
        st.markdown("## ✍️ O que vamos vender hoje?")
        num = st.number_input("Quantidade de Itens", 1, 10, 1)
        itens = []
        for i in range(num):
            st.markdown(f'<div class="item-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([3, 1])
            with c1: n = st.text_input(f"Nome do Item {i+1}", key=f"n{i}")
            with c2: p = st.text_input(f"Preço", key=f"p{i}")
            d = st.text_area(f"Breve descrição/ingredientes", key=f"d{i}", height=80)
            if n: itens.append({"nome": n, "preco": p, "desc": d})
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("✨ GERAR LEGENDAS PROFISSIONAIS"):
            if restaurante and itens:
                with st.spinner("O Chef IA está preparando suas legendas..."):
                    try:
                        model = get_model()
                        lista_p = "".join([f"- {x['nome']} (R$ {x['preco']}): {x['desc']}\n" for x in itens])
                        dias_str = ", ".join(dias_semana)
                        
                        prompt = (f"Você é um Copywriter especialista em gastronomia. Gere legendas magnéticas para {restaurante}.\n"
                                  f"Contexto: Aberto {dias_str} | Horário: {horario} | Entrega: {entrega}.\n"
                                  f"Estilo: {estilo} | Canal: {destino}.\n"
                                  f"Produtos:\n{lista_p}\n"
                                  f"Use emojis e CTAs fortes. Separe cada opção com '---SEPARAR---'.")
                        
                        res = model.generate_content(prompt)
                        legendas = [l.strip() for l in res.text.split('---SEPARAR---') if l.strip()]
                        
                        for idx, texto in enumerate(legendas):
                            st.markdown(f"### 📝 Sugestão {idx+1}")
                            st.markdown(f'<div class="copy-area">{texto}</div>', unsafe_allow_html=True)
                            copy_button(texto, f"btn_leg_{idx}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Erro na IA: {e}")
            else:
                st.warning("Preencha o nome da sua loja e pelo menos um produto!")

    with tab_estrategia:
        st.markdown("## 📊 Planejamento de Conteúdo")
        c_est1, c_est2 = st.columns(2)
        with c_est1:
            fase = st.selectbox("Fase do Mês", ["Início (Novidades)", "Meio (Engajamento)", "Fim (Ofertas)", "Especial (Feriados)"])
        with c_est2:
            passado = st.text_input("Tema do último post", placeholder="Ex: Reels da Cozinha")

        if st.button("📅 GERAR CRONOGRAMA SEMANAL"):
            if restaurante:
                with st.spinner("Analisando mercado..."):
                    try:
                        model = get_model()
                        prompt_est = (f"Crie um plano estratégico de 7 dias para {restaurante} ({tipo_comida}). "
                                      f"Fase: {fase}. Último post foi: {passado}. Aberto em {dias_semana}. "
                                      f"Formate em tópicos claros por dia.")
                        res = model.generate_content(prompt_est)
                        st.markdown(f'<div class="item-card" style="border-left: 5px solid #25D366;">{res.text}</div>', unsafe_allow_html=True)
                        copy_button(res.text, "plan_final")
                    except Exception as e:
                        st.error(f"Erro: {e}")
