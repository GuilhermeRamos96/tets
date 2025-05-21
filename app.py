import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle, Ellipse
import matplotlib.patheffects as path_effects
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches

# Assumindo que o arquivo dados_anestesicos.py existe
try:
    from dados_anestesicos import anestesicos, calcular_base_livre
except ImportError:
    # Definição de backup caso o arquivo não exista
    def calcular_base_livre(pKa, pH):
        return 100 / (1 + 10**(pKa - pH))
    
    anestesicos = {
        "Lidocaína": {
            "tipo": "Amida",
            "pKa": 7.9,
            "base_percent": 24,
            "inicio_acao": "2-5"
        },
        "Bupivacaína": {
            "tipo": "Amida",
            "pKa": 8.1,
            "base_percent": 17,
            "inicio_acao": "5-8"
        },
        "Procaína": {
            "tipo": "Éster",
            "pKa": 8.9,
            "base_percent": 3,
            "inicio_acao": "6-10"
        }
    }

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

def criar_imagem_mecanismo():
    # Usar figsize fixo
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Cores
    cor_extracelular = '#f0f8ff'  # Azul claro para meio extracelular
    cor_intracelular = '#fffacd'  # Amarelo claro para meio intracelular
    cor_membrana_externa = '#87cefa'  # Azul para cabeças polares externas
    cor_membrana_interna = '#87cefa'  # Azul para cabeças polares internas
    cor_membrana_lipidica = '#ffa07a'  # Laranja para caudas lipídicas
    
    # Desenhar meio extracelular e intracelular
    ax.add_patch(Rectangle((0, 0.5), 1, 0.5, facecolor=cor_extracelular, edgecolor='black', alpha=0.8))
    ax.add_patch(Rectangle((0, 0), 1, 0.5, facecolor=cor_intracelular, edgecolor='black', alpha=0.8))
    
    # Desenhar a bicamada lipídica (bainha do nervo) com estrutura mais detalhada
    # Camada externa (cabeças polares)
    for i in np.arange(0.05, 0.95, 0.05):
        ax.add_patch(Circle((i, 0.5), 0.02, facecolor=cor_membrana_externa, edgecolor='black', alpha=0.9))
    
    # Camada interna (cabeças polares)
    for i in np.arange(0.05, 0.95, 0.05):
        ax.add_patch(Circle((i, 0.4), 0.02, facecolor=cor_membrana_interna, edgecolor='black', alpha=0.9))
    
    # Caudas lipídicas entre as camadas
    for i in np.arange(0.05, 0.95, 0.05):
        ax.add_patch(Rectangle((i-0.015, 0.42), 0.03, 0.06, facecolor=cor_membrana_lipidica, edgecolor='none', alpha=0.8))
    
    # Adicionar canais de sódio na membrana (bainha do nervo)
    canal_positions = [0.2, 0.5, 0.8]
    for pos in canal_positions:
        if pos != 0.5:  # Canais normais
            ax.add_patch(Rectangle((pos-0.03, 0.42), 0.06, 0.08, facecolor='#d3d3d3', edgecolor='black', alpha=0.9))
            ax.text(pos, 0.38, "Na⁺", ha='center', fontsize=8, fontweight='bold')
        else:  # Canal bloqueado
            ax.add_patch(Rectangle((pos-0.03, 0.42), 0.06, 0.08, 
                                  facecolor='#ff6347', edgecolor='black', alpha=0.7))
            ax.text(pos, 0.38, "Na⁺\nBloqueado", ha='center', fontsize=8, fontweight='bold')
            # Adicionar símbolo de bloqueio (X) sobre o canal
            ax.text(pos, 0.46, "✕", ha='center', va='center', fontsize=12, 
                    color='black', fontweight='bold')
    
    # Adicionar legendas para as regiões
    ax.text(0.5, 0.85, f"Extracelular (pH {pH})", ha='center', fontsize=12, fontweight='bold')
    ax.text(0.5, 0.25, f"Intracelular (pH {pH})", ha='center', fontsize=12, fontweight='bold')
    ax.text(0.5, 0.45, "Bainha do nervo", ha='center', fontsize=10, fontweight='bold', 
            color='black', path_effects=[path_effects.withStroke(linewidth=2, foreground='white')])
    
    # Calcular proporções de base/ácido
    base_percent = calcular_base_livre(pKa, pH)
    acid_percent = 100 - base_percent
    
    # Informações sobre concentrações
    total_extracelular = 1000
    rn_extra = int(total_extracelular * (base_percent / 100))
    rnh_extra = total_extracelular - rn_extra
    
    proporcao_intra_extra = 0.25
    total_intracelular = int(total_extracelular * proporcao_intra_extra)
    rn_intra = int(total_intracelular * (base_percent / 100))
    rnh_intra = total_intracelular - rn_intra
    
    # Textos informativos
    texto_rnh_extra = ax.text(0.2, 0.75, f"RNH⁺: {rnh_extra}\n({acid_percent:.1f}%)", ha='center', fontsize=10)
    texto_rn_extra = ax.text(0.8, 0.75, f"RN: {rn_extra}\n({base_percent:.1f}%)", ha='center', fontsize=10)
    texto_rnh_intra = ax.text(0.2, 0.15, f"RNH⁺: {rnh_intra}\n({acid_percent:.1f}%)", ha='center', fontsize=10)
    texto_rn_intra = ax.text(0.8, 0.15, f"RN: {rn_intra}\n({base_percent:.1f}%)", ha='center', fontsize=10)
    
    # Adicionar partículas
    # RNH+ no extracelular
    rnh_extra_x = np.array([0.15, 0.25, 0.18, 0.22])
    rnh_extra_y = np.array([0.7, 0.8, 0.65, 0.75])
    ax.scatter(rnh_extra_x, rnh_extra_y, color='red', s=50, alpha=0.7)
    
    # RN no extracelular
    rn_extra_x = np.array([0.75, 0.85, 0.78, 0.82])
    rn_extra_y = np.array([0.7, 0.8, 0.65, 0.75])
    ax.scatter(rn_extra_x, rn_extra_y, color='blue', s=50, alpha=0.7)
    
    # RN atravessando a membrana
    ax.scatter([0.65], [0.45], color='blue', s=50, alpha=0.7)
    
    # RN no intracelular
    rn_intra_x = np.array([0.7, 0.8, 0.75])
    rn_intra_y = np.array([0.2, 0.3, 0.25])
    ax.scatter(rn_intra_x, rn_intra_y, color='blue', s=50, alpha=0.7)
    
    # RNH+ no intracelular
    rnh_intra_x = np.array([0.3, 0.2])
    rnh_intra_y = np.array([0.2, 0.3])
    ax.scatter(rnh_intra_x, rnh_intra_y, color='red', s=50, alpha=0.7)
    
    # RNH+ bloqueando o canal
    canal_alvo_x = 0.5
    rnh_bloqueio_x = np.array([canal_alvo_x-0.01, canal_alvo_x+0.01])
    rnh_bloqueio_y = np.array([0.45, 0.45])
    ax.scatter(rnh_bloqueio_x, rnh_bloqueio_y, color='red', s=50, alpha=0.7)
    
    # Adicionar setas indicando movimento
    # RN atravessando a membrana
    ax.add_patch(FancyArrowPatch((0.7, 0.6), (0.65, 0.5), 
                                arrowstyle='->', mutation_scale=15, 
                                color='black', linewidth=2))
    
    # RNH+ bloqueando o canal
    ax.add_patch(FancyArrowPatch((0.3, 0.3), (0.5, 0.45), 
                                arrowstyle='->', mutation_scale=15, 
                                color='black', linewidth=2))
    
    # Legenda personalizada
    handles = [
        mpatches.Patch(color='blue', alpha=0.7, label='RN (Base livre)'),
        mpatches.Patch(color='red', alpha=0.7, label='RNH⁺ (Forma ionizada)'),
        mpatches.Patch(color='#d3d3d3', alpha=0.9, label='Canal de Na⁺'),
        mpatches.Patch(color='#ff6347', alpha=0.7, label='Canal de Na⁺ Bloqueado')
    ]
    ax.legend(handles=handles, loc='upper right', fontsize=8)
    
    # Configurações do gráfico
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Título
    titulo = f"Mecanismo de Ação: {anestesico_selecionado} (pKa: {pKa})"
    ax.set_title(titulo, fontsize=14, fontweight='bold')
    
    # Adicionar nota de referência
    ax.text(0.02, 0.02, "Baseado em: Mecanismo de ação dos anestésicos locais. Adaptado para fins educacionais.", 
            fontsize=6, style='italic')
    
    # Garantir que o tamanho da figura seja consistente
    fig.tight_layout(pad=1.0)
    
    return fig

