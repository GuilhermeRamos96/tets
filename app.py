import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, FancyArrowPatch
import matplotlib.patheffects as path_effects
from dados_anestesicos import anestesicos, calcular_base_livre

st.set_page_config(
    page_title="Simulador de Anestésicos Locais",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Simulador do Mecanismo de Ação de Anestésicos Locais")
st.markdown("""
Este simulador demonstra como os anestésicos locais exercem seu efeito bloqueador
nos canais de sódio, com base nas propriedades físico-químicas de cada agente.
""")

anestesico_selecionado = st.sidebar.selectbox(
    "Escolha um anestésico:",
    list(anestesicos.keys())
)

st.sidebar.subheader("Propriedades do Anestésico")
st.sidebar.markdown(f"""
- **Tipo:** {anestesicos[anestesico_selecionado]['tipo']}
- **pKa:** {anestesicos[anestesico_selecionado]['pKa']}
- **% Base (RN) em pH 7,4:** {anestesicos[anestesico_selecionado]['base_percent']}%
- **Início de ação:** {anestesicos[anestesico_selecionado]['inicio_acao']} minutos
""")

with st.sidebar.expander("Equação de Henderson-Hasselbalch"):
    st.markdown(r"""
    $$\% \text{base livre (RN)} = \frac{1}{1 + 10^{(pKa - pH)}} \times 100$$
    """)

pKa = anestesicos[anestesico_selecionado]['pKa']
pH = 7.4
base_percent_calculada = calcular_base_livre(pKa, pH)
acid_percent_calculada = 100 - base_percent_calculada
base_percent_tabela = anestesicos[anestesico_selecionado]['base_percent']

st.sidebar.subheader("Cálculos")
st.sidebar.markdown(f"""
**Usando a equação de Henderson-Hasselbalch:**
- % Base (RN) calculada: {base_percent_calculada:.2f}%
- % Ácido (RNH⁺) calculada: {acid_percent_calculada:.2f}%

**Valor da tabela:**
- % Base (RN): {base_percent_tabela}%
""")

def criar_imagem_estatica(etapa=1):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    cor_extracelular = '#ffcccc'
    cor_intracelular = '#ffffcc'
    cor_membrana = '#cc6666'
    
    ax.add_patch(Rectangle((0, 0.5), 1, 0.5, facecolor=cor_extracelular, edgecolor='black', alpha=0.8))
    ax.add_patch(Rectangle((0, 0), 1, 0.5, facecolor=cor_intracelular, edgecolor='black', alpha=0.8))
    ax.add_patch(Rectangle((0, 0.48), 1, 0.04, facecolor=cor_membrana, edgecolor='black', hatch='///', alpha=0.7))
    
    ax.text(0.5, 0.85, f"Extracelular (pH {pH})", ha='center', fontsize=12, fontweight='bold')
    ax.text(0.5, 0.25, f"Intracelular (pH {pH})", ha='center', fontsize=12, fontweight='bold')
    ax.text(0.5, 0.5, "Bainha do nervo", ha='center', fontsize=10, fontweight='bold', 
            color='white', path_effects=[path_effects.withStroke(linewidth=2, foreground='black')])
    
    base_percent = calcular_base_livre(pKa, pH)
    acid_percent = 100 - base_percent
    
    total_extracelular = 1000
    rn_extra = int(total_extracelular * (base_percent / 100))
    rnh_extra = total_extracelular - rn_extra
    
    proporcao_intra_extra = 0.25
    total_intracelular = int(total_extracelular * proporcao_intra_extra)
    rn_intra = int(total_intracelular * (base_percent / 100))
    rnh_intra = total_intracelular - rn_intra
    
    texto_rnh_extra = ax.text(0.2, 0.75, f"RNH⁺: {rnh_extra}\n({acid_percent:.1f}%)", ha='center', fontsize=10)
    texto_rn_extra = ax.text(0.8, 0.75, f"RN: {rn_extra}\n({base_percent:.1f}%)", ha='center', fontsize=10)
    texto_rnh_intra = ax.text(0.2, 0.15, f"RNH⁺: {rnh_intra}\n({acid_percent:.1f}%)", ha='center', fontsize=10)
    texto_rn_intra = ax.text(0.8, 0.15, f"RN: {rn_intra}\n({base_percent:.1f}%)", ha='center', fontsize=10)
    
    n_particulas = 20
    n_rn = int(n_particulas * (base_percent / 100))
    n_rnh = n_particulas - n_rn
    
    # Posições iniciais das partículas
    np.random.seed(42)  # Para reprodutibilidade
    
    # RNH+ no extracelular (não atravessa a membrana)
    rnh_extra_x = np.random.uniform(0.1, 0.3, n_rnh)
    rnh_extra_y = np.random.uniform(0.6, 0.9, n_rnh)
    
    # RN no extracelular (atravessa a membrana)
    rn_extra_x = np.random.uniform(0.7, 0.9, n_rn)
    rn_extra_y = np.random.uniform(0.6, 0.9, n_rn)
    
    # Partículas no intracelular (inicialmente vazias)
    rn_intra_x = np.array([])
    rn_intra_y = np.array([])
    
    rnh_intra_x = np.array([])
    rnh_intra_y = np.array([])
    
    # Etapa 1: Estado inicial
    if etapa >= 1:
        ax.scatter(rnh_extra_x, rnh_extra_y, color='red', s=50, alpha=0.7, label='RNH⁺ (Extracelular)')
        ax.scatter(rn_extra_x, rn_extra_y, color='blue', s=50, alpha=0.7, label='RN (Extracelular)')
    
    # Etapa 2: RN começa a atravessar a membrana
    if etapa >= 2:
        # Selecionar algumas partículas RN para atravessar
        n_atravessando = min(3, n_rn)
        for i in range(n_atravessando):
            # Posicionar na membrana
            ax.scatter(rn_extra_x[i], 0.5, color='blue', s=50, alpha=0.7)
            # Remover da posição original
            rn_extra_x[i] = np.nan
            rn_extra_y[i] = np.nan
        
        # Atualizar o gráfico de RN no extracelular
        ax.scatter(rn_extra_x, rn_extra_y, color='blue', s=50, alpha=0.7)
        
        # Adicionar seta indicando movimento
        ax.add_patch(FancyArrowPatch((0.5, 0.7), (0.5, 0.6), 
                                    arrowstyle='->', mutation_scale=15, 
                                    color='black', linewidth=2))
    
    # Etapa 3: RN chega ao intracelular
    if etapa >= 3:
        # Adicionar RN no intracelular
        rn_intra_x = np.array([0.7, 0.8, 0.75])
        rn_intra_y = np.array([0.2, 0.3, 0.25])
        ax.scatter(rn_intra_x, rn_intra_y, color='blue', s=50, alpha=0.7, label='RN (Intracelular)')
    
    # Etapa 4: RN se converte parcialmente em RNH+ no intracelular
    if etapa >= 4:
        # Converter algumas partículas RN em RNH+
        rnh_intra_x = np.array([0.3, 0.2])
        rnh_intra_y = np.array([0.2, 0.3])
        ax.scatter(rnh_intra_x, rnh_intra_y, color='red', s=50, alpha=0.7, label='RNH⁺ (Intracelular)')
        
        # Remover algumas partículas RN (convertidas)
        rn_intra_x = np.array([0.75])
        rn_intra_y = np.array([0.25])
        ax.scatter(rn_intra_x, rn_intra_y, color='blue', s=50, alpha=0.7)
    
    # Etapa 5: RNH+ bloqueia o canal de sódio
    if etapa >= 5:
        # Adicionar canal de sódio
        canal_x = 0.4
        canal_y = 0.2
        ax.add_patch(Rectangle((canal_x-0.05, canal_y-0.05), 0.1, 0.1, 
                              facecolor='gray', edgecolor='black', alpha=0.7))
        ax.text(canal_x, canal_y-0.1, "Canal de Na⁺", ha='center', fontsize=8)
        
        # Mover RNH+ para o canal
        rnh_intra_x = np.array([0.4, 0.38])
        rnh_intra_y = np.array([0.2, 0.22])
        ax.scatter(rnh_intra_x, rnh_intra_y, color='red', s=50, alpha=0.7)
        
        # Adicionar seta indicando bloqueio
        ax.add_patch(FancyArrowPatch((0.3, 0.3), (0.38, 0.22), 
                                    arrowstyle='->', mutation_scale=15, 
                                    color='black', linewidth=2))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    
    titulo = f"Mecanismo de Ação: {anestesico_selecionado} (pKa: {pKa})"
    if etapa == 1:
        titulo += " - Estado Inicial"
    elif etapa == 2:
        titulo += " - RN Atravessa a Membrana"
    elif etapa == 3:
        titulo += " - RN Chega ao Intracelular"
    elif etapa == 4:
        titulo += " - RN se Converte em RNH⁺"
    elif etapa == 5:
        titulo += " - RNH⁺ Bloqueia o Canal de Na⁺"
    
    ax.set_title(titulo, fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=8)
    
    return fig

st.header("Visualização do Mecanismo de Ação")

etapa = st.slider("Etapa do mecanismo:", 1, 5, 1)
descricoes = [
    "Estado inicial: Distribuição das formas RN e RNH⁺ no meio extracelular",
    "RN atravessa a membrana da bainha do nervo",
    "RN chega ao meio intracelular",
    "RN se converte parcialmente em RNH⁺ no meio intracelular",
    "RNH⁺ bloqueia o canal de sódio"
]

st.caption(descricoes[etapa-1])
fig = criar_imagem_estatica(etapa)
st.pyplot(fig)

st.header("Explicação do Mecanismo de Ação")
st.markdown(f"""
### Como funciona o anestésico local {anestesico_selecionado}:

1. **Equilíbrio ácido-base no meio extracelular (pH 7,4)**:
   - O anestésico existe em duas formas: ionizada (RNH⁺) e não-ionizada (RN)
   - Com pKa de {pKa}, aproximadamente {anestesicos[anestesico_selecionado]['base_percent']}% está na forma de base livre (RN)

2. **Travessia da membrana**:
   - Apenas a forma não-ionizada (RN) consegue atravessar a membrana lipídica
   - Quanto maior a proporção de RN, mais rápida é a penetração no nervo

3. **Reequilíbrio no meio intracelular (pH 7,4)**:
   - No interior da célula, o anestésico se reequilibra nas formas RN e RNH⁺
   - A forma ionizada (RNH⁺) é a responsável pelo bloqueio dos canais de sódio

4. **Bloqueio do canal de sódio**:
   - RNH⁺ se liga ao receptor no canal de sódio, bloqueando-o
   - Isso impede a propagação do potencial de ação
   - Resulta em bloqueio da condução nervosa e anestesia local
""")
