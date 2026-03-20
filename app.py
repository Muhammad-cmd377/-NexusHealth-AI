import streamlit as st
import io
import plotly.graph_objects as go
from datetime import datetime
from brain import get_ai_response, build_vitals_context, get_diet_plan, get_exercise_plan
from config import APP_TITLE, APP_ICON
from database import (init_db, add_patient, get_all_patients,
                      get_patient_by_name, save_vitals, get_vitals_history,
                      delete_patient, add_medicine, get_medicines, delete_medicine,
                      update_patient_measurements)

init_db()

st.set_page_config(
    page_title="NexusHealth AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="NexusHealth AI">
<meta name="theme-color" content="#00f5a0">
<link rel="manifest" href="manifest.json">
<link rel="apple-touch-icon" href="icon-192.png">
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/sw.js').then(function(reg) {
      console.log('SW registered');
    });
  });
}
</script>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
:root {
    --bg:      #070a12;
    --surface: #0d1117;
    --card:    #111827;
    --card2:   #161e2e;
    --accent:  #00f5a0;
    --accent2: #00c9ff;
    --danger:  #ff4757;
    --warn:    #ffa502;
    --text:    #e8eaf0;
    --muted:   #5a6278;
    --border:  rgba(255,255,255,0.07);
}
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Outfit', sans-serif !important;
}
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stHeader"] { background: transparent !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }
.nexus-header {
    background: linear-gradient(135deg, #0d1117 0%, #111827 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}
.nexus-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}
.nexus-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}
.nexus-sub { color: var(--muted); font-size: 0.85rem; font-weight: 300; margin: 0.2rem 0 0; }
.nexus-badge {
    background: rgba(0,245,160,0.08);
    border: 1px solid rgba(0,245,160,0.2);
    color: var(--accent);
    font-size: 0.72rem; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; padding: 0.35rem 0.8rem;
    border-radius: 100px; display: flex; align-items: center; gap: 0.4rem;
}
.live-dot {
    width: 6px; height: 6px; background: var(--accent);
    border-radius: 50%; display: inline-block; animation: pulse 2s infinite;
}
@keyframes pulse {
    0%,100% { box-shadow: 0 0 0 0 rgba(0,245,160,0.4); }
    50%      { box-shadow: 0 0 0 5px rgba(0,245,160,0); }
}
.metric-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 14px; padding: 1.2rem 1.4rem;
    position: relative; overflow: hidden; transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-2px); }
