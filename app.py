import os
import warnings
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

warnings.filterwarnings('ignore')

# ── PAGE CONFIG ───────────────────────────────────────────
st.set_page_config(
    page_title="Smart Farming Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── LOAD EXTERNAL CSS ─────────────────────────────────────
def load_css(css_file):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(BASE_DIR, css_file)
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('style.css')

# ── STYLE HELPER untuk semua grafik Plotly ────────────────
def style_fig(fig, height=420, showlegend=True):
    fig.update_layout(
        plot_bgcolor='#f9fafb',
        paper_bgcolor='white',
        height=height,
        margin=dict(t=55, b=25, l=20, r=20),
        font=dict(color='#1e3a2f', family='Poppins, Arial', size=12),
        title_font=dict(color='#1e3a2f', size=14),
        showlegend=showlegend,
        legend=dict(
            font=dict(color='#1e3a2f'),
            title=dict(font=dict(color='#1e3a2f', size=12))
        ),
        xaxis=dict(
            tickfont=dict(color='#1e3a2f'),
            title_font=dict(color='#1e3a2f'),
        ),
        yaxis=dict(
            tickfont=dict(color='#1e3a2f'),
            title_font=dict(color='#1e3a2f'),
        ),
    )
    return fig


# ── LOAD DATA ─────────────────────────────────────────────
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, 'cleaned_data.csv')
    df = pd.read_csv(DATA_PATH, sep=None, engine='python', encoding='utf-8-sig')
    df.columns = df.columns.str.strip().str.replace('\ufeff', '', regex=False)
    numeric_cols = [
        'soil_moisture_%', 'soil_pH', 'temperature_C', 'rainfall_mm',
        'humidity_%', 'sunlight_hours', 'pesticide_usage_ml',
        'total_days', 'yield_kg_per_hectare', 'NDVI_index'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True, errors='coerce')
    return df

df = load_data()

# ── THRESHOLD ALERT (batas aman sensor) ───────────────────
THRESHOLDS = {
    'soil_moisture_%' : {'min': 15.0, 'max': 40.0, 'label': 'Soil Moisture (%)'},
    'soil_pH'         : {'min': 5.8,  'max': 7.2,  'label': 'Soil pH'},
    'temperature_C'   : {'min': 15.0, 'max': 32.0, 'label': 'Suhu (°C)'},
    'humidity_%'      : {'min': 40.0, 'max': 85.0, 'label': 'Humidity (%)'},
    'NDVI_index'      : {'min': 0.4,  'max': 1.0,  'label': 'NDVI Index'},
}

# ── SIDEBAR ───────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/plant-under-sun.png", width=70)
st.sidebar.markdown("## 🌾 Smart Farming")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔽 Filter Data")

regions = ['Semua'] + sorted(df['region'].dropna().unique().tolist())
crops   = ['Semua'] + sorted(df['crop_type'].dropna().unique().tolist())
disease = ['Semua'] + sorted(df['crop_disease_status'].dropna().unique().tolist())

sel_region  = st.sidebar.selectbox("📍 Wilayah",        regions)
sel_crop    = st.sidebar.selectbox("🌱 Jenis Tanaman",   crops)
sel_disease = st.sidebar.selectbox("🦠 Status Penyakit", disease)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚠️ Batas Threshold Alert")
st.sidebar.caption("Ubah batas aman sensor:")
THRESHOLDS['soil_moisture_%']['min'] = st.sidebar.slider(
    "💧 Min Soil Moisture (%)", 5.0, 30.0, 15.0, 0.5)
THRESHOLDS['temperature_C']['max']   = st.sidebar.slider(
    "🌡️ Max Suhu (°C)",         25.0, 40.0, 32.0, 0.5)
THRESHOLDS['NDVI_index']['min']      = st.sidebar.slider(
    "🌿 Min NDVI Index",         0.1,  0.7,  0.4, 0.05)

df_f = df.copy()
if sel_region  != 'Semua': df_f = df_f[df_f['region']             == sel_region]
if sel_crop    != 'Semua': df_f = df_f[df_f['crop_type']           == sel_crop]
if sel_disease != 'Semua': df_f = df_f[df_f['crop_disease_status'] == sel_disease]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Data ditampilkan:** {len(df_f)} farm")


# ═══════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════
st.markdown("# 🌾 Smart Farming Dashboard")
st.markdown("Monitoring & analisis data sensor pertanian berbasis IoT")
st.markdown("---")