st.header("Visualização do Mecanismo de Ação")

# Exibir apenas a imagem final (etapa 5)
fig = criar_imagem_mecanismo()
st.pyplot(fig)

st.header("Explicação do Mecanismo de Ação")
st.markdown(f"""
### Como funciona o anestésico local {anestesico_selecionado}:

1. **Equilíbrio ácido-base no meio extracelular (pH 7,4)**:
   - O anestésico existe em duas formas: ionizada (RNH⁺) e não-ionizada (RN)
   - Com pKa de {pKa}, aproximadamente {anestesicos[anestesico_selecionado]['base_percent']}% está na forma de base livre (RN)

2. **Travessia da membrana**:
   - Apenas a forma não-ionizada (RN) consegue atravessar a membrana lipídica da bainha do nervo
   - Quanto maior a proporção de RN, mais rápida é a penetração no nervo

3. **Reequilíbrio no meio intracelular (pH 7,4)**:
   - No interior da célula, o anestésico se reequilibra nas formas RN e RNH⁺
   - A forma ionizada (RNH⁺) é a responsável pelo bloqueio dos canais de sódio

4. **Bloqueio do canal de sódio**:
   - RNH⁺ se move em direção ao canal de sódio localizado na bainha do nervo
   - RNH⁺ se liga ao receptor no canal de sódio, bloqueando-o
   - Isso impede a propagação do potencial de ação
   - Resulta em bloqueio da condução nervosa e anestesia local

**Referência bibliográfica:**
RANG, H.P.; DALE, M.M.; RITTER, J.M.; FLOWER, R.J.; HENDERSON, G. Farmacologia. 8. ed. Rio de Janeiro: Elsevier, 2016.
""")