.metric-card.danger { border-color: rgba(255,71,87,0.3); }
.metric-card.danger::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: var(--danger);
}
.metric-card.normal::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: var(--accent);
}
.metric-label { font-size: 0.72rem; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: var(--muted); margin-bottom: 0.5rem; }
.metric-value { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 800; letter-spacing: -1px; color: var(--text); line-height: 1; margin-bottom: 0.3rem; }
.metric-value.danger { color: var(--danger); }
.metric-value.accent { color: var(--accent); }
.metric-status { font-size: 0.75rem; font-weight: 500; padding: 0.15rem 0.5rem; border-radius: 100px; display: inline-block; }
.status-normal { background: rgba(0,245,160,0.1); color: var(--accent); }
.status-danger { background: rgba(255,71,87,0.1); color: var(--danger); }
.alert-danger {
    background: rgba(255,71,87,0.08); border: 1px solid rgba(255,71,87,0.25);
    border-left: 3px solid var(--danger); border-radius: 10px;
    padding: 0.8rem 1rem; color: #ff6b6b; font-size: 0.88rem; margin: 0.4rem 0;
}
.alert-success {
    background: rgba(0,245,160,0.06); border: 1px solid rgba(0,245,160,0.2);
    border-left: 3px solid var(--accent); border-radius: 10px;
    padding: 0.8rem 1rem; color: var(--accent); font-size: 0.88rem; margin: 0.4rem 0;
}
.alert-info {
    background: rgba(0,201,255,0.06); border: 1px solid rgba(0,201,255,0.2);
    border-left: 3px solid var(--accent2); border-radius: 10px;
    padding: 0.8rem 1rem; color: var(--accent2); font-size: 0.88rem; margin: 0.4rem 0;
}
.chat-user {
    background: var(--card2); border: 1px solid var(--border);
    border-left: 3px solid var(--accent); border-radius: 0 12px 12px 12px;
    padding: 0.9rem 1.1rem; margin: 0.6rem 0; max-width: 85%; margin-left: auto;
}
.chat-ai {
    background: var(--card); border: 1px solid var(--border);
    border-left: 3px solid var(--muted); border-radius: 12px 12px 12px 0;
    padding: 0.9rem 1.1rem; margin: 0.6rem 0;
    max-width: 90%; white-space: pre-wrap; line-height: 1.7;
}
.chat-label { font-size: 0.68rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 0.4rem; }
.label-user { color: var(--accent); }
.label-ai   { color: var(--muted); }
.sec-label { font-size: 0.68rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: var(--accent); margin-bottom: 0.8rem; padding-bottom: 0.4rem; border-bottom: 1px solid var(--border); }
.patient-card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1rem 1.2rem; position: relative; overflow: hidden; }
.patient-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, var(--accent), var(--accent2)); }
.patient-name { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: var(--accent); margin-bottom: 0.2rem; }
.patient-info { color: var(--muted); font-size: 0.82rem; }
.bmi-card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 1.5rem; text-align: center; }
.bmi-number { font-family: 'Syne', sans-serif; font-size: 3.5rem; font-weight: 800; letter-spacing: -2px; line-height: 1; margin-bottom: 0.5rem; }
.bmi-category { font-size: 1rem; font-weight: 600; padding: 0.3rem 1rem; border-radius: 100px; display: inline-block; margin-bottom: 1rem; }
.med-card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.7rem; display: flex; align-items: flex-start; gap: 1rem; }
.med-icon { width: 42px; height: 42px; background: rgba(0,245,160,0.08); border: 1px solid rgba(0,245,160,0.15); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; flex-shrink: 0; }
.med-name { font-weight: 700; font-size: 0.95rem; color: var(--text); }
.med-detail { font-size: 0.8rem; color: var(--muted); margin-top: 0.2rem; }
.med-time { background: rgba(0,201,255,0.08); border: 1px solid rgba(0,201,255,0.15); color: var(--accent2); font-size: 0.72rem; font-weight: 600; padding: 0.15rem 0.5rem; border-radius: 4px; display: inline-block; margin-top: 0.3rem; }
.plan-card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 1.5rem; white-space: pre-wrap; line-height: 1.8; font-size: 0.92rem; color: var(--text); font-weight: 300; }
.stButton > button { background: var(--accent) !important; color: #000 !important; font-family: 'Outfit', sans-serif !important; font-weight: 700 !important; font-size: 0.88rem !important; border: none !important; border-radius: 8px !important; padding: 0.55rem 1.3rem !important; transition: all 0.2s !important; }
.stButton > button:hover { opacity: 0.85 !important; transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(0,245,160,0.25) !important; }
.stDownloadButton > button { background: transparent !important; color: var(--accent) !important; border: 1px solid rgba(0,245,160,0.3) !important; border-radius: 8px !important; font-weight: 600 !important; }
[data-testid="stTextInput"] input, textarea, [data-testid="stNumberInput"] input { background-color: var(--card) !important; color: var(--text) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; font-family: 'Outfit', sans-serif !important; }
.stTabs [data-baseweb="tab-list"] { background: var(--card) !important; border-radius: 10px !important; padding: 0.3rem !important; gap: 0.2rem !important; border: 1px solid var(--border) !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: var(--muted) !important; border-radius: 7px !important; font-weight: 500 !important; font-size: 0.88rem !important; padding: 0.5rem 1rem !important; border: none !important; }
.stTabs [aria-selected="true"] { background: var(--accent) !important; color: #000 !important; font-weight: 700 !important; }
[data-testid="stForm"] { background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; padding: 1rem !important; }
hr { border-color: var(--border) !important; }
[data-testid="stSidebar"] label { color: var(--muted) !important; font-size: 0.82rem !important; font-weight: 500 !important; }
@media (max-width: 768px) {
    [data-testid="stSidebar"] {
        width: 85vw !important;
        min-width: 0 !important;
    }
    .nexus-title { font-size: 1.3rem !important; }
    .metric-value { font-size: 1.4rem !important; }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.75rem !important;
        padding: 0.4rem 0.6rem !important;
    }
    .nexus-header { padding: 1rem 1.2rem !important; }
    .metric-card { padding: 0.9rem 1rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
defaults = {
    "chat_history":     [],
    "last_ai_response": "",
    "report_ready":     False,
    "current_patient":  None,
    "vitals_saved":     False,
    "diet_plan":        "",
    "exercise_plan":    "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── PDF Generator ─────────────────────────────────────────────────────────────
def generate_pdf(bp_sys, bp_dia, heart_rate, glucose, ai_assessment, patient_name, bmi=None):
    from fpdf import FPDF
    def sanitize(text):
        return text.encode("latin-1", errors="replace").decode("latin-1")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_fill_color(0, 180, 100)
    pdf.rect(0, 0, 210, 3, "F")
    pdf.ln(5)
    pdf.set_text_color(0, 180, 100)
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 12, "NexusHealth AI - Medical Report", ln=True, align="C")
    pdf.set_text_color(120, 120, 120)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Patient: {patient_name}   |   {datetime.now().strftime('%B %d, %Y  %H:%M')}", ln=True, align="C")
    pdf.ln(5)
    pdf.set_draw_color(0, 180, 100)
    pdf.set_line_width(0.4)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)
    pdf.set_text_color(0, 160, 90)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Patient Vitals", ln=True)
    pdf.ln(2)
    vitals_list = [
        ("Blood Pressure", f"{bp_sys}/{bp_dia} mmHg", "ELEVATED" if bp_sys >= 140 else "Normal"),
        ("Heart Rate",     f"{heart_rate} bpm",       ""),
        ("Blood Glucose",  f"{glucose} mg/dL",        "HIGH" if glucose > 140 else "Normal"),
    ]
    if bmi:
        bmi_cat = ("Obese" if bmi >= 30 else "Overweight" if bmi >= 25
                   else "Normal" if bmi >= 18.5 else "Underweight")
        vitals_list.append(("BMI", f"{bmi:.1f}", bmi_cat))
    for lbl, val, sts in vitals_list:
        pdf.set_text_color(150, 150, 150)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(70, 7, lbl + ":", ln=False)
        pdf.set_text_color(210, 210, 210)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(50, 7, val, ln=False)
        if sts:
            clr = (220, 50, 50) if sts in ("ELEVATED", "HIGH", "Obese", "Overweight") else (0, 180, 90)
            pdf.set_text_color(*clr)
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 7, f"  [{sts}]", ln=True)
        else:
            pdf.ln()
    pdf.ln(4)
    pdf.set_draw_color(60, 60, 60)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)
    pdf.set_text_color(0, 160, 90)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "AI Assessment", ln=True)
    pdf.ln(2)
    clean = sanitize(ai_assessment.replace("**","").replace("###","").replace("##","").replace("#","").replace("*","-"))
    pdf.set_text_color(190, 190, 190)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, clean)
    pdf.ln(6)
    pdf.set_draw_color(0, 180, 100)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    pdf.set_text_color(100, 100, 100)
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(0, 5, sanitize("Disclaimer: This report is AI-generated and not a substitute for professional medical advice. Always consult a qualified healthcare provider."))
    buf = io.BytesIO()
    buf.write(bytearray(pdf.output()))
    buf.seek(0)
    return buf.read()