# ═══════════════════════════════════════════════════════════
# SECTION 1 — KPI METRICS
# ═══════════════════════════════════════════════════════════
def kpi(col, icon, label, value, color="#4caf50"):
    col.markdown(f"""
    <div class="metric-card" style="border-left-color:{color}">
        <div class="metric-value">{icon} {value}</div>
        <div class="metric-label">{label}</div>
    </div>""", unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)
kpi(k1, "🏡", "Total Farm",        f"{len(df_f)}")
kpi(k2, "📈", "Avg Yield (kg/ha)", f"{df_f['yield_kg_per_hectare'].mean():.0f}", "#2196f3")
kpi(k3, "🌿", "Avg NDVI",          f"{df_f['NDVI_index'].mean():.2f}",           "#8bc34a")
kpi(k4, "🌡️", "Avg Suhu (°C)",     f"{df_f['temperature_C'].mean():.1f}",        "#ff9800")
kpi(k5, "💧", "Avg Soil Moisture", f"{df_f['soil_moisture_%'].mean():.1f}%",     "#03a9f4")

st.markdown("---")


# ═══════════════════════════════════════════════════════════
# SECTION 2 — ALERT SYSTEM
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🚨 Alert System — Status Sensor</div>',
            unsafe_allow_html=True)

def check_alerts(df_check):
    alerts = []
    for col, thr in THRESHOLDS.items():
        if col not in df_check.columns:
            continue
        below = df_check[df_check[col] < thr['min']]
        above = df_check[df_check[col] > thr['max']]
        if len(below) > 0:
            alerts.append({
                'sensor'  : thr['label'],
                'kondisi' : f"⬇️ Di bawah minimum ({thr['min']})",
                'jumlah'  : len(below),
                'farm_ids': ', '.join(below['farm_id'].head(5).tolist()),
                'tipe'    : 'below'
            })
        if len(above) > 0:
            alerts.append({
                'sensor'  : thr['label'],
                'kondisi' : f"⬆️ Di atas maksimum ({thr['max']})",
                'jumlah'  : len(above),
                'farm_ids': ', '.join(above['farm_id'].head(5).tolist()),
                'tipe'    : 'above'
            })
    return alerts

alerts = check_alerts(df_f)

alert_mask = pd.Series([False] * len(df_f), index=df_f.index)
for col, thr in THRESHOLDS.items():
    if col in df_f.columns:
        alert_mask |= (df_f[col] < thr['min']) | (df_f[col] > thr['max'])
total_alert_farms = alert_mask.sum()

# Banner status
if total_alert_farms == 0:
    st.markdown("""
    <div style="background:#e8f5e9;border:1.5px solid #4caf50;border-radius:10px;
                padding:14px 20px;margin-bottom:14px;">
        <span style="font-size:20px">✅</span>
        <strong style="color:#2e7d32;font-size:15px;margin-left:8px;">
            Semua sensor dalam kondisi normal
        </strong>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style="background:#ffebee;border:1.5px solid #f44336;border-radius:10px;
                padding:14px 20px;margin-bottom:14px;">
        <span style="font-size:20px">🚨</span>
        <strong style="color:#c62828;font-size:15px;margin-left:8px;">
            {total_alert_farms} farm terdeteksi kondisi sensor di luar batas aman!
        </strong>
    </div>""", unsafe_allow_html=True)

