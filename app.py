import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import time
import tempfile
from pathlib import Path
from matplotlib.patches import Rectangle, Arrow, FancyArrowPatch
import matplotlib.patheffects as path_effects
from matplotlib.colors import LinearSegmentedColormap
from dados_anestesicos import anestesicos, esquema_distribuicao, calcular_base_livre

# Configuração da página Streamlit
st.set_page_config(
    page_title="Simulador de Anestésicos Locais",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título e introdução
st.title("Simulador do Mecanismo de Ação de Anestésicos Locais")
st.markdown("""
Este simulador interativo demonstra como os anestésicos locais exercem seu efeito bloqueador
nos canais de sódio, com base nas propriedades físico-químicas de cada agente.

A eficácia de um anestésico local depende de vários fatores, incluindo seu pKa, que determina
a proporção entre as formas ionizada (RNH⁺) e não-ionizada (RN) em determinado pH.
Apenas a forma não-ionizada (RN) consegue atravessar a membrana lipídica da bainha do nervo.
""")

# Sidebar para seleção do anestésico
st.sidebar.header("Selecione o Anestésico Local")
anestesico_selecionado = st.sidebar.selectbox(
    "Escolha um anestésico:",
    list(anestesicos.keys())
)

# Exibir propriedades do anestésico selecionado
st.sidebar.subheader("Propriedades do Anestésico")
st.sidebar.markdown(f"""
- **Tipo:** {anestesicos[anestesico_selecionado]['tipo']}
- **pKa:** {anestesicos[anestesico_selecionado]['pKa']}
- **% Base (RN) em pH 7,4:** {anestesicos[anestesico_selecionado]['base_percent']}%
- **Início de ação:** {anestesicos[anestesico_selecionado]['inicio_acao']} minutos
""")

# Explicação da equação de Henderson-Hasselbalch
with st.sidebar.expander("Equação de Henderson-Hasselbalch"):
    st.markdown(r"""
    A porcentagem de base livre (RN) é calculada usando a equação:
    
    $$\% \text{base livre (RN)} = \frac{1}{1 + 10^{(pKa - pH)}} \times 100$$
    
    Onde:
    - pKa é a constante de dissociação do anestésico
    - pH é o pH do meio (7,4 para o meio fisiológico)
    """)

# Calcular a porcentagem real de base livre usando a equação
pKa = anestesicos[anestesico_selecionado]['pKa']
pH = 7.4
base_percent_calculada = calcular_base_livre(pKa, pH)
acid_percent_calculada = 100 - base_percent_calculada

# Comparar com o valor da tabela
base_percent_tabela = anestesicos[anestesico_selecionado]['base_percent']

# Exibir os cálculos
st.sidebar.subheader("Cálculos")
st.sidebar.markdown(f"""
**Usando a equação de Henderson-Hasselbalch:**
- % Base (RN) calculada: {base_percent_calculada:.2f}%
- % Ácido (RNH⁺) calculada: {acid_percent_calculada:.2f}%

**Valor da tabela:**
- % Base (RN): {base_percent_tabela}%
""")

# Função para criar a animação
def criar_animacao():
    # Configuração da figura
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.close()  # Fechamos a figura para não exibi-la duas vezes
    
    # Cores
    cor_extracelular = '#ffcccc'  # Rosa claro
    cor_intracelular = '#ffffcc'  # Amarelo claro
    cor_membrana = '#cc6666'      # Vermelho escuro
    
    # Desenhar os compartimentos
    ax.add_patch(Rectangle((0, 0.5), 1, 0.5, facecolor=cor_extracelular, edgecolor='black', alpha=0.8))
    ax.add_patch(Rectangle((0, 0), 1, 0.5, facecolor=cor_intracelular, edgecolor='black', alpha=0.8))
    
    # Desenhar a membrana
    ax.add_patch(Rectangle((0, 0.48), 1, 0.04, facecolor=cor_membrana, edgecolor='black', hatch='///', alpha=0.7))
    
    # Textos dos compartimentos
    ax.text(0.5, 0.85, f"Extracelular (pH {pH})", ha='center', fontsize=12, fontweight='bold')
    ax.text(0.5, 0.25, f"Intracelular (pH {pH})", ha='center', fontsize=12, fontweight='bold')
    ax.text(0.5, 0.5, "Bainha do nervo", ha='center', fontsize=10, fontweight='bold', 
            color='white', path_effects=[path_effects.withStroke(linewidth=2, foreground='black')])
    
    # Calcular as quantidades de RN e RNH+ com base no pKa do anestésico selecionado
    base_percent = calcular_base_livre(pKa, pH)
    acid_percent = 100 - base_percent
    
    # Normalizar para manter a proporção total de 1000 moléculas no extracelular
    total_extracelular = 1000
    rn_extra = int(total_extracelular * (base_percent / 100))
    rnh_extra = total_extracelular - rn_extra
    
    # Proporção intracelular (aproximadamente 25% do total extracelular)
    proporcao_intra_extra = 0.25
    total_intracelular = int(total_extracelular * proporcao_intra_extra)
    rn_intra = int(total_intracelular * (base_percent / 100))
    rnh_intra = total_intracelular - rn_intra
    
    # Textos das quantidades iniciais
    texto_rnh_extra = ax.text(0.2, 0.75, f"RNH⁺: {rnh_extra}\n({acid_percent:.1f}%)", ha='center', fontsize=10)
    texto_rn_extra = ax.text(0.8, 0.75, f"RN: {rn_extra}\n({base_percent:.1f}%)", ha='center', fontsize=10)
    texto_rnh_intra = ax.text(0.2, 0.15, f"RNH⁺: {rnh_intra}\n({acid_percent:.1f}%)", ha='center', fontsize=10)
    texto_rn_intra = ax.text(0.8, 0.15, f"RN: {rn_intra}\n({base_percent:.1f}%)", ha='center', fontsize=10)
    
    # Criar partículas para animação
    n_particulas = 20  # Número de partículas para animação
    
    # Proporção de partículas RN vs RNH+ baseada no pKa
    n_rn = int(n_particulas * (base_percent / 100))
    n_rnh = n_particulas - n_rn
    
    # Posições iniciais das partículas
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
    
    # Criar os objetos de partículas
    particulas_rnh_extra = ax.scatter(rnh_extra_x, rnh_extra_y, color='red', s=50, alpha=0.7, label='RNH⁺ (Extracelular)')
    particulas_rn_extra = ax.scatter(rn_extra_x, rn_extra_y, color='blue', s=50, alpha=0.7, label='RN (Extracelular)')
    particulas_rn_intra = ax.scatter([], [], color='blue', s=50, alpha=0.7, label='RN (Intracelular)')
    particulas_rnh_intra = ax.scatter([], [], color='red', s=50, alpha=0.7, label='RNH⁺ (Intracelular)')
    
    # Setas para indicar direção do movimento
    seta1 = ax.add_patch(FancyArrowPatch((0.5, 0.7), (0.5, 0.6), 
                                         arrowstyle='->', mutation_scale=15, 
                                         color='black', linewidth=2))
    seta2 = ax.add_patch(FancyArrowPatch((0.5, 0.3), (0.5, 0.4), 
                                         arrowstyle='->', mutation_scale=15, 
                                         color='black', linewidth=2))
    
    # Adicionar canal de sódio no intracelular
    canal_x = 0.4
    canal_y = 0.2
    canal = ax.add_patch(Rectangle((canal_x-0.05, canal_y-0.05), 0.1, 0.1, 
                                  facecolor='gray', edgecolor='black', alpha=0.7))
    texto_canal = ax.text(canal_x, canal_y-0.1, "Canal de Na⁺", ha='center', fontsize=8)
    
    # Configurações do gráfico
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Título com o nome do anestésico
    titulo = ax.set_title(f"Mecanismo de Ação: {anestesico_selecionado} (pKa: {pKa})", fontsize=14, fontweight='bold')
    
    # Legenda
    ax.legend(loc='upper right', fontsize=8)
    
    # Variáveis para controlar a animação
    rn_atravessando = []  # Lista para armazenar partículas RN que estão atravessando a membrana
    
    # Função de inicialização da animação
    def init():
        particulas_rnh_extra.set_offsets(np.column_stack((rnh_extra_x, rnh_extra_y)))
        particulas_rn_extra.set_offsets(np.column_stack((rn_extra_x, rn_extra_y)))
        particulas_rn_intra.set_offsets(np.empty((0, 2)))
        particulas_rnh_intra.set_offsets(np.empty((0, 2)))
        return (particulas_rnh_extra, particulas_rn_extra, 
                particulas_rn_intra, particulas_rnh_intra)
    
    # Função de atualização da animação
    def update(frame):
        nonlocal rn_atravessando, rn_intra_x, rn_intra_y, rnh_intra_x, rnh_intra_y
        
        # Movimento aleatório das partículas RNH+ no extracelular (não atravessam a membrana)
        rnh_extra_x += np.random.normal(0, 0.01, n_rnh)
        rnh_extra_y += np.random.normal(0, 0.01, n_rnh)
        
        # Manter as partículas dentro dos limites do extracelular
        rnh_extra_x = np.clip(rnh_extra_x, 0.05, 0.35)
        rnh_extra_y = np.clip(rnh_extra_y, 0.55, 0.95)
        
        # Atualizar posições das partículas RNH+ no extracelular
        particulas_rnh_extra.set_offsets(np.column_stack((rnh_extra_x, rnh_extra_y)))
        
        # Movimento das partículas RN no extracelular
        for i in range(len(rn_extra_x)):
            # Se a partícula não está atravessando a membrana
            if i not in [r[0] for r in rn_atravessando]:
                # Movimento aleatório
                rn_extra_x[i] += np.random.normal(0, 0.01)
                rn_extra_y[i] += np.random.normal(0, 0.01)
                
                # Manter dentro dos limites do extracelular
                rn_extra_x[i] = np.clip(rn_extra_x[i], 0.65, 0.95)
                rn_extra_y[i] = np.clip(rn_extra_y[i], 0.55, 0.95)
                
                # Probabilidade de começar a atravessar a membrana
                if np.random.random() < 0.02 and len(rn_atravessando) < 3:
                    rn_atravessando.append((i, 0))  # (índice, progresso)
        
        # Atualizar partículas RN que estão atravessando a membrana
        new_rn_atravessando = []
        for idx, progresso in rn_atravessando:
            progresso += 0.05
            if progresso < 1:
                # Ainda atravessando
                new_rn_atravessando.append((idx, progresso))
                # Atualizar posição (movimento vertical através da membrana)
                rn_extra_y[idx] = 0.9 - progresso * 0.5
            else:
                # Terminou de atravessar, mover para o intracelular
                # Probabilidade de conversão para RNH+ no intracelular
                if np.random.random() < 0.3:
                    rnh_intra_x = np.append(rnh_intra_x, rn_extra_x[idx])
                    rnh_intra_y = np.append(rnh_intra_y, 0.2)
                else:
                    rn_intra_x = np.append(rn_intra_x, rn_extra_x[idx])
                    rn_intra_y = np.append(rn_intra_y, 0.2)
        
        rn_atravessando = new_rn_atravessando
        
        # Movimento aleatório das partículas RN no intracelular
        for i in range(len(rn_intra_x)):
            rn_intra_x[i] += np.random.normal(0, 0.01)
            rn_intra_y[i] += np.random.normal(0, 0.01)
            
            # Manter dentro dos limites do intracelular
            rn_intra_x[i] = np.clip(rn_intra_x[i], 0.05, 0.95)
            rn_intra_y[i] = np.clip(rn_intra_y[i], 0.05, 0.45)
        
        # Movimento aleatório das partículas RNH+ no intracelular
        for i in range(len(rnh_intra_x)):
            rnh_intra_x[i] += np.random.normal(0, 0.01)
            rnh_intra_y[i] += np.random.normal(0, 0.01)
            
            # Manter dentro dos limites do intracelular
            rnh_intra_x[i] = np.clip(rnh_intra_x[i], 0.05, 0.95)
            rnh_intra_y[i] = np.clip(rnh_intra_y[i], 0.05, 0.45)
            
            # Verificar se está próximo ao canal de sódio
            dist_canal = np.sqrt((rnh_intra_x[i] - canal_x)**2 + (rnh_intra_y[i] - canal_y)**2)
            if dist_canal < 0.1:
                # Atrair para o canal (bloqueio)
                dx = canal_x - rnh_intra_x[i]
                dy = canal_y - rnh_intra_y[i]
                rnh_intra_x[i] += dx * 0.1
                rnh_intra_y[i] += dy * 0.1
        
        # Atualizar os scatters com as novas posições
        particulas_rn_extra.set_offsets(np.column_stack((rn_extra_x, rn_extra_y)))
        
        if len(rn_intra_x) > 0:
            particulas_rn_intra.set_offsets(np.column_stack((rn_intra_x, rn_intra_y)))
        else:
            particulas_rn_intra.set_offsets(np.empty((0, 2)))
            
        if len(rnh_intra_x) > 0:
            particulas_rnh_intra.set_offsets(np.column_stack((rnh_intra_x, rnh_intra_y)))
        else:
            particulas_rnh_intra.set_offsets(np.empty((0, 2)))
        
        return (particulas_rnh_extra, particulas_rn_extra,
                particulas_rn_intra, particulas_rnh_intra)
    
    # Criar a animação
    ani = animation.FuncAnimation(
        fig, update, init_func=init, frames=100, interval=100, blit=True
    )
    
    # Salvar como GIF temporário
    temp_dir = tempfile.mkdtemp()
    gif_path = Path(temp_dir) / "animacao.gif"
    ani.save(str(gif_path), writer="pillow", fps=10)
    
    return gif_path

# Exibir a animação no Streamlit
st.header("Animação do Mecanismo de Ação")
with st.spinner("Gerando animação... (isso pode levar alguns segundos)"):
    gif_path = criar_animacao()
    st.image(str(gif_path), caption=f"Mecanismo de ação do {anestesico_selecionado}: RN atravessa a membrana e se converte em RNH⁺ no interior da célula")

# Explicação do mecanismo de ação
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

# Relação entre pKa e início de ação
st.header("Relação entre pKa e Início de Ação")
st.markdown(f"""
O **pKa** de um anestésico local é um fator determinante para seu início de ação:

- **pKa baixo** (como Benzocaína, pKa = 3,5):
  - Maior proporção na forma não-ionizada (RN) em pH fisiológico
  - Atravessa mais rapidamente a membrana
  - Início de ação mais rápido

- **pKa alto** (como Procaína, pKa = 9,1):
  - Menor proporção na forma não-ionizada (RN) em pH fisiológico
  - Atravessa mais lentamente a membrana
  - Início de ação mais lento

- **pKa próximo ao pH fisiológico** (como {anestesico_selecionado}, pKa = {pKa}):
  - Equilíbrio mais balanceado entre as formas RN e RNH⁺
  - Início de ação intermediário
""")

# Efeito do pH do tecido
st.header("Efeito do pH do Tecido")
st.markdown("""
Em tecidos inflamados ou infectados, o pH local é mais ácido (pH < 7,4):

- **Tecido acidificado**:
  - Menor proporção de anestésico na forma não-ionizada (RN)
  - Menor penetração através da membrana
  - Redução da eficácia anestésica

Isso explica por que anestésicos locais são menos eficazes em tecidos inflamados ou infectados.
""")

# Referências
st.markdown("""
---
### Referências

1. CATTERALL, W. A.; MACKIE, K. Anestésicos Locais. In: BRUNTON, L. L. et al. (Ed.). As Bases Farmacológicas da Terapêutica de Goodman & Gilman. 13. ed. Porto Alegre: AMGH, 2018.

2. BECKER, D. E.; REED, K. L. Local Anesthetics: Review of Pharmacological Considerations. Anesthesia Progress, v. 59, n. 2, p. 90-102, 2012.

3. MALAMED, S. F. Manual de Anestesia Local. 6. ed. Rio de Janeiro: Elsevier, 2013.
""")

# Rodapé
st.markdown("""
---
Desenvolvido para fins educacionais | © 2025
""")