# ── Chart Helper ──────────────────────────────────────────────────────────────
def make_chart(dates, values, label, color, danger_line=None):
    clean = [(d, v) for d, v in zip(dates, values) if v is not None]
    if not clean:
        fig = go.Figure()
        fig.update_layout(paper_bgcolor="#070a12", plot_bgcolor="#0d1117",
                          font=dict(color="#5a6278"), height=240)
        return fig
    dates  = [d for d, v in clean]
    values = [int(v) for d, v in clean]
    latest = values[-1]
    mx     = max(values)
    mn     = min(values)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=values, mode="lines+markers+text",
        line=dict(color=color, width=2.5),
        marker=dict(size=8, color=color),
        text=[str(v) for v in values],
        textposition="top center",
        textfont=dict(color=color, size=10),
    ))
    if danger_line:
        fig.add_hrect(y0=danger_line, y1=max(mx+20, danger_line+30),
            fillcolor="rgba(255,71,87,0.06)", line_width=0,
            annotation_text="⚠️ Danger Zone", annotation_position="top right",
            annotation_font_color="#ff4757", annotation_font_size=10)
        fig.add_hline(y=danger_line, line_dash="dash", line_color="#ff4757",
            line_width=1.5, opacity=0.6,
            annotation_text=f"Limit: {danger_line}", annotation_position="bottom right",
            annotation_font_color="#ff6b7a", annotation_font_size=9)
    fig.add_annotation(x=dates[-1], y=values[-1], text=f"<b>{latest}</b>",
        showarrow=True, arrowhead=2, arrowcolor=color,
        bgcolor="#111827", bordercolor=color, borderwidth=1.5,
        borderpad=4, font=dict(color=color, size=12), xshift=12, yshift=22)
    fig.add_annotation(text=f"Max: {mx}  |  Min: {mn}",
        xref="paper", yref="paper", x=0.01, y=1.12, showarrow=False,
        font=dict(color="#5a6278", size=9), bgcolor="#111827",
        bordercolor="#1e293b", borderwidth=1, borderpad=3)
    fig.update_layout(
        paper_bgcolor="#070a12", plot_bgcolor="#0d1117",
        font=dict(color="#5a6278"), margin=dict(l=20,r=20,t=50,b=20), height=240,
        xaxis=dict(gridcolor="#1e293b", tickfont=dict(size=9, color="#3a4460")),
        yaxis=dict(gridcolor="#1e293b", title=dict(text=label, font=dict(size=9, color="#3a4460"))),
        showlegend=False)
    return fig

# ── BMI Helpers ───────────────────────────────────────────────────────────────
def calc_bmi(weight_kg, height_cm):
    if not height_cm or not weight_kg or height_cm <= 0 or weight_kg <= 0:
        return None
    h = height_cm / 100
    return round(weight_kg / (h * h), 1)

def bmi_category(bmi):
    if bmi < 18.5: return "Underweight", "#00c9ff", "rgba(0,201,255,0.1)"
    if bmi < 25.0: return "Normal",      "#00f5a0", "rgba(0,245,160,0.1)"
    if bmi < 30.0: return "Overweight",  "#ffa502", "rgba(255,165,2,0.1)"
    return               "Obese",        "#ff4757", "rgba(255,71,87,0.1)"

