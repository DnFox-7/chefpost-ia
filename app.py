import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import streamlit.components.v1 as components

# --- 1. CONFIGURAÇÃO SUPABASE ---
SUPABASE_URL = "https://msitsrebkgekgqbuclqp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1zaXRzcmVia2dla2dxYnVjbHFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA3NDE3MzgsImV4cCI6MjA4NjMxNzczOH0.AXZbP1hoCMCIwfHBH6iX98jy4XB2FoJp7P6i73ssq2k"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. CONFIGURAÇÃO GEMINI ---
# Trocado para 1.5-flash para garantir limite de 1500 requisições/dia no plano free
API_KEY_GEMINI = "AIzaSyBNI6HOmI4YPCO88XCxdDl4krCwuGR_fSU"
genai.configure(api_key=API_KEY_GEMINI, transport='rest')

# --- 3. DESIGN E CSS ---
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

# --- 4. FUNÇÃO BOTÃO DE COPIAR (JS) ---
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

# --- 5. FUNÇÕES DE ACESSO ---
def verificar_plano(email):
    try:
        res = supabase.table("perfis_clientes").select("plano_ativo").eq("email", email).execute()
        return res.data[0]['plano_ativo'] if res.data else False
    except: return False

def cadastrar_perfil(email):
    try: supabase.table("perfis_clientes").insert({"email": email, "plano_ativo": False}).execute()
    except: pass

# --- 6. SISTEMA DE LOGIN E CADASTRO ---
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
                    if verificar_plano(e):
                        st.session_state.user = res
                        st.rerun()
                    else: st.warning("⚠️ Conta aguardando ativação (PIX: danillo.lima328@gmail.com)")
                except: st.error("Dados incorretos.")
        with aba_cad:
            e_c = st.text_input("E-mail", key="c_e")
            s_c = st.text_input("Senha", type="password", key="c_s")
            if st.button("Registrar"):
                try:
                    supabase.auth.sign_up({"email": e_c, "password": s_c})
                    cadastrar_perfil(e_c)
                    st.success("Conta criada! Fale com o suporte para ativar.")
                except Exception as ex: st.error(f"Erro: {ex}")
else:
    # --- 7. APP PRINCIPAL ---
    with st.sidebar:
        st.header("👨‍🍳 Painel")
        restaurante = st.text_input("Restaurante", placeholder="Ex: Burguer do Zé")
        tipo_comida = st.selectbox("Tipo de Cozinha", ["Hamburgueria", "Pizzaria", "Japonesa", "Marmitaria", "Doceria", "Italiana", "Churrascaria"])
        st.divider()
        destino = st.selectbox("Onde vai postar?", ["Instagram", "WhatsApp", "iFood", "Facebook Ads"])
        
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

    tab_gerador, tab_estrategia = st.tabs(["🚀 Gerador de Legendas", "📊 Estratégia & Tráfego"])

    # --- ABA 1: GERADOR ---
    with tab_gerador:
        st.subheader("Crie legendas profissionais")
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

        if st.button("✨ GERAR TODAS AS LEGENDAS"):
            if restaurante and itens:
                with st.spinner("Chef IA preparando..."):
                    try:
                        # Modelo trocado para 1.5-flash para evitar erro 429
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        
                        lista_p = "".join([f"- {x['nome']} (R$ {x['preco']}): {x['desc']}\n" for x in itens])
                        info_func = f"Atendimento: {', '.join(dias)} - {horas}" if dias else ""
                        
                        prompt = (
                            f"Atue como redator focado em vendas. Gere legendas INDIVIDUAIS para o restaurante {restaurante}. "
                            f"Estilo: {estilo}. Canal: {destino}. Taxa: {taxa}. Tempo: {tempo}. {info_func}\n"
                            f"Produtos:\n{lista_p}\n"
                            f"SEPARE CADA LEGENDA COM O MARCADOR '---SEPARAR---'. Seja criativo!"
                        )
                        
                        res = model.generate_content(prompt)
                        legendas = [l.strip() for l in res.text.split('---SEPARAR---') if l.strip()]
                        
                        st.divider()
                        for idx, texto in enumerate(legendas):
                            nome_prod = itens[idx]['nome'] if idx < len(itens) else f"Opção {idx+1}"
                            st.markdown(f"### 📦 {nome_prod}")
                            st.markdown(f'<div class="copy-area">{texto}</div>', unsafe_allow_html=True)
                            copy_button(texto, f"btn_leg_{idx}")
                            st.divider()
                        st.balloons()
                    except Exception as e:
                        st.error(f"Erro de conexão. Tente novamente em instantes. {e}")
            else: st.warning("Preencha o nome do restaurante e adicione produtos!")

    # --- ABA 2: ESTRATÉGIA ---
    with tab_estrategia:
        st.subheader("Consultoria de Crescimento")
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            if st.button("📅 CALENDÁRIO SEMANAL"):
                if restaurante:
                    with st.spinner("Planejando..."):
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        res = model.generate_content(f"Crie um planejamento de 7 dias de posts para {restaurante} ({tipo_comida}).")
                        st.markdown('<div class="strategy-card">', unsafe_allow_html=True)
                        st.markdown(res.text)
                        st.markdown('</div>', unsafe_allow_html=True)
                        copy_button(res.text, "plan_sem")
        
        with col_c2:
            if st.button("📢 GUIA DE ANÚNCIOS"):
                if restaurante:
                    with st.spinner("Analisando..."):
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        res = model.generate_content(f"Sugira público e estratégia de tráfego pago para {tipo_comida} ({restaurante}).")
                        st.markdown('<div class="strategy-card" style="border-left-color: #FF4B2B;">', unsafe_allow_html=True)
                        st.markdown(res.text)
                        st.markdown('</div>', unsafe_allow_html=True)
                        copy_button(res.text, "ads_sug")
