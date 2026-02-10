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
st.set_page_config(page_title="ChefPost Pro 2026", page_icon="🥘", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .item-card { background-color: rgba(255, 75, 43, 0.05); padding: 20px; border-radius: 15px; border: 1px solid #FF4B2B; margin-bottom: 20px; }
    .copy-area { background: #161b22; color: #c9d1d9; padding: 15px; border-radius: 8px; font-family: sans-serif; white-space: pre-wrap; margin-bottom: 10px; border: 1px solid #30363d; }
    .stButton>button { background: linear-gradient(90deg, #FF4B2B 0%, #FF416C 100%); color: white !important; font-weight: bold; border-radius: 10px; height: 50px; width: 100%; border: none; }
    .strategy-card { background-color: #1e252e; padding: 20px; border-radius: 10px; border-left: 5px solid #25D366; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNÇÕES ---
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

# --- 5. LOGIN (Simplificado para o exemplo) ---
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
    # --- 6. PAINEL LATERAL ---
    with st.sidebar:
        st.header("👨‍🍳 Configurações")
        restaurante = st.text_input("Nome do Restaurante", placeholder="Ex: Pizzaria Gourmet")
        tipo_comida = st.selectbox("Tipo de Cozinha", ["Hamburgueria", "Pizzaria", "Japonesa", "Marmitaria", "Doceria", "Italiana"])
        st.divider()
        estilo = st.select_slider("Estilo da Escrita", options=["Descontraído", "Persuasivo", "Gourmet"])
        if st.button("Sair"):
            st.session_state.user = None
            st.rerun()

    # --- 7. ABAS PRINCIPAIS ---
    tab_gerador, tab_estrategia = st.tabs(["🚀 Gerador de Legendas", "📊 Estratégia & Tráfego"])

    with tab_gerador:
        st.subheader("Crie legendas para seus produtos")
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

       if st.button("✨ GERAR LEGENDAS"):
        if restaurante and itens:
            with st.spinner("Chef IA preparando suas legendas..."):
                try:
                    model = genai.GenerativeModel('gemini-3-flash-preview')
                    
                    # Montamos um único pedido para a IA não travar por excesso de requisições
                    lista_produtos = "".join([f"- {x['nome']} (R$ {x['preco']}): {x['desc']}\n" for x in itens])
                    
                    prompt = (
                        f"Você é um copywriter gourmet. Gere legendas INDIVIDUAIS para cada produto abaixo do restaurante {restaurante}. "
                        f"Estilo: {estilo}. Canal: {destino}. Taxa: {taxa}. Tempo: {tempo}.\n"
                        f"Produtos:\n{lista_produtos}\n"
                        f"IMPORTANTE: Separe cada legenda com o marcador '---PRODUTO---'. Não misture os textos."
                    )
                    
                    res = model.generate_content(prompt)
                    # Separamos o texto da IA usando o marcador que pedimos
                    legendas_separadas = res.text.split('---PRODUTO---')
                    
                    # Limpamos espaços vazios da lista
                    legendas_separadas = [l.strip() for l in legendas_separadas if l.strip()]

                    st.divider()
                    
                    for idx, texto_legenda in enumerate(legendas_separadas):
                        # Tentamos pegar o nome do produto para o título, se não houver, usamos o índice
                        nome_display = itens[idx]['nome'] if idx < len(itens) else f"Sugestão {idx+1}"
                        
                        st.markdown(f"### 📦 {nome_display}")
                        st.markdown(f'<div class="copy-area">{texto_legenda}</div>', unsafe_allow_html=True)
                        copy_button(texto_legenda, f"leg_{idx}")
                        st.divider()

                    st.balloons()
                except Exception as e:
                    st.error(f"Eita! A API está ocupada. Tente novamente em 10 segundos. Erro: {e}")
            if st.button("📅 GERAR CALENDÁRIO DA SEMANA"):
                if restaurante:
                    with st.spinner("Criando seu plano de postagens..."):
                        model = genai.GenerativeModel('gemini-3-flash-preview')
                        prompt = f"Crie um calendário de postagens de 7 dias para um(a) {tipo_comida} chamado {restaurante}. Sugira o tema do post e a legenda para cada dia."
                        res = model.generate_content(prompt)
                        st.markdown('<div class="strategy-card">', unsafe_allow_html=True)
                        st.markdown(res.text)
                        st.markdown('</div>', unsafe_allow_html=True)
                        copy_button(res.text, "cal_sem")
                else: st.warning("Digite o nome do restaurante no painel lateral.")

        with c2:
            if st.button("📢 SUGERIR PÚBLICO PARA ANÚNCIOS"):
                if restaurante:
                    with st.spinner("Analisando seu público ideal..."):
                        model = genai.GenerativeModel('gemini-3-flash-preview')
                        prompt = f"Sugira a configuração de público para anúncios no Facebook/Instagram Ads para um(a) {tipo_comida}. Inclua interesses, raio de distância e o tipo de criativo que mais converte."
                        res = model.generate_content(prompt)
                        st.markdown('<div class="strategy-card" style="border-left-color: #FF4B2B;">', unsafe_allow_html=True)
                        st.markdown(res.text)
                        st.markdown('</div>', unsafe_allow_html=True)
                        copy_button(res.text, "ads_sug")
                else: st.warning("Digite o nome do restaurante no painel lateral.")