# ── Safe HTML Helper ──────────────────────────────────────────────────────────
def safe(val, suffix=""):
    if val is None or val == 0:
        return "N/A"
    return f"{val}{suffix}"

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sec-label">👤 Patient Profile</div>', unsafe_allow_html=True)
    patients      = get_all_patients()
    patient_names = [p["name"] for p in patients]
    mode = st.radio("", ["Select Patient", "New Patient"],
                    horizontal=True, label_visibility="collapsed")

    if mode == "New Patient":
        with st.form("new_patient_form"):
            new_name = st.text_input("Full Name")
            col_a, col_b = st.columns(2)
            new_age    = col_a.number_input("Age", 1, 120, 30)
            new_gender = col_b.selectbox("Gender", ["Male", "Female", "Other"])
            col_h, col_w = st.columns(2)
            new_height = col_h.number_input("Height (cm)", 50.0, 250.0, 170.0, 0.5)
            new_weight = col_w.number_input("Weight (kg)", 10.0, 300.0, 70.0, 0.5)
            submitted = st.form_submit_button("➕ Add Patient", use_container_width=True)
            if submitted and new_name.strip():
                ok = add_patient(new_name.strip(), new_age, new_gender, new_height, new_weight)
                if ok:
                    st.session_state.current_patient = get_patient_by_name(new_name.strip())
                    st.session_state.chat_history    = []
                    st.session_state.report_ready    = False
                    st.rerun()
                else:
                    st.error("Patient already exists!")
    else:
        if patient_names:
            selected = st.selectbox("Choose Patient", patient_names)
            if st.button("Load Patient →", use_container_width=True):
                st.session_state.current_patient = get_patient_by_name(selected)
                st.session_state.chat_history    = []
                st.session_state.report_ready    = False
                st.session_state.vitals_saved    = False
                st.session_state.diet_plan       = ""
                st.session_state.exercise_plan   = ""
                st.rerun()
        else:
            st.markdown('<div class="alert-info">No patients yet. Create one!</div>',
                        unsafe_allow_html=True)

    if st.session_state.current_patient:
        p    = st.session_state.current_patient
        p_h  = float(p.get("height") or 0)
        p_w  = float(p.get("weight") or 0)
        p_bmi = calc_bmi(p_w, p_h)
        st.markdown("---")

        info_line = f"Age: {p['age']} &nbsp;|&nbsp; {p['gender']}"
        if p_h > 0 and p_w > 0:
            info_line += f"<br>Height: {p_h}cm &nbsp;|&nbsp; Weight: {p_w}kg"
        if p_bmi:
            info_line += f'<br><b style="color:var(--accent)">BMI: {p_bmi}</b>'

        st.markdown(f"""
        <div class="patient-card">
            <div class="patient-name">🩺 {p['name']}</div>
            <div class="patient-info">{info_line}</div>
        </div>""", unsafe_allow_html=True)

        if st.button("🗑 Delete Patient", use_container_width=True):
            delete_patient(p["id"])
            st.session_state.current_patient = None
            st.session_state.chat_history    = []
            st.session_state.report_ready    = False
            st.rerun()

    st.markdown("---")
    st.markdown('<div class="sec-label">📊 Enter Vitals</div>', unsafe_allow_html=True)
    bp_systolic  = st.slider("Systolic BP (mmHg)",   80,  200, 120)
    bp_diastolic = st.slider("Diastolic BP (mmHg)",  40,  130,  80)
    heart_rate   = st.slider("Heart Rate (bpm)",      40,  200,  72)
    glucose      = st.slider("Blood Glucose (mg/dL)", 60,  400,  95)

    if st.session_state.current_patient:
        if st.button("💾 Save Vitals", use_container_width=True):
            save_vitals(st.session_state.current_patient["id"],
                        bp_systolic, bp_diastolic, heart_rate, glucose)
            st.session_state.vitals_saved = True
            st.rerun()

    if st.session_state.get("vitals_saved"):
        st.markdown('<div class="alert-success">✅ Vitals saved!</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<small style='color:#2a3450;font-size:0.72rem'>NexusHealth AI v3.0<br>Powered by Groq + LLaMA 3.3 70B</small>",
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
p_name = (st.session_state.current_patient["name"]
          if st.session_state.current_patient else "No Patient")
st.markdown(f"""
<div class="nexus-header">
    <div>
        <p class="nexus-title">🩺 NexusHealth AI</p>
        <p class="nexus-sub">Professional vitals analysis powered by LLaMA 3.3 70B &nbsp;·&nbsp; {p_name}</p>
    </div>
    <div class="nexus-badge"><span class="live-dot"></span>AI Active</div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.current_patient:
    st.markdown("""
    <div style="text-align:center;padding:5rem 0;">
        <p style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;
                  background:linear-gradient(135deg,#00f5a0,#00c9ff);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            👈 Select or Create a Patient
        </p>
        <p style="font-size:0.95rem;color:#3a4460;">Use the sidebar to get started</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

cp      = st.session_state.current_patient
bmi_val = calc_bmi(cp.get("weight") or 0, cp.get("height") or 0)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📋 Consultation", "📈 Trends", "🗂 History",
    "⚖️ BMI", "💊 Medicines", "🥗 Diet Plan", "🏃 Exercise",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CONSULTATION
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    c1, c2, c3, c4 = st.columns(4)

    def render_metric(col, label, value, unit, is_danger):
        css_class  = "danger" if is_danger else "normal"
        val_class  = "danger" if is_danger else "accent"
        status_txt = "⚠ Elevated" if is_danger else "✓ Normal"
        status_cls = "status-danger" if is_danger else "status-normal"
        col.markdown(f"""
        <div class="metric-card {css_class}">
            <div class="metric-label">{label}</div>
            <div class="metric-value {val_class}">{value}
                <small style="font-size:0.9rem;font-weight:400"> {unit}</small>
            </div>
            <span class="metric-status {status_cls}">{status_txt}</span>
        </div>""", unsafe_allow_html=True)

    render_metric(c1, "SYSTOLIC BP",   bp_systolic,  "mmHg", bp_systolic >= 140)
    render_metric(c2, "DIASTOLIC BP",  bp_diastolic, "mmHg", bp_diastolic >= 90)
    render_metric(c3, "HEART RATE",    heart_rate,   "bpm",  heart_rate > 100 or heart_rate < 60)
    render_metric(c4, "BLOOD GLUCOSE", glucose,      "mg/dL", glucose > 140)

    if bp_systolic >= 140:
        st.markdown('<div class="alert-danger">⚠️ Systolic BP ≥ 140 mmHg — May indicate hypertension. Consult a doctor.</div>', unsafe_allow_html=True)
    if glucose > 140:
        st.markdown('<div class="alert-danger">⚠️ Blood glucose > 140 mg/dL — Elevated levels detected.</div>', unsafe_allow_html=True)
    if bp_systolic < 100:
        st.markdown('<div class="alert-info">ℹ️ Low blood pressure detected. Monitor for dizziness.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="sec-label">💬 Health Consultation</div>', unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user"><div class="chat-label label-user">YOU</div>{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-ai"><div class="chat-label label-ai">NEXUSHEALTH AI</div>{msg["content"]}</div>', unsafe_allow_html=True)

    col_in, col_btn = st.columns([5, 1])
    with col_in:
        user_input = st.text_input("Ask", placeholder="e.g. What do my vitals indicate?",
                                   label_visibility="collapsed", key="user_query")
    with col_btn:
        send = st.button("Send →", use_container_width=True)

    st.markdown('<p style="color:#2a3450;font-size:0.75rem;margin-top:0.3rem">Quick prompts:</p>', unsafe_allow_html=True)
    qcols   = st.columns(4)
    prompts = ["Analyze my vitals", "Am I at risk?", "Lifestyle changes?", "Should I see a doctor?"]
    chosen  = None
    for i, qp in enumerate(prompts):
        if qcols[i].button(qp, key=f"qp_{i}"):
            chosen = qp

    query = chosen or (user_input if send and user_input.strip() else None)
    if query:
        vtx = build_vitals_context(bp_systolic, bp_diastolic, heart_rate, glucose, bmi_val)
        with st.spinner("Analyzing your health data..."):
            reply = get_ai_response(st.session_state.chat_history, vtx, query)
        st.session_state.chat_history.append({"role": "user",      "content": query})
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.session_state.last_ai_response = reply
        st.session_state.report_ready     = True
        st.rerun()

    if st.session_state.report_ready and st.session_state.last_ai_response:
        st.markdown("---")
        st.markdown('<div class="sec-label">📄 Medical Report</div>', unsafe_allow_html=True)
        try:
            pdf_bytes = generate_pdf(bp_systolic, bp_diastolic, heart_rate, glucose,
                                     st.session_state.last_ai_response, cp["name"], bmi_val)
            fname = f"NexusHealth_{cp['name']}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            st.download_button("📥 Download PDF Report", data=pdf_bytes,
                               file_name=fname, mime="application/pdf")
        except Exception as e:
            st.error(f"PDF error: {e}")

    if st.session_state.chat_history:
        if st.button("🗑 Clear Chat"):
            st.session_state.chat_history     = []
            st.session_state.last_ai_response = ""
            st.session_state.report_ready     = False
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — VITALS TRENDS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="sec-label">📈 Vitals Trends</div>', unsafe_allow_html=True)
    history = get_vitals_history(cp["id"], limit=20)
    if len(history) < 2:
        st.markdown('<div style="text-align:center;padding:3rem;color:#3a4460"><p>Save vitals at least twice to see charts.</p></div>', unsafe_allow_html=True)
    else:
        history  = list(reversed(history))
        dates    = [r[5] for r in history]
        sys_vals = [r[1] for r in history]
        dia_vals = [r[2] for r in history]
        hr_vals  = [r[3] for r in history]
        gl_vals  = [r[4] for r in history]
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<p style="color:#3a4460;font-size:0.82rem">Systolic BP</p>', unsafe_allow_html=True)
            st.plotly_chart(make_chart(dates, sys_vals, "Systolic BP", "#00f5a0", 140),
                            use_container_width=True, key="chart_sys")
            st.markdown('<p style="color:#3a4460;font-size:0.82rem">Heart Rate</p>', unsafe_allow_html=True)
            st.plotly_chart(make_chart(dates, hr_vals, "Heart Rate", "#00c9ff"),
                            use_container_width=True, key="chart_hr")
        with col_b:
            st.markdown('<p style="color:#3a4460;font-size:0.82rem">Diastolic BP</p>', unsafe_allow_html=True)
            st.plotly_chart(make_chart(dates, dia_vals, "Diastolic BP", "#ffa502"),
                            use_container_width=True, key="chart_dia")
            st.markdown('<p style="color:#3a4460;font-size:0.82rem">Blood Glucose</p>', unsafe_allow_html=True)
            st.plotly_chart(make_chart(dates, gl_vals, "Glucose", "#ff4757", 140),
                            use_container_width=True, key="chart_gl")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — HISTORY TABLE
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="sec-label">🗂 Vitals History</div>', unsafe_allow_html=True)
    history_all = get_vitals_history(cp["id"], limit=50)

    if not history_all:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:#3a4460">
            <p style="font-size:1.1rem">No History Yet</p>
            <p>Save vitals from the sidebar to start recording history.</p>
        </div>""", unsafe_allow_html=True)
    else:
        recent = history_all[0]
        sc1, sc2, sc3, sc4, sc5 = st.columns(5)

        def small_card(col, label, value, unit):
            col.markdown(f"""
            <div class="metric-card normal" style="padding:0.9rem 1rem">
                <div class="metric-label">{label}</div>
                <div class="metric-value accent" style="font-size:1.3rem">
                    {value}<small style="font-size:0.75rem;font-weight:400"> {unit}</small>
                </div>
            </div>""", unsafe_allow_html=True)

        small_card(sc1, "LATEST SYS BP",  safe(recent[1]), "mmHg")
        small_card(sc2, "LATEST DIA BP",  safe(recent[2]), "mmHg")
        small_card(sc3, "LATEST HR",      safe(recent[3]), "bpm")
        small_card(sc4, "LATEST GLUCOSE", safe(recent[4]), "mg/dL")
        small_card(sc5, "TOTAL RECORDS",  len(history_all), "")

        st.markdown("<br>", unsafe_allow_html=True)

        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            search_date = st.text_input("Filter", placeholder="Filter by date e.g. 2026-03",
                                        label_visibility="collapsed", key="hist_search")
        with col_f2:
            show_danger = st.checkbox("⚠️ Danger readings only", key="hist_danger")

        rows = list(reversed(history_all))
        if search_date:
            rows = [r for r in rows if search_date in str(r[5])]
        if show_danger:
            rows = [r for r in rows if (r[1] and r[1] >= 140) or (r[4] and r[4] > 140)]

        if not rows:
            st.markdown('<div class="alert-info">No records match your filter.</div>', unsafe_allow_html=True)
        else:
            # Table header
            st.markdown("""
            <div style="display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr 1fr 1fr 1.5fr;
                        gap:0.5rem;padding:0.6rem 1rem;
                        background:var(--card2);border-radius:8px 8px 0 0;
                        border:1px solid var(--border);margin-top:0.5rem">
                <span style="font-size:0.7rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted)">PATIENT</span>
                <span style="font-size:0.7rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted)">DATE</span>
                <span style="font-size:0.7rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted)">SYS BP</span>
                <span style="font-size:0.7rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted)">DIA BP</span>
                <span style="font-size:0.7rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted)">HEART RATE</span>
                <span style="font-size:0.7rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted)">GLUCOSE</span>
                <span style="font-size:0.7rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted)">STATUS</span>
            </div>""", unsafe_allow_html=True)

            for i, r in enumerate(rows):
                p_name_h, sys_bp, dia_bp, hr, gluc, rec_at = r

                warnings = []
                if sys_bp and sys_bp >= 140: warnings.append("High BP")
                if gluc   and gluc   > 140:  warnings.append("High Glucose")
                if hr     and hr     > 100:  warnings.append("High HR")

                status_html = (
                    f'<span style="background:rgba(255,71,87,0.1);color:#ff4757;'
                    f'font-size:0.72rem;font-weight:600;padding:0.15rem 0.5rem;border-radius:4px">'
                    f'⚠ {", ".join(warnings)}</span>'
                    if warnings else
                    '<span style="background:rgba(0,245,160,0.1);color:#00f5a0;'
                    'font-size:0.72rem;font-weight:600;padding:0.15rem 0.5rem;border-radius:4px">'
                    '✓ Normal</span>'
                )

                sys_color  = "#ff4757" if sys_bp and sys_bp >= 140 else "#e8eaf0"
                gluc_color = "#ff4757" if gluc   and gluc   > 140  else "#e8eaf0"
                hr_color   = "#ffa502" if hr     and hr     > 100  else "#e8eaf0"
                bg         = "rgba(255,71,87,0.03)" if warnings else "transparent"
                is_last    = (i == len(rows) - 1)

                try:
                    from datetime import datetime as dt
                    d        = dt.strptime(rec_at[:19], "%Y-%m-%d %H:%M:%S")
                    date_fmt = d.strftime("%d %b %Y")
                    time_fmt = d.strftime("%I:%M %p")
                except Exception:
                    date_fmt = str(rec_at)[:10]
                    time_fmt = str(rec_at)[11:16]

                radius = "border-radius:0 0 8px 8px" if is_last else ""

                st.markdown(f"""
                <div style="display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr 1fr 1fr 1.5fr;
                            gap:0.5rem;padding:0.7rem 1rem;background:{bg};
                            border-left:1px solid var(--border);
                            border-right:1px solid var(--border);
                            border-bottom:1px solid var(--border);{radius}">
                    <div style="font-size:0.9rem;font-weight:700;color:var(--accent);align-self:center">
                        {p_name_h}
                    </div>
                    <div>
                        <div style="font-size:0.85rem;font-weight:600;color:var(--text)">{date_fmt}</div>
                        <div style="font-size:0.72rem;color:var(--muted)">{time_fmt}</div>
                    </div>
                    <div style="font-size:0.95rem;font-weight:700;color:{sys_color};align-self:center">{sys_bp if sys_bp else '-'}</div>
                    <div style="font-size:0.95rem;font-weight:700;color:var(--text);align-self:center">{dia_bp if dia_bp else '-'}</div>
                    <div style="font-size:0.95rem;font-weight:700;color:{hr_color};align-self:center">{hr if hr else '-'}</div>
                    <div style="font-size:0.95rem;font-weight:700;color:{gluc_color};align-self:center">{gluc if gluc else '-'}</div>
                    <div style="align-self:center">{status_html}</div>
                </div>""", unsafe_allow_html=True)

        # Summary Stats
        if rows:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="sec-label">📊 Summary Stats</div>', unsafe_allow_html=True)
            valid_sys  = [r[1] for r in rows if r[1]]
            valid_dia  = [r[2] for r in rows if r[2]]
            valid_hr   = [r[3] for r in rows if r[3]]
            valid_gluc = [r[4] for r in rows if r[4]]
            st1, st2, st3, st4 = st.columns(4)

            def stat_card(col, label, vals, unit, danger):
                if not vals: return
                avg  = round(sum(vals) / len(vals), 1)
                mn   = min(vals)
                mx   = max(vals)
                is_d = avg >= danger
                col.markdown(f"""
                <div class="metric-card {'danger' if is_d else 'normal'}" style="padding:0.9rem 1rem">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value {'danger' if is_d else 'accent'}" style="font-size:1.4rem">
                        {avg}<small style="font-size:0.72rem;font-weight:400"> {unit}</small>
                    </div>
                    <div style="font-size:0.75rem;color:var(--muted);margin-top:0.3rem">
                        Min: {mn} &nbsp;|&nbsp; Max: {mx}
                    </div>
                </div>""", unsafe_allow_html=True)

            stat_card(st1, "AVG SYSTOLIC BP",  valid_sys,  "mmHg", 140)
            stat_card(st2, "AVG DIASTOLIC BP", valid_dia,  "mmHg", 90)
            stat_card(st3, "AVG HEART RATE",   valid_hr,   "bpm",  100)
            stat_card(st4, "AVG GLUCOSE",      valid_gluc, "mg/dL", 140)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — BMI
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="sec-label">⚖️ BMI Calculator</div>', unsafe_allow_html=True)
    col_bmi1, col_bmi2 = st.columns(2)
    with col_bmi1:
        h_val = float(cp.get("height") or 0)
        w_val = float(cp.get("weight") or 0)
        height_in = st.number_input("Height (cm)", 50.0, 250.0,
                                    h_val if h_val >= 50.0 else 170.0, 0.5, key="bmi_h")
        weight_in = st.number_input("Weight (kg)", 10.0, 300.0,
                                    w_val if w_val >= 10.0 else 70.0,  0.5, key="bmi_w")
        if st.button("Calculate BMI", use_container_width=True):
            update_patient_measurements(cp["id"], height_in, weight_in)
            st.session_state.current_patient = get_patient_by_name(cp["name"])
            st.rerun()
    bmi_calc = calc_bmi(weight_in, height_in)
    with col_bmi2:
        if bmi_calc:
            bmi_cat, bmi_col, bmi_bg = bmi_category(bmi_calc)
            st.markdown(f"""
            <div class="bmi-card">
                <div class="metric-label">YOUR BMI</div>
                <div class="bmi-number" style="color:{bmi_col}">{bmi_calc}</div>
                <span class="bmi-category" style="background:{bmi_bg};color:{bmi_col}">{bmi_cat}</span>
                <br><br>
                <div style="color:var(--muted);font-size:0.82rem;text-align:left">
                    <div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid var(--border)">
                        <span>Underweight</span><span style="color:#00c9ff">Below 18.5</span></div>
                    <div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid var(--border)">
                        <span>Normal</span><span style="color:#00f5a0">18.5 – 24.9</span></div>
                    <div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid var(--border)">
                        <span>Overweight</span><span style="color:#ffa502">25.0 – 29.9</span></div>
                    <div style="display:flex;justify-content:space-between;padding:0.3rem 0">
                        <span>Obese</span><span style="color:#ff4757">30.0+</span></div>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-info">Enter height and weight to calculate BMI</div>',
                        unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — MEDICINES
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="sec-label">💊 Medicine Tracker</div>', unsafe_allow_html=True)
    col_med1, col_med2 = st.columns(2)
    with col_med1:
        with st.form("med_form"):
            med_name   = st.text_input("Medicine Name", placeholder="e.g. Metformin")
            col_m1, col_m2 = st.columns(2)
            med_dosage = col_m1.text_input("Dosage", placeholder="e.g. 500mg")
            med_freq   = col_m2.selectbox("Frequency",
                ["Once daily","Twice daily","Three times daily","As needed","Weekly"])
            med_time   = st.selectbox("Time of Day",
                ["Morning","Afternoon","Evening","Night","Morning & Night","With meals"])
            med_notes  = st.text_input("Notes (optional)", placeholder="e.g. Take with food")
            if st.form_submit_button("➕ Add Medicine", use_container_width=True):
                if med_name.strip():
                    add_medicine(cp["id"], med_name.strip(), med_dosage,
                                 med_freq, med_time, med_notes)
                    st.rerun()
    with col_med2:
        meds = get_medicines(cp["id"])
        if not meds:
            st.markdown('<div class="alert-info">No medicines added yet.</div>',
                        unsafe_allow_html=True)
        else:
            for med in meds:
                col_mc, col_md = st.columns([5, 1])
                with col_mc:
                    notes_html = (f'<div class="med-detail" style="margin-top:0.3rem">📝 {med["notes"]}</div>'
                                  if med.get("notes") else "")
                    st.markdown(f"""
                    <div class="med-card">
                        <div class="med-icon">💊</div>
                        <div>
                            <div class="med-name">{med['name']}</div>
                            <div class="med-detail">{med['dosage']} &nbsp;·&nbsp; {med['frequency']}</div>
                            <span class="med-time">⏰ {med['time_of_day']}</span>
                            {notes_html}
                        </div>
                    </div>""", unsafe_allow_html=True)
                with col_md:
                    if st.button("🗑", key=f"del_med_{med['id']}"):
                        delete_medicine(med["id"])
                        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — DIET PLAN
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="sec-label">🥗 AI Diet Plan</div>', unsafe_allow_html=True)
    bmi_for_diet = bmi_val or 22.0
    col_d1, col_d2 = st.columns([1, 2])
    with col_d1:
        st.markdown(f"""
        <div class="metric-card normal">
            <div class="metric-label">BASED ON YOUR VITALS</div>
            <div style="font-size:0.85rem;color:var(--muted);margin-top:0.5rem;line-height:1.8">
                BP: {bp_systolic}/{bp_diastolic} mmHg<br>
                Glucose: {glucose} mg/dL<br>
                BMI: {bmi_for_diet:.1f}
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button("🥗 Generate Diet Plan", use_container_width=True):
            with st.spinner("Creating your personalized diet plan..."):
                st.session_state.diet_plan = get_diet_plan(
                    bp_systolic, bp_diastolic, glucose, bmi_for_diet)
            st.rerun()
    with col_d2:
        if st.session_state.diet_plan:
            st.markdown(f'<div class="plan-card">{st.session_state.diet_plan}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center;padding:3rem;color:#3a4460">Click "Generate Diet Plan" to start</div>',
                        unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — EXERCISE PLAN
# ══════════════════════════════════════════════════════════════════════════════
with tab7:
    st.markdown('<div class="sec-label">🏃 AI Exercise Plan</div>', unsafe_allow_html=True)
    bmi_for_ex = bmi_val or 22.0
    col_e1, col_e2 = st.columns([1, 2])
    with col_e1:
        st.markdown(f"""
        <div class="metric-card normal">
            <div class="metric-label">BASED ON YOUR VITALS</div>
            <div style="font-size:0.85rem;color:var(--muted);margin-top:0.5rem;line-height:1.8">
                BP: {bp_systolic}/{bp_diastolic} mmHg<br>
                Heart Rate: {heart_rate} bpm<br>
                BMI: {bmi_for_ex:.1f}
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button("🏃 Generate Exercise Plan", use_container_width=True):
            with st.spinner("Creating your personalized exercise plan..."):
                st.session_state.exercise_plan = get_exercise_plan(
                    bp_systolic, heart_rate, bmi_for_ex)
            st.rerun()
    with col_e2:
        if st.session_state.exercise_plan:
            st.markdown(f'<div class="plan-card">{st.session_state.exercise_plan}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center;padding:3rem;color:#3a4460">Click "Generate Exercise Plan" to start</div>',
                        unsafe_allow_html=True)