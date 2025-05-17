import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import tempfile
from pathlib import Path
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

def criar_animacao():
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.close()
    
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
    
    rnh_extra_x = np.random.uniform(0.1, 0.3, n_rnh)
    rnh_extra_y = np.random.uniform(0.6, 0.9, n_rnh)
    
    rn_extra_x = np.random.uniform(0.7, 0.9, n_rn)
    rn_extra_y = np.random.uniform(0.6, 0.9, n_rn)
    
    rn_intra_x = np.array([])
    rn_intra_y = np.array([])
    
    rnh_intra_x = np.array([])
    rnh_intra_y = np.array([])
    
    particulas_rnh_extra = ax.scatter(rnh_extra_x, rnh_extra_y, color='red', s=50, alpha=0.7, label='RNH⁺ (Extracelular)')
    particulas_rn_extra = ax.scatter(rn_extra_x, rn_extra_y, color='blue', s=50, alpha=0.7, label='RN (Extracelular)')
    particulas_rn_intra = ax.scatter([], [], color='blue', s=50, alpha=0.7, label='RN (Intracelular)')
    particulas_rnh_intra = ax.scatter([], [], color='red', s=50, alpha=0.7, label='RNH⁺ (Intracelular)')
    
    seta1 = ax.add_patch(FancyArrowPatch((0.5, 0.7), (0.5, 0.6), 
                                         arrowstyle='->', mutation_scale=15, 
                                         color='black', linewidth=2))
    seta2 = ax.add_patch(FancyArrowPatch((0.5, 0.3), (0.5, 0.4), 
                                         arrowstyle='->', mutation_scale=15, 
                                         color='black', linewidth=2))
    
    canal_x = 0.4
    canal_y = 0.2
    canal = ax.add_patch(Rectangle((canal_x-0.05, canal_y-0.05), 0.1, 0.1, 
                                  facecolor='gray', edgecolor='black', alpha=0.7))
    texto_canal = ax.text(canal_x, canal_y-0.1, "Canal de Na⁺", ha='center', fontsize=8)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    
    ax.set_title(f"Mecanismo de Ação: {anestesico_selecionado} (pKa: {pKa})", fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=8)
    
    rn_atravessando = []
    
    def init():
        particulas_rnh_extra.set_offsets(np.column_stack((rnh_extra_x, rnh_extra_y)))
        particulas_rn_extra.set_offsets(np.column_stack((rn_extra_x, rn_extra_y)))
        particulas_rn_intra.set_offsets(np.empty((0, 2)))
        particulas_rnh_intra.set_offsets(np.empty((0, 2)))
        return (particulas_rnh_extra, particulas_rn_extra, 
                particulas_rn_intra, particulas_rnh_intra)
    
    def update(frame):
        nonlocal rn_atravessando, rn_intra_x, rn_intra_y, rnh_intra_x, rnh_intra_y
        
        rnh_extra_x += np.random.normal(0, 0.01, n_rnh)
        rnh_extra_y += np.random.normal(0, 0.01, n_rnh)
        
        rnh_extra_x = np.clip(rnh_extra_x, 0.05, 0.35)
        rnh_extra_y = np.clip(rnh_extra_y, 0.55, 0.95)
        
        particulas_rnh_extra.set_offsets(np.column_stack((rnh_extra_x, rnh_extra_y)))
        
        for i in range(len(rn_extra_x)):
            if i not in [r[0] for r in rn_atravessando]:
                rn_extra_x[i] += np.random.normal(0, 0.01)
                rn_extra_y[i] += np.random.normal(0, 0.01)
                
                rn_extra_x[i] = np.clip(rn_extra_x[i], 0.65, 0.95)
                rn_extra_y[i] = np.clip(rn_extra_y[i], 0.55, 0.95)
                
                if np.random.random() < 0.02 and len(rn_atravessando) < 3:
                    rn_atravessando.append((i, 0))
        
        new_rn_atravessando = []
        for idx, progresso in rn_atravessando:
            progresso += 0.05
            if progresso < 1:
                new_rn_atravessando.append((idx, progresso))
                rn_extra_y[idx] = 0.9 - progresso * 0.5
            else:
                if np.random.random() < 0.3:
                    rnh_intra_x = np.append(rnh_intra_x, rn_extra_x[idx])
                    rnh_intra_y = np.append(rnh_intra_y, 0.2)
                else:
                    rn_intra_x = np.append(rn_intra_x, rn_extra_x[idx])
                    rn_intra_y = np.append(rn_intra_y, 0.2)
                
                rn_extra_x[idx] = np.nan
                rn_extra_y[idx] = np.nan
        
        rn_atravessando = new_rn_atravessando
        
        for i in range(len(rn_intra_x)):
            rn_intra_x[i] += np.random.normal(0, 0.01)
            rn_intra_y[i] += np.random.normal(0, 0.01)
            
            rn_intra_x[i] = np.clip(rn_intra_x[i], 0.05, 0.95)
            rn_intra_y[i] = np.clip(rn_intra_y[i], 0.05, 0.45)
        
        for i in range(len(rnh_intra_x)):
            rnh_intra_x[i] += np.random.normal(0, 0.01)
            rnh_intra_y[i] += np.random.normal(0, 0.01)
            
            rnh_intra_x[i] = np.clip(rnh_intra_x[i], 0.05, 0.95)
            rnh_intra_y[i] = np.clip(rnh_intra_y[i], 0.05, 0.45)
            
            dist_canal = np.sqrt((rnh_intra_x[i] - canal_x)**2 + (rnh_intra_y[i] - canal_y)**2)
            if dist_canal < 0.1:
                dx = canal_x - rnh_intra_x[i]
                dy = canal_y - rnh_intra_y[i]
                rnh_intra_x[i] += dx * 0.1
                rnh_intra_y[i] += dy * 0.1
        
        particulas_rn_extra.set_offsets(np.column_stack((rn_extra_x, rn_extra_y)))
        particulas_rn_intra.set_offsets(np.column_stack((rn_intra_x, rn_intra_y)))
        particulas_rnh_intra.set_offsets(np.column_stack((rnh_intra_x, rnh_intra_y)))
        
        return (particulas_rnh_extra, particulas_rn_extra,
                particulas_rn_intra, particulas_rnh_intra)
    
    return fig, update, init

st.header("Animação do Mecanismo de Ação")

if st.button("Iniciar Animação"):
    with st.spinner("Gerando animação..."):
        fig, update, init = criar_animacao()
        ani = animation.FuncAnimation(fig, update, init_func=init, frames=100, interval=100, blit=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            temp_video_path = Path(f.name)
            ani.save(str(temp_video_path), fps=10, extra_args=['-vcodec', 'libx264'])

        st.video(str(temp_video_path))

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
