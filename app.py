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
    # Esta função garante que o código use sempre o modelo disponível na sua conta
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m in modelos:
            if "flash" in m:
                return genai.GenerativeModel(m)
        return genai.GenerativeModel(modelos[0])
    except:
        return genai.GenerativeModel('gemini-1.5-flash')

# --- 3. ESTILO VISUAL (LAYOUT DARK PREMIUM) ---
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

# --- 5. LÓGICA DE ACESSO ---
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
                    st.success("Conta criada! Já pode fazer login.")
                except Exception as ex: st.error(f"Erro: {ex}")
else:
    # --- 6. PAINEL LATERAL (CONFIGURAÇÕES) ---
    with st.sidebar:
        st.header("👨‍🍳 Configurações")
        restaurante = st.text_input("Nome da Loja")
        tipo_comida = st.selectbox("Segmento", ["Hamburgueria", "Pizzaria", "Japonesa", "Marmitaria", "Doceria", "Italiana"])
        
        st.divider()
        st.subheader("📅 Funcionamento")
        dias_semana = st.multiselect("Dias que Abre", ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"], default=["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"])
        horario = st.text_input("Horário (Ex: 18h às 23h)")
        entrega = st.text_input("Entrega (Ex: Grátis, R$ 5,00 ou iFood)")

        st.divider()
        destino = st.selectbox("Canal Principal", ["Instagram", "WhatsApp", "iFood", "Facebook Ads"])
        estilo = st.select_slider("Estilo da Escrita", options=["Descontraído", "Persuasivo", "Gourmet"])
        
        if st.button("Sair da Conta"):
            st.session_state.user = None
            st.rerun()

    tab_gerador, tab_estrategia = st.tabs(["🚀 Gerador de Legendas", "📊 Estratégia Evolutiva"])

    # --- ABA 1: GERADOR DE LEGENDAS ---
    with tab_gerador:
        num = st.number_input("Quantos produtos quer anunciar?", 1, 10, 1)
        itens = []
        for i in range(num):
            st.markdown(f'<div class="item-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([3, 1])
            with c1: n = st.text_input(f"Produto {i+1}", key=f"n{i}")
            with c2: p = st.text_input(f"Preço", key=f"p{i}")
            d = st.text_area(f"Descrição/Diferenciais", key=f"d{i}", height=70)
            if n: itens.append({"nome": n, "preco": p, "desc": d})
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("✨ GERAR LEGENDAS"):
            if restaurante and itens:
                with st.spinner("O Chef IA está a escrever..."):
                    try:
                        model = get_model()
                        lista_p = "".join([f"- {x['nome']} (R$ {x['preco']}): {x['desc']}\n" for x in itens])
                        dias_str = ", ".join(dias_semana)
                        
                        prompt = (f"Atue como redator de gastronomia. Gere legendas para o restaurante {restaurante}.\n"
                                  f"Dados: Abre em {dias_str} | Horário: {horario} | Entrega: {entrega}.\n"
                                  f"Canal: {destino} | Estilo: {estilo}.\n"
                                  f"Produtos:\n{lista_p}\n"
                                  f"Inclua CTAs claros e separe com '---SEPARAR---'.")
                        
                        res = model.generate_content(prompt)
                        legendas = [l.strip() for l in res.text.split('---SEPARAR---') if l.strip()]
                        
                        for idx, texto in enumerate(legendas):
                            st.markdown(f"### 📦 Legenda {idx+1}")
                            st.markdown(f'<div class="copy-area">{texto}</div>', unsafe_allow_html=True)
                            copy_button(texto, f"btn_leg_{idx}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Erro: {e}")
            else:
                st.warning("Preencha o nome do restaurante e adicione produtos!")

    # --- ABA 2: ESTRATÉGIA EVOLUTIVA ---
    with tab_estrategia:
        st.subheader("📊 Planeamento que não se repete")
        col_est1, col_est2 = st.columns(2)
        
        with col_est1:
            fase_mes = st.selectbox("Em que fase estamos?", [
                "Início do Mês (Novidades e Autoridade)",
                "Meio do Mês (Engajamento e Prova Social)",
                "Fim do Mês (Vendas Agressivas e Combos)",
                "Data Comemorativa / Evento Especial"
            ])
        
        with col_est2:
            ultimo_tema = st.text_input("O que postou na última semana? (Opcional)", placeholder="Ex: Promoção de pizza de 10 reais")

        if st.button("📅 GERAR ESTRATÉGIA DA SEMANA"):
            if restaurante:
                with st.spinner("Analisando tendências para o seu segmento..."):
                    try:
                        model = get_model()
                        dias_str = ", ".join(dias_semana)
                        
                        prompt_est = (
                            f"Você é um consultor de marketing especializado em {tipo_comida}.\n"
                            f"Crie um cronograma de 7 dias para o restaurante {restaurante}.\n"
                            f"Contexto: {fase_mes}.\n"
                            f"Horário de funcionamento: {horario} em {dias_str}.\n"
                            f"IMPORTANTE: Na semana passada postamos sobre: {ultimo_tema}. "
                            f"NÃO REPITA essa estratégia. Traga ideias novas, focadas em Reels e Stories interativos.\n"
                            f"Formate como um guia prático dia após dia."
                        )
                        
                        res = model.generate_content(prompt_est)
                        st.markdown('<div class="strategy-card">', unsafe_allow_html=True)
                        st.markdown(res.text)
                        st.markdown('</div>', unsafe_allow_html=True)
                        copy_button(res.text, "plan_evo")
                    except Exception as e:
                        st.error(f"Erro ao gerar plano: {e}")
            else:
                st.warning("Preencha o nome do restaurante no painel lateral.")