# Kartu alert per sensor
if alerts:
    n_show = min(len(alerts), 4)
    alert_cols = st.columns(n_show)
    for i, alert in enumerate(alerts[:n_show]):
        bg   = '#fff3e0' if alert['tipe'] == 'above' else '#ffebee'
        bc   = '#ff9800' if alert['tipe'] == 'above' else '#f44336'
        tc   = '#e65100' if alert['tipe'] == 'above' else '#c62828'
        icon = ('🌡️' if 'Suhu' in alert['sensor'] else
                '💧' if 'Moisture' in alert['sensor'] else
                '🌿' if 'NDVI' in alert['sensor'] else '⚠️')
        alert_cols[i].markdown(f"""
        <div style="background:{bg};border:1.5px solid {bc};border-radius:10px;
                    padding:14px 16px;margin-bottom:8px;">
            <div style="font-size:13px;font-weight:700;color:{tc}">{icon} {alert['sensor']}</div>
            <div style="font-size:11px;color:{tc};margin-top:4px">{alert['kondisi']}</div>
            <div style="font-size:24px;font-weight:700;color:{tc};margin-top:6px">
                {alert['jumlah']} farm
            </div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")


# ═══════════════════════════════════════════════════════════
# SECTION 3 — GAUGE METER
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🎯 Gauge Meter — Kondisi Rata-rata Sensor</div>',
            unsafe_allow_html=True)

gauge_sensors = [
    ('soil_moisture_%', 'Soil Moisture', '%',  0,  50,  15, 40),
    ('humidity_%',      'Humidity',      '%',  0, 100,  40, 85),
    ('temperature_C',   'Suhu',          '°C', 0,  45,  15, 32),
    ('NDVI_index',      'NDVI Index',    '',   0,   1, 0.4,  1),
]

g_cols = st.columns(4)
for i, (col, label, unit, rmin, rmax, smin, smax) in enumerate(gauge_sensors):
    val = float(df_f[col].mean()) if col in df_f.columns else 0.0
    bar_color = ('#f44336' if (val < smin or val > smax) else
                 '#ff9800' if (val < smin * 1.15 or val > smax * 0.93) else
                 '#4caf50')
    fig_g = go.Figure(go.Indicator(
        mode='gauge+number+delta',
        value=val,
        number=dict(suffix=f' {unit}', font=dict(color='#1e3a2f', size=22)),
        delta=dict(reference=(smin + smax) / 2, font=dict(color='#1e3a2f')),
        title=dict(text=f'<b>{label}</b>', font=dict(color='#1e3a2f', size=13)),
        gauge=dict(
            axis=dict(range=[rmin, rmax],
                      tickfont=dict(color='#1e3a2f', size=9),
                      tickcolor='#1e3a2f'),
            bar=dict(color=bar_color, thickness=0.25),
            bgcolor='white',
            borderwidth=1,
            bordercolor='#e0e0e0',
            steps=[
                dict(range=[rmin, smin], color='#ffebee'),
                dict(range=[smin, smax], color='#e8f5e9'),
                dict(range=[smax, rmax], color='#fff3e0'),
            ],
            threshold=dict(
                line=dict(color='#f44336', width=3),
                thickness=0.75, value=smax
            )
        )
    ))
    fig_g.update_layout(
        paper_bgcolor='white', height=230,
        margin=dict(t=40, b=10, l=20, r=20),
        font=dict(color='#1e3a2f')
    )
    g_cols[i].plotly_chart(fig_g, use_container_width=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════
# SECTION 4 — TIME SERIES
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📈 Time Series — Tren Sensor IoT per Bulan</div>',
            unsafe_allow_html=True)

def hex_to_rgba(hex_color, alpha=0.08):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f'rgba({r},{g},{b},{alpha})'

month_map = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr',
             5:'Mei', 6:'Jun', 7:'Jul', 8:'Agu'}

ts_cols   = ['yield_kg_per_hectare', 'soil_moisture_%', 'temperature_C',
             'humidity_%', 'NDVI_index']
ts_labels = ['Yield (kg/ha)', 'Soil Moisture (%)', 'Suhu (°C)',
             'Humidity (%)', 'NDVI Index']

df_ts      = df_f.copy()
df_ts['bulan_num'] = df_ts['timestamp'].dt.month
df_monthly = df_ts.groupby('bulan_num')[ts_cols].mean().reset_index()
df_monthly['bulan'] = df_monthly['bulan_num'].map(month_map)
df_monthly = df_monthly.sort_values('bulan_num')

ts_sel = st.multiselect(
    "Pilih sensor:",
    options=ts_cols,
    default=['soil_moisture_%', 'temperature_C', 'NDVI_index'],
    format_func=lambda x: dict(zip(ts_cols, ts_labels))[x]
)

if ts_sel and len(df_monthly) > 0:
    ts_colors = ['#2196f3', '#f44336', '#4caf50', '#ff9800', '#9c27b0']
    fig_ts = make_subplots(
        rows=len(ts_sel), cols=1,
        shared_xaxes=True,
        subplot_titles=[dict(zip(ts_cols, ts_labels))[m] for m in ts_sel],
        vertical_spacing=0.07
    )
    for i, metric in enumerate(ts_sel):
        color = ts_colors[i % len(ts_colors)]
        fig_ts.add_trace(go.Scatter(
            x=df_monthly['bulan'], y=df_monthly[metric],
            mode='lines+markers',
            name=dict(zip(ts_cols, ts_labels))[metric],
            line=dict(color=color, width=2.5),
            marker=dict(size=8, color=color),
            fill='tozeroy', fillcolor=hex_to_rgba(color, 0.08),
        ), row=i+1, col=1)

        if metric in THRESHOLDS:
            fig_ts.add_hline(
                y=THRESHOLDS[metric]['min'],
                line_dash='dot', line_color='#f44336', line_width=1.5,
                annotation_text=f"Min ({THRESHOLDS[metric]['min']})",
                annotation_font_color='#f44336', annotation_font_size=10,
                row=i+1, col=1
            )
            fig_ts.add_hline(
                y=THRESHOLDS[metric]['max'],
                line_dash='dot', line_color='#ff9800', line_width=1.5,
                annotation_text=f"Max ({THRESHOLDS[metric]['max']})",
                annotation_font_color='#ff9800', annotation_font_size=10,
                row=i+1, col=1
            )
        fig_ts.update_yaxes(
            title_text=dict(zip(ts_cols, ts_labels))[metric],
            title_font=dict(color='#1e3a2f', size=11),
            tickfont=dict(color='#1e3a2f', size=10),
            gridcolor='#eee', row=i+1, col=1
        )
    fig_ts.update_xaxes(
        tickfont=dict(color='#1e3a2f'), gridcolor='#eee',
        row=len(ts_sel), col=1
    )
    fig_ts.update_layout(
        paper_bgcolor='white', plot_bgcolor='#f9fafb',
        height=195 * len(ts_sel),
        margin=dict(t=40, b=30, l=20, r=20),
        font=dict(color='#1e3a2f', family='Poppins, Arial'),
        showlegend=False,
        title=dict(text='📈 Tren Bulanan Data Sensor IoT',
                   font=dict(color='#1e3a2f', size=14))
    )
    for ann in fig_ts.layout.annotations:
        ann.font.color = '#1e3a2f'
        ann.font.size  = 12
    st.plotly_chart(fig_ts, use_container_width=True)
else:
    st.info("Pilih minimal satu sensor di atas.")

st.markdown("---")


# ═══════════════════════════════════════════════════════════
# SECTION 5 — HEATMAP KORELASI
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔬 Heatmap — Korelasi Antar Sensor</div>',
            unsafe_allow_html=True)

corr_cols = ['soil_moisture_%', 'soil_pH', 'temperature_C', 'rainfall_mm',
             'humidity_%', 'sunlight_hours', 'pesticide_usage_ml',
             'total_days', 'NDVI_index', 'yield_kg_per_hectare']
corr_cols = [c for c in corr_cols if c in df_f.columns]
corr_labels = {
    'soil_moisture_%'     : 'Soil Moisture', 'soil_pH'         : 'Soil pH',
    'temperature_C'       : 'Suhu',          'rainfall_mm'     : 'Rainfall',
    'humidity_%'          : 'Humidity',      'sunlight_hours'  : 'Sunlight',
    'pesticide_usage_ml'  : 'Pestisida',     'total_days'      : 'Total Hari',
    'NDVI_index'          : 'NDVI',          'yield_kg_per_hectare': 'Yield'
}

corr_matrix = df_f[corr_cols].corr()
corr_matrix.index   = [corr_labels.get(c, c) for c in corr_matrix.index]
corr_matrix.columns = [corr_labels.get(c, c) for c in corr_matrix.columns]

fig_hm = px.imshow(
    corr_matrix, text_auto='.2f',
    color_continuous_scale='RdYlGn', zmin=-1, zmax=1,
    title='🔬 Matriks Korelasi Antar Variabel Sensor & Yield',
    aspect='auto'
)
fig_hm.update_traces(textfont=dict(color='#1e3a2f', size=11))
fig_hm.update_layout(
    paper_bgcolor='white', height=480,
    margin=dict(t=55, b=20, l=20, r=20),
    title_font=dict(color='#1e3a2f', size=14),
    font=dict(color='#1e3a2f', family='Poppins, Arial'),
    xaxis=dict(tickfont=dict(color='#1e3a2f'), title_font=dict(color='#1e3a2f')),
    yaxis=dict(tickfont=dict(color='#1e3a2f'), title_font=dict(color='#1e3a2f')),
    coloraxis_colorbar=dict(
        tickfont=dict(color='#1e3a2f'),
        title=dict(text='Korelasi', font=dict(color='#1e3a2f'))
    )
)
st.plotly_chart(fig_hm, use_container_width=True)

st.markdown("---")

