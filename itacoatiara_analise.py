# =============================================================================
# O GRINGO TINHA RAZÃO?
# Uma análise de dados sobre a praia mais secreta do Rio de Janeiro
# =============================================================================
# Contexto:
#   Um turista estrangeiro visitou a Praia de Itacoatiara, em Niterói (RJ),
#   elogiou demais e disse que não queria que ninguém fosse para lá —
#   para que continuasse sendo boa. Mas o que os dados dizem?
#   Será que Itacoatiara é mesmo um segredo guardado a sete chaves?
#
# Fonte dos dados: Google Trends (2021–2026)
# Termos comparados: Itacoatiara, Ipanema, Copacabana, Búzios
# =============================================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker
import numpy as np

# =============================================================================
# 1. CARREGAMENTO E LIMPEZA DOS DADOS
# =============================================================================

# Carregando a série temporal de interesse de busca
df = pd.read_csv('data/time_series_google_trends.csv')
df['Time'] = pd.to_datetime(df['Time'])
df = df.rename(columns={'itacoatiara': 'Itacoatiara'})

# Adicionando colunas auxiliares para análise temporal
df['Ano']    = df['Time'].dt.year
df['Mes']    = df['Time'].dt.month
df['AnoMes'] = df['Time'].dt.strftime('%Y-%m')

# Carregando as consultas mais frequentes
queries = pd.read_csv('data/top_queries_google_trends.csv')

print("=== Dados carregados com sucesso ===")
print(f"Período: {df['Time'].min().date()} até {df['Time'].max().date()}")
print(f"Total de meses: {len(df)}\n")
print(df.head())


# =============================================================================
# 2. ANÁLISE EXPLORATÓRIA
# =============================================================================

praias = ['Itacoatiara', 'Ipanema', 'Copacabana', 'Búzios']

print("\n=== Estatísticas Descritivas (Interesse Médio 2021–2026) ===")
print(df[praias].describe().round(2))

# Médias por praia
medias = df[praias].mean().round(1).sort_values(ascending=False)
print("\n=== Ranking de interesse médio ===")
for praia, media in medias.items():
    print(f"  {praia:<15} {media}")

# Insight principal
ratio = medias['Copacabana'] / medias['Itacoatiara']
print(f"\n>> Copacabana é {ratio:.0f}x mais buscada que Itacoatiara no Google.")
print(f">> Itacoatiara nunca ultrapassou {df['Itacoatiara'].max()} de interesse em 5 anos.")

# Pico recente
pico = df.loc[df['Copacabana'].idxmax()]
print(f"\n>> Pico geral: {pico['AnoMes']} — Copacabana atingiu score {pico['Copacabana']}")
print("   Possível causa: viralização nas redes sociais (investigar!)")

# Análise das buscas relacionadas a Itacoatiara RJ vs AM
print("\n=== Consultas relacionadas: Itacoatiara RJ (praia) ===")
filtro_rj = queries['query'].str.contains(
    'praia|niteroi|niterói|rj|ondas|surf|trilha|pousada|costão|costao',
    case=False, na=False
)
print(queries[filtro_rj][['query', 'search interest', 'increase percent']].to_string(index=False))

print("\n=== Consultas relacionadas: Itacoatiara AM (cidade) ===")
filtro_am = queries['query'].str.contains(
    'amazonas|manaus|am$| am |cep|bemol|eucatur',
    case=False, na=False
)
print(queries[filtro_am][['query', 'search interest', 'increase percent']].to_string(index=False))


# =============================================================================
# 3. VISUALIZAÇÃO
# =============================================================================

# Paleta de cores temática
BG_MAIN   = '#0a0f1e'
BG_PANEL  = '#111827'
BG_DARK   = '#0d1b2a'
TITLE_CLR = '#e8d5a3'
SUB_CLR   = '#a0b4c8'

CORES = {
    'Copacabana':  '#f59e0b',
    'Ipanema':     '#ef4444',
    'Búzios':      '#22c55e',
    'Itacoatiara': '#00d4ff',
}

fig = plt.figure(figsize=(18, 14), facecolor=BG_MAIN)
gs  = gridspec.GridSpec(3, 2, figure=fig, hspace=0.55, wspace=0.4)

# --- Título ---
fig.text(0.5, 0.97, 'O Gringo Tinha Razão?',
         fontsize=28, fontweight='bold', color=TITLE_CLR,
         ha='center', va='top', fontfamily='serif')
fig.text(0.5, 0.935,
         'O que os dados do Google dizem sobre Itacoatiara vs as praias mais famosas do RJ',
         fontsize=13, color=SUB_CLR, ha='center', va='top')

# ---- GRÁFICO 1: Série temporal ----
ax1 = fig.add_subplot(gs[0, :])
ax1.set_facecolor(BG_PANEL)

for praia, cor in CORES.items():
    lw    = 3 if praia == 'Itacoatiara' else 1.5
    alpha = 1.0 if praia == 'Itacoatiara' else 0.8
    ax1.plot(df['Time'], df[praia], color=cor, linewidth=lw,
             label=praia, alpha=alpha)

