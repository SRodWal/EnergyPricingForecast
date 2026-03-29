import pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

import matplotlib.image as mpimg
from pathlib import Path



# --- Updated Data: Diesel in USD/galón, WTI in USD/barril ---
rows = [
('Enero',2022,3.56,88.15),('Febrero',2022,3.71,95.72),('Marzo',2022,4.03,100.28),
('Abril',2022,4.52,104.69),('Mayo',2022,4.90,114.67),('Junio',2022,4.93,105.76),
('Julio',2022,4.94,98.62),('Agosto',2022,4.55,89.55),('Septiembre',2022,4.54,79.49),
('Octubre',2022,4.49,86.53),('Noviembre',2022,4.65,80.56),('Diciembre',2022,4.12,80.47),

('Enero',2023,4.01,80.11),('Febrero',2023,4.08,77.05),('Marzo',2023,3.75,75.67),
('Abril',2023,3.61,76.78),('Mayo',2023,3.37,68.09),('Junio',2023,3.28,70.64),
('Julio',2023,3.36,81.80),('Agosto',2023,3.71,83.63),('Septiembre',2023,4.06,90.79),
('Octubre',2023,4.15,81.02),('Noviembre',2023,3.89,75.96),('Diciembre',2023,3.55,71.65),

('Enero',2024,3.47,75.85),('Febrero',2024,3.66,78.26),('Marzo',2024,3.68,83.17),
('Abril',2024,3.64,81.93),('Mayo',2024,3.50,76.99),('Junio',2024,3.40,81.54),
('Julio',2024,3.47,77.91),('Agosto',2024,3.37,73.55),('Septiembre',2024,3.22,68.17),
('Octubre',2024,3.15,69.26),('Noviembre',2024,3.17,68.00),('Diciembre',2024,3.16,71.72),

('Enero',2025,3.22,72.53),('Febrero',2025,3.35,69.76),('Marzo',2025,3.28,71.48),
('Abril',2025,3.14,58.21),('Mayo',2025,3.02,60.79),('Junio',2025,3.03,65.11),
('Julio',2025,3.23,69.26),('Agosto',2025,3.33,64.01),('Septiembre',2025,3.24,62.37),
('Octubre',2025,3.26,60.98),('Noviembre',2025,3.26,58.55),('Diciembre',2025,3.26,57.42),

('Enero',2026,3.06,65.21),('Febrero',2026,3.26,67.02),('Marzo',2026,4.06,99.64)
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
usd_fmt = FuncFormatter(lambda v, pos: f"${v:,.2f}")

fig, ax1 = plt.subplots(figsize=(12, 6.5))
x = np.arange(len(df))

# Lines
ax1.plot(x, df['Diesel_HNL_galon'], color=MEDIAN_COLOR, lw=2.2, label='Diésel Honduras (USD/galón)')
ax2 = ax1.twinx()
ax2.plot(x, df['WTI_USD_barril'], color=MEAN_COLOR, lw=2.2, linestyle='--', label='WTI Crude (USD/barril)')

# Labels/format
ax1.set_ylabel('Precio Diésel (USD/galón)')
ax1.yaxis.set_major_formatter(usd_fmt)
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
    (pd.Timestamp('2022-02-01'), 'Ukrania (Feb 2022)'),
    (pd.Timestamp('2026-02-01'), 'Irán (Feb 2026)')
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

# --- Load logo (PNG recommended) ---
logo_path = "logo.jpg"
logo = mpimg.imread(logo_path)

# --- Add an axes in *figure coordinates* (x, y, width, height) ---
# Coordinates are fractions of the figure:
# (0,0) bottom-left, (1,1) top-right
logo_ax = fig.add_axes([0.075, 0.020, 0.15, 0.15], anchor='SW')

logo_ax.imshow(logo)
logo_ax.axis("off")

# Title/caption
fig.suptitle('Precio de Diesel se incrementa en un 25% en Honduras, mitigado por subsidios, \n mientras que el WIT Curde aunmenta un 45%. \nSubsidio podria desaparecer a finales de Abril, 2026.',
             fontsize = 16,
             fontweight = 'bold',
             y = 0.98)
caption = 'La ultima vez, los precios tardaron un año en bajar hasta su premedio inicual.\n \nFuentes: \nWTI Crude Oil (precios de cierre, USD/barril): NYMEX/CME Group; \nDiesel de la Secretaria de Energia de Honduras (SPS); \nTipo de cambio promedio mensual de Banco Central de Honduras aplicado para convertir a USD.  '
ax1.text(0.13, -0.09, caption, transform=ax1.transAxes,
         ha="left", va="top", color="#555555", fontsize=9)

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