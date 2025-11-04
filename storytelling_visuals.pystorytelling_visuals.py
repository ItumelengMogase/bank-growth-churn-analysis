"""
storytelling_visuals.py
- Creates 4 visualisations (HTML) in outputs/
- Visual 4 text set to black
- Executive summary exported as a PowerPoint slide (outputs/05_executive_summary_slide.pptx)
- Uses 'ME' month-end freq for placeholders
- Safe guards for empty queries and ZAR formatting
"""

import os
from dotenv import load_dotenv
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

load_dotenv()

# ---------- Configuration / environment ----------
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "bank_analytics")
DB_PORT = os.getenv("DB_PORT", "5432")

if not DB_USER or not DB_PASSWORD:
    raise RuntimeError("DB_USER and DB_PASSWORD must be set in the environment (or .env).")

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Ensure outputs dir exists
os.makedirs("outputs", exist_ok=True)

# ---------- Styling / colours ----------
COLORS = {
    'context': '#D3D3D3',      # Grey - background info
    'primary': '#2E86AB',      # Blue - hero (Referral)
    'problem': '#E63946',      # Red - issues
    'target': '#06A77D',       # Green - goals
    'text_main': '#2B2B2B',    # black-ish for text
    'text_secondary': '#757575'
}

# ---------- Helpers ----------
def safe_get_single(df, cond_col, cond_val, return_col, default=None):
    """Return a single value from df[return_col] where df[cond_col] == cond_val.
       Returns default if no match or empty.
    """
    if df is None or df.empty:
        return default
    sel = df.loc[df[cond_col] == cond_val, return_col]
    if sel.empty:
        return default
    return sel.iloc[0]

def zAR(v, round_to=0):
    """Format numeric value as South African Rand string like R1,234"""
    try:
        if v is None:
            return "R0"
        if pd.isna(v):
            return "R0"
        vnum = int(round(float(v), round_to))
        return f"R{vnum:,}"
    except Exception:
        return str(v)

def save_html(fig, filename_base):
    path = os.path.join("outputs", f"{filename_base}.html")
    fig.write_html(path)
    return path

# -----------------------------
# VISUALISATION 1: Churn Crisis
# -----------------------------
print("Creating Viz 1: The Churn Crisis.")

try:
    churn_df = pd.read_sql("""
        SELECT month, churn_rate_pct, mom_change, risk_level
        FROM analytics.churn_acceleration
        ORDER BY month
    """, engine)

    if churn_df.empty:
        raise ValueError("Empty result set")

except Exception as e:
    print(f"Warning: Could not fetch churn_acceleration data ({e}). Creating placeholder chart.")
    churn_df = pd.DataFrame({
        'month': pd.date_range(start='2024-01-01', periods=12, freq='ME'),
        'churn_rate_pct': [5.6,5.6,5.7,5.8,5.9,6.0,6.1,6.3,6.4,6.6,6.8,6.9],
        'mom_change': [0]*12,
        'risk_level': ['normal']*12
    })

churn_df['month'] = pd.to_datetime(churn_df['month'])

fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=churn_df['month'][:7],
    y=churn_df['churn_rate_pct'][:7],
    mode='lines',
    name='Normal Period',
    line=dict(color=COLORS['context'], width=2),
    hovertemplate='%{y:.1f}%<extra></extra>'
))

fig1.add_trace(go.Scatter(
    x=churn_df['month'][6:],
    y=churn_df['churn_rate_pct'][6:],
    mode='lines+markers',
    name='Crisis Period',
    line=dict(color=COLORS['problem'], width=4),
    marker=dict(size=8),
    hovertemplate='%{y:.1f}%<extra></extra>'
))

fig1.add_hline(
    y=6.0,
    line_dash="dot",
    line_color=COLORS['problem'],
    annotation_text="6% alert threshold",
    annotation_position="right",
    annotation=dict(font_size=11, font_color=COLORS['problem'])
)

# If May exists annotate "2 employees quit here"
may_row = churn_df[churn_df['month'].dt.month == 5]
if not may_row.empty:
    m = may_row.iloc[0]
    fig1.add_annotation(
        x=m['month'],
        y=m['churn_rate_pct'],
        text="2 employees quit here",
        showarrow=True,
        arrowhead=2,
        ax=0, ay=-60,
        font=dict(color=COLORS['text_main'])
    )