# Anotação do pico
ax1.annotate(
    f'Pico: {pico["AnoMes"]}',
    xy=(pico['Time'], pico['Copacabana']),
    xytext=(pico['Time'], pico['Copacabana'] + 6),
    color='#f59e0b', fontsize=9, ha='center',
    arrowprops=dict(arrowstyle='->', color='#f59e0b', lw=1.5)
)

ax1.set_title('Interesse de busca ao longo do tempo (Google Trends, 2021–2026)',
              color=TITLE_CLR, fontsize=13, pad=10)
ax1.set_ylabel('Interesse relativo (0–100)', color=SUB_CLR, fontsize=10)
ax1.tick_params(colors=SUB_CLR)
ax1.spines[:].set_color('#1f2937')
ax1.legend(facecolor='#1f2937', labelcolor=SUB_CLR, fontsize=10,
           loc='upper left', framealpha=0.8)
ax1.set_ylim(0, 110)

# ---- GRÁFICO 2: Barras de interesse médio ----
ax2 = fig.add_subplot(gs[1, 0])
ax2.set_facecolor(BG_PANEL)

nomes      = list(medias.index)
valores    = list(medias.values)
bar_colors = [CORES[n] for n in nomes]

bars = ax2.bar(nomes, valores, color=bar_colors, width=0.5, edgecolor='none')
for bar, val in zip(bars, valores):
    ax2.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + 0.8,
             f'{val:.0f}', ha='center',
             color='white', fontsize=12, fontweight='bold')

ax2.set_title('Interesse médio nos últimos 5 anos', color=TITLE_CLR, fontsize=12, pad=10)
ax2.set_ylabel('Score médio', color=SUB_CLR, fontsize=10)
ax2.tick_params(colors=SUB_CLR)
ax2.spines[:].set_color('#1f2937')
ax2.set_ylim(0, max(valores) * 1.2)

# ---- GRÁFICO 3: O que buscam sobre Itacoatiara RJ ----
ax3 = fig.add_subplot(gs[1, 1])
ax3.set_facecolor(BG_PANEL)

rj_labels = [
    'praia itacoatiara',
    'praia de itacoatiara',
    'itacoatiara niteroi',
    'ondas itacoatiara',
    'costão itacoatiara',
    'surfguru itacoatiara',
    'trilha itacoatiara',
    'pousada itacoatiara',
]
rj_vals   = [95, 54, 47, 12, 17, 11, 8, 9]
rj_colors = ['#00d4ff' if v > 30 else '#1d4ed8' for v in rj_vals]

bars2 = ax3.barh(rj_labels[::-1], rj_vals[::-1],
                 color=rj_colors[::-1], edgecolor='none')
for bar, val in zip(bars2, rj_vals[::-1]):
    ax3.text(val + 1, bar.get_y() + bar.get_height() / 2,
             str(val), va='center', color='white', fontsize=9)

ax3.set_title('O que as pessoas buscam sobre a praia', color=TITLE_CLR, fontsize=12, pad=10)
ax3.tick_params(colors=SUB_CLR, labelsize=8)
ax3.spines[:].set_color('#1f2937')
ax3.set_xlim(0, 115)

# ---- GRÁFICO 4: Card de conclusão ----
ax4 = fig.add_subplot(gs[2, :])
ax4.set_facecolor(BG_DARK)
ax4.axis('off')
ax4.set_title('4 Insights que o Gringo Não Sabia que Estava Provando',
              color=TITLE_CLR, fontsize=13, pad=14)

insights = [
    ("INVISIVEL",  f"Score médio: {medias['Itacoatiara']:.0f}\nA praia mais secreta do RJ.",        '#00d4ff'),
    ("15x MENOR",  f"Interesse {ratio:.0f}x menor\nque Copacabana.",                               '#f59e0b'),
    ("SCORE ZERO", '"Praia de Itacoatiara Niterói"\ntem interesse = 0 no Google.',                 '#ef4444'),
    ("AUTENTICA",  "As buscas falam de surf,\nondas e natureza — nao de turismo.", '#22c55e'),
]

for i, (titulo, texto, cor) in enumerate(insights):
    x = 0.12 + i * 0.24
    ax4.text(x, 0.80, titulo, transform=ax4.transAxes,
             fontsize=13, fontweight='bold', color=cor, ha='center')
    ax4.text(x, 0.35, texto, transform=ax4.transAxes,
             fontsize=9.5, color=SUB_CLR, ha='center', va='center',
             linespacing=1.7)

plt.savefig('itacoatiara_analise.png', dpi=150,
            bbox_inches='tight', facecolor=BG_MAIN, edgecolor='none')
print("\nVisualizacao salva em: itacoatiara_analise.png")
plt.show()


# =============================================================================
# 4. EXPORTANDO DADOS LIMPOS PARA O LOOKER STUDIO
# =============================================================================

df_export = df[['AnoMes', 'Time', 'Ano', 'Mes'] + praias].copy()
df_export.to_csv('data/praias_rj_looker_ready.csv', index=False)

print("\n=== CSV exportado para o Looker Studio ===")
print(f"Arquivo: data/praias_rj_looker_ready.csv")
print(f"Linhas:  {len(df_export)}")
print(f"Colunas: {list(df_export.columns)}")

# =============================================================================
# FIM DA ANÁLISE
# =============================================================================
