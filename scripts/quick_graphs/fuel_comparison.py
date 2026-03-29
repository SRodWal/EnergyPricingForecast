import pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

rows = [
('Enero',2022,87.49,83.22),('Febrero',2022,91.54,91.64),('Marzo',2022,98.98,108.50),('Abril',2022,110.83,101.78),('Mayo',2022,120.30,109.55),('Junio',2022,121.08,114.84),('Julio',2022,121.53,101.62),('Agosto',2022,111.87,93.67),('Septiembre',2022,112.22,84.26),('Octubre',2022,111.40,87.55),('Noviembre',2022,115.38,84.37),('Diciembre',2022,101.83,76.44),
('Enero',2023,99.10,78.12),('Febrero',2023,100.70,76.83),('Marzo',2023,92.57,73.28),('Abril',2023,89.04,79.45),('Mayo',2023,83.19,71.58),('Junio',2023,81.02,70.25),('Julio',2023,83.12,76.07),('Agosto',2023,91.67,81.39),('Septiembre',2023,100.43,89.43),('Octubre',2023,102.97,85.64),('Noviembre',2023,96.53,77.69),('Diciembre',2023,88.05,71.90),
('Enero',2024,85.87,74.15),('Febrero',2024,90.66,77.25),('Marzo',2024,91.29,81.28),('Abril',2024,90.23,85.35),('Mayo',2024,86.97,80.02),('Junio',2024,84.35,79.77),('Julio',2024,86.37,81.80),('Agosto',2024,83.84,76.68),('Septiembre',2024,80.26,70.24),('Octubre',2024,78.72,71.99),('Noviembre',2024,79.76,69.95),('Diciembre',2024,80.32,70.12),
('Enero',2025,82.32,75.74),('Febrero',2025,86.03,71.53),('Marzo',2025,84.34,68.24),('Abril',2025,81.12,63.54),('Mayo',2025,78.55,62.17),('Junio',2025,79.32,68.17),('Julio',2025,85.11,68.39),('Agosto',2025,87.18,64.86),('Septiembre',2025,85.02,63.96),('Octubre',2025,85.92,60.89),('Noviembre',2025,86.11,60.06),('Diciembre',2025,86.36,57.97),
('Enero',2026,81.27,60.04),('Febrero',2026,84.78,64.51),('Marzo',2026,95.33,88.80)
]

month_map = {'Enero':1,'Febrero':2,'Marzo':3,'Abril':4,'Mayo':5,'Junio':6,'Julio':7,'Agosto':8,'Septiembre':9,'Octubre':10,'Noviembre':11,'Diciembre':12}

df = pd.DataFrame(rows, columns=['Mes','Año','Diesel_HNL_galon','WTI_USD_barril'])
df['MesNum'] = df['Mes'].map(month_map)
df['Fecha'] = pd.to_datetime(dict(year=df['Año'], month=df['MesNum'], day=1))
df = df.sort_values('Fecha').reset_index(drop=True)

# Style (Fed-like) - same as your script
from matplotlib.ticker import FuncFormatter

def apply_fed_style():
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Georgia', 'DejaVu Serif', 'Times New Roman', 'Times'],
        'axes.edgecolor': '#444444',
        'axes.linewidth': 0.8,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.dpi': 120
    })

apply_fed_style()

MEDIAN_COLOR = '#001E40'
MEAN_COLOR = '#2C6E49'
EVENT_COLOR = '#666666'

hnl_fmt = FuncFormatter(lambda v, pos: f"L{v:,.0f}")
usd_fmt = FuncFormatter(lambda v, pos: f"${v:,.0f}")

fig, ax1 = plt.subplots(figsize=(12, 6.5))
x = np.arange(len(df))

# Lines
ax1.plot(x, df['Diesel_HNL_galon'], color=MEDIAN_COLOR, lw=2.2, label='Diésel Honduras (HNL/galón)')
ax2 = ax1.twinx()
ax2.plot(x, df['WTI_USD_barril'], color=MEAN_COLOR, lw=2.2, linestyle='--', label='WTI Crude (USD/barril)')

# Labels/format
ax1.set_ylabel('Precio Diésel (HNL/galón)')
ax1.yaxis.set_major_formatter(hnl_fmt)
ax2.set_ylabel('WTI Crude (USD/barril)')
ax2.yaxis.set_major_formatter(usd_fmt)

# Grid improvement: dashed horizontal lines (y only)
ax1.grid(axis='y', color='#DDDDDD', linestyle='--', dashes=(3,3), linewidth=0.7)
ax1.grid(axis='x', visible=False)

# Spines
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax2.spines['top'].set_visible(False)

# X ticks yearly
xticks, xticklabels = [], []
for yr in sorted(df['Año'].unique()):
    idx = df.index[df['Año']==yr][0]
    xticks.append(idx)
    xticklabels.append(str(yr))
ax1.set_xticks(xticks)
ax1.set_xticklabels(xticklabels)

# --- Event vertical lines ---
# Define events by date; place at nearest index
events = [
    (pd.Timestamp('2022-02-24'), 'Ukrania (Feb 2022)'),
    (pd.Timestamp('2026-02-28'), 'Irán (Feb 2026)')
]

# y-limits after plotting to position labels
ax1.relim(); ax1.autoscale_view()
ymin, ymax = ax1.get_ylim()

for dt, label in events:
    # find index of dt in df
    if dt in set(df['Fecha']):
        idx = int(df.index[df['Fecha']==dt][0])
    else:
        idx = int((df['Fecha'] - dt).abs().idxmin())
    ax1.axvline(idx, color=EVENT_COLOR, lw=1.0, ls=':')
    ax1.text(idx+0.2, ymax, label, color=EVENT_COLOR, va='top', ha='left', fontsize=9)

# Title/caption
fig.suptitle('Comparación: Precio Promedio Mensual Diésel (SPS) vs WTI Crude')
caption = 'Fuente: OK WIT de US Energy Information Administration (EIA); Diesel de la Secretaria de Energia de Honduras (SPS)'
ax1.text(0.0, -0.16, caption, transform=ax1.transAxes, ha='left', va='top', color='#555555', fontsize=9)

# Legend combined
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1+lines2, labels1+labels2, loc='lower left', frameon=False)

plt.tight_layout()

out_png = 'diesel_vs_wti_fedstyle_events.png'
out_pdf = 'diesel_vs_wti_fedstyle_events.pdf'
fig.savefig(out_png, dpi=300, bbox_inches='tight')
fig.savefig(out_pdf, bbox_inches='tight')
plt.close(fig)

out_png, out_pdf