fig1.update_layout(
    title={
        'text': '<b>Churn Crisis: Rate Jumped (recent months)</b><br><sub>Two headcount changes in May; recovery incomplete</sub>',
        'x': 0, 'xanchor': 'left', 'font': {'size': 18, 'color': COLORS['text_main']}
    },
    xaxis_title='<b>Month (2024)</b>',
    yaxis_title='<b>Churn Rate (%)</b>',
    height=500, width=900, hovermode='x unified', showlegend=False,
    plot_bgcolor='white', paper_bgcolor='white',
    font=dict(family="Arial", size=12, color=COLORS['text_main'])
)
fig1.update_xaxes(showline=True, linewidth=1, linecolor=COLORS['context'], gridcolor='rgba(211,211,211,0.3)', tickformat='%b')
fig1.update_yaxes(showline=True, linewidth=1, linecolor=COLORS['context'], gridcolor='rgba(211,211,211,0.3)', range=[max(0, churn_df['churn_rate_pct'].min()-0.5), churn_df['churn_rate_pct'].max()+0.5])

path1 = save_html(fig1, "01_churn_crisis")
print("  ✓ Saved:", path1)

# --------------------------------
# VISUALISATION 2: Channel Performance
# --------------------------------
print("Creating Viz 2: Channel Performance.")

try:
    channel_df = pd.read_sql("""
        SELECT acquisition_channel, avg_conversion_rate as conversion_rate, cac, total_users_acquired, quality_score
        FROM analytics.channel_scorecard
        ORDER BY quality_score DESC
    """, engine)

    if channel_df.empty:
        raise ValueError("Empty result set")

except Exception as e:
    print(f"Warning: Could not fetch channel_scorecard data ({e}). Creating placeholders.")
    channel_df = pd.DataFrame({
        'acquisition_channel': ['Referral','Email','Social Media','Paid Search'],
        'conversion_rate': [82.6,45.0,12.3,33.1],
        'cac': [20,10,42,30],
        'total_users_acquired': [20000,15000,45000,12000],
        'quality_score': [95,80,30,60]
    })

colors = [
    COLORS['primary'] if ch == 'Referral' else COLORS['problem'] if ch == 'Social Media' else COLORS['context']
    for ch in channel_df['acquisition_channel']
]

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    y=channel_df['acquisition_channel'],
    x=channel_df['conversion_rate'],
    orientation='h',
    marker=dict(color=colors),
    text=[f"{x:.1f}%" for x in channel_df['conversion_rate']],
    textposition='outside',
    textfont=dict(size=13, color=COLORS['text_main']),
    hovertemplate='<b>%{y}</b><br>Conversion: %{x:.1f}%<extra></extra>'
))

ref_conv = safe_get_single(channel_df, 'acquisition_channel', 'Referral', 'conversion_rate', default=None)
sm_conv = safe_get_single(channel_df, 'acquisition_channel', 'Social Media', 'conversion_rate', default=None)
if ref_conv is not None:
    fig2.add_annotation(
        x=ref_conv, y='Referral',
        text="<b>Best conversion</b><br>High first-deposit conversion",
        showarrow=True, arrowhead=2, arrowcolor=COLORS['primary'], ax=-100, ay=-40,
        font=dict(size=11, color=COLORS['primary']),
        bgcolor='rgba(255,255,255,0.9)', bordercolor=COLORS['primary'], borderwidth=2
    )
if sm_conv is not None:
    fig2.add_annotation(
        x=sm_conv, y='Social Media',
        text="<b>Poor conversion</b><br>High spend, low conversion",
        showarrow=True, arrowhead=2, arrowcolor=COLORS['problem'], ax=100, ay=40,
        font=dict(size=11, color=COLORS['problem']),
        bgcolor='rgba(255,255,255,0.9)', bordercolor=COLORS['problem'], borderwidth=2
    )

fig2.update_layout(
    title={'text': '<b>Channel performance: who converts?</b><br><sub>Referral channels show highest conversion</sub>', 'x':0, 'xanchor':'left', 'font': {'size': 18, 'color': COLORS['text_main']}},
    xaxis_title='<b>Conversion Rate (% who make first deposit)</b>',
    height=450, width=900, showlegend=False,
    plot_bgcolor='white', paper_bgcolor='white', font=dict(family="Arial", size=12, color=COLORS['text_main'])
)
fig2.update_xaxes(showline=True, linewidth=1, linecolor=COLORS['context'], gridcolor='rgba(211,211,211,0.3)', range=[0, max(90, channel_df['conversion_rate'].max()*1.1)])
fig2.update_yaxes(showline=False, categoryorder='total ascending')

path2 = save_html(fig2, "02_channel_performance")
print("  ✓ Saved:", path2)

# -----------------------------
# VISUALISATION 3: LTV:CAC
# -----------------------------
print("Creating Viz 3: LTV:CAC Analysis.")

try:
    ltv_df = pd.read_sql("""
        SELECT acquisition_channel, estimated_ltv_12month as ltv, cac, ltv_cac_ratio_12m as ratio, profitability_grade
        FROM analytics.ltv_by_channel_proxy
        ORDER BY ltv_cac_ratio_12m DESC
    """, engine)

    if ltv_df.empty:
        raise ValueError("Empty result set")

except Exception as e:
    print(f"Warning: Could not fetch ltv_by_channel_proxy data ({e}). Creating placeholders.")
    ltv_df = pd.DataFrame({
        'acquisition_channel': ['Referral','Email','Paid Search','Social Media'],
        'ltv': [320,120,90,30],
        'cac': [100,70,100,28],
        'ratio': [3.2,1.7,0.9,1.1],
        'profitability_grade': ['A','B','C','D']
    })

colors = [COLORS['primary'] if ch == 'Referral' else COLORS['problem'] if ch == 'Social Media' else COLORS['context'] for ch in ltv_df['acquisition_channel']]

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    x=ltv_df['acquisition_channel'],
    y=ltv_df['ratio'],
    marker=dict(color=colors),
    text=[f"{x:.1f}x" for x in ltv_df['ratio']],
    textposition='outside',
    textfont=dict(size=14, color=COLORS['text_main'], family='Arial Black'),
    hovertemplate='<b>%{x}</b><br>LTV:CAC Ratio: %{y:.1f}x<extra></extra>'
))

fig3.add_hline(y=3.0, line_dash="dash", line_color=COLORS['target'], annotation_text="Healthy 3:1 benchmark", annotation_position="right", annotation=dict(font_size=12, font_color=COLORS['target']))
fig3.add_hline(y=1.0, line_dash="dash", line_color=COLORS['problem'], annotation_text="Break-even", annotation_position="right", annotation=dict(font_size=11, font_color=COLORS['problem']))

fig3.update_layout(
    title={'text': '<b>Referral customers: high LTV:CAC</b><br><sub>Social Media underperforms</sub>', 'x':0, 'xanchor':'left', 'font': {'size':18, 'color': COLORS['text_main']}},
    xaxis_title='<b>Acquisition Channel</b>', yaxis_title='<b>LTV:CAC Ratio (12-month)</b>',
    height=500, width=900, showlegend=False, plot_bgcolor='white', paper_bgcolor='white', font=dict(family="Arial", size=12, color=COLORS['text_main'])
)
fig3.update_xaxes(showline=True, linewidth=1, linecolor=COLORS['context'])
fig3.update_yaxes(showline=True, linewidth=1, linecolor=COLORS['context'], gridcolor='rgba(211,211,211,0.3)', range=[0, max(4, ltv_df['ratio'].max()*1.1)])

path3 = save_html(fig3, "03_ltv_cac_ratio")
print("  ✓ Saved:", path3)

# ---------------------------------------
# VISUALISATION 4: Engagement / Growth (text in black)
# ---------------------------------------
print("Creating Viz 4: Growth vs. Engagement.")

engagement_df = pd.read_sql("""
    SELECT month, active_users, engagement_score, engagement_change_pct_mom
    FROM analytics.engagement_trends
    ORDER BY month
""", engine)

if engagement_df.empty:
    print("Warning: engagement_trends returned no rows. Creating placeholders.")
    engagement_df = pd.DataFrame({
        'month': pd.date_range(start='2024-01-01', periods=12, freq='ME'),
        'active_users': [42500,44000,48000,52000,56000,61000,65000,69000,73000,76000,80000,81300],
        'engagement_score': [100,98,95,92,88,84,80,76,72,68,65,65],
        'engagement_change_pct_mom': [0]*12
    })

engagement_df['month'] = pd.to_datetime(engagement_df['month'])

def normalize_series(s):
    if s.max() == s.min():
        return [50]*len(s)
    return ((s - s.min()) / (s.max() - s.min())) * 100

engagement_df['users_normalized'] = normalize_series(engagement_df['active_users'])
engagement_df['engagement_normalized'] = normalize_series(engagement_df['engagement_score'])

fig4 = go.Figure()
fig4.add_trace(go.Scatter(
    x=engagement_df['month'],
    y=engagement_df['users_normalized'],
    name='Active Users',
    mode='lines',
    line=dict(color=COLORS['context'], width=2),
    fill='tozeroy',
    fillcolor='rgba(211,211,211,0.2)',
    hovertemplate='Active Users: %{customdata:,0f}<extra></extra>',
    customdata=engagement_df['active_users']
))
fig4.add_trace(go.Scatter(
    x=engagement_df['month'],
    y=engagement_df['engagement_normalized'],
    name='Engagement Score',
    mode='lines+markers',
    line=dict(color=COLORS['problem'], width=4),
    marker=dict(size=8),
    hovertemplate='Engagement Score: %{customdata:.1f}<extra></extra>',
    customdata=engagement_df['engagement_score']
))

fig4.update_layout(
    title={'text': "<b>Growth paradox: users up, engagement down</b><br><sub>Acquiring faster than engaging</sub>", 'x':0, 'xanchor':'left', 'font': {'size':18, 'color': COLORS['text_main']}},
    xaxis_title='<b>Month (2024)</b>',
    yaxis_title='<b>Normalized Score (0-100)</b>',
    height=500, width=900, hovermode='x unified', showlegend=True,
    plot_bgcolor='white', paper_bgcolor='white',
    font=dict(family="Arial", size=12, color=COLORS['text_main']),
    legend=dict(font=dict(color=COLORS['text_main']))
)

fig4.update_xaxes(showline=True, linewidth=1, linecolor=COLORS['context'], gridcolor='rgba(211,211,211,0.3)', tickformat='%b', tickfont=dict(color=COLORS['text_main']))
fig4.update_yaxes(showline=True, linewidth=1, linecolor=COLORS['context'], gridcolor='rgba(211,211,211,0.3)', tickfont=dict(color=COLORS['text_main']))

path4 = save_html(fig4, "04_growth_vs_engagement")
print("  ✓ Saved:", path4)

# ------------------------------------------------
# Executive Summary as a PowerPoint slide
# ------------------------------------------------
print("Creating Executive Summary slide (PowerPoint).")

# Compute summary KPIs using available data, fallbacks if missing
current_churn = float(churn_df['churn_rate_pct'].iloc[-1]) if not churn_df.empty else None
baseline_churn = float(churn_df['churn_rate_pct'].iloc[0]) if not churn_df.empty else None

average_revenue_per_customer = 1200  # placeholder ZAR/year
customer_base = 10000  # placeholder
if current_churn is not None and baseline_churn is not None:
    savings_rands = customer_base * max(0, baseline_churn - current_churn) / 100.0 * average_revenue_per_customer
else:
    savings_rands = 400000

top_ratio = ltv_df['ratio'].max() if not ltv_df.empty else None
top_ratio_text = f"{top_ratio:.1f}x" if top_ratio is not None else "—"
needed_fte = 2

# Build simple one-slide PPTX
prs = Presentation()
prs.slide_width = Inches(13.33)
prs.slide_height = Inches(7.5)

slide_layout = prs.slide_layouts[5]  # blank
slide = prs.slides.add_slide(slide_layout)

# Title
title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.3), Inches(0.8))
tf = title_box.text_frame
p = tf.paragraphs[0]
p.text = "Executive Summary"
p.font.size = Pt(28)
p.font.bold = True
p.font.name = 'Arial'

# KPI boxes
left = Inches(0.7)
top = Inches(1.4)
width = Inches(5.5)
height = Inches(2.4)

def add_kpi_box(left, top, headline, subtext):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.clear()
    p1 = tf.paragraphs[0]
    p1.text = headline
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.name = 'Arial'
    p1.font.color.rgb = RGBColor(43, 43, 43)
    p2 = tf.add_paragraph()
    p2.text = subtext
    p2.font.size = Pt(12)
    p2.font.name = 'Arial'
    p2.font.color.rgb = RGBColor(43, 43, 43)
    p2.space_before = Pt(6)

# Add four KPI boxes
add_kpi_box(left, top, zAR(savings_rands), "Estimated annual savings if churn drops slightly")
add_kpi_box(left + Inches(6.0), top, top_ratio_text, "Top LTV:CAC ratio (e.g., Referral)")
add_kpi_box(left, top + Inches(2.6), f"{current_churn:.1f}%" if current_churn is not None else "—", "Current churn rate")
add_kpi_box(left + Inches(6.0), top + Inches(2.6), f"{needed_fte} FTEs", "Needed to launch 30-day activation programme")

pptx_path = os.path.join("outputs", "05_executive_summary_slide.pptx")
prs.save(pptx_path)
print("  ✓ Saved Executive Summary slide:", pptx_path)

print("\nAll done. Outputs saved to 'outputs/' (4 visualisations + exec summary slide).")