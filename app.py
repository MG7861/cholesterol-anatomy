
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Premium Cholesterol Anatomy Simulator", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
:root{--bg:#f6f8fc;--ink:#0f172a;--muted:#64748b;--blue:#2563eb;--red:#dc2626;--green:#16a34a;--amber:#f59e0b;}
.block-container{padding-top:1.4rem;max-width:1500px}.stApp{background:var(--bg)}
.hero{padding:34px;border-radius:34px;background:radial-gradient(circle at top right,rgba(37,99,235,.35),transparent 35%),linear-gradient(135deg,#020617,#0f172a,#1e1b4b);color:white;margin-bottom:24px;box-shadow:0 25px 70px rgba(15,23,42,.22)}
.hero h1{font-size:48px;margin:0;font-weight:850;letter-spacing:-1px}.hero p{color:#cbd5e1;line-height:1.6;max-width:1000px}.hero .pill{display:inline-flex;padding:7px 12px;border-radius:999px;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.1);font-size:13px;color:#bfdbfe;margin-bottom:13px}
.kpi{background:white;border:1px solid #e8eef6;border-radius:26px;padding:22px;box-shadow:0 15px 40px rgba(15,23,42,.08);height:100%}.kpi small{color:#64748b;font-weight:800;text-transform:uppercase;letter-spacing:.08em}.kpi h2{font-size:38px;margin:.25rem 0;font-weight:850}.red{color:#dc2626}.green{color:#16a34a}.blue{color:#2563eb}.amber{color:#f59e0b}.card{background:white;border:1px solid #e8eef6;border-radius:28px;padding:24px;box-shadow:0 15px 40px rgba(15,23,42,.08);margin-bottom:18px}.note{color:#64748b;font-size:14px;line-height:1.55}.badge{display:inline-flex;padding:5px 11px;border-radius:999px;font-size:12px;font-weight:800}.badge-red{background:#fee2e2;color:#991b1b}.badge-green{background:#dcfce7;color:#166534}.badge-blue{background:#dbeafe;color:#1d4ed8}.badge-amber{background:#fef3c7;color:#92400e}
</style>
""", unsafe_allow_html=True)

def r(x, d=1): return round(float(x), d)
def risk_after_ldl_drop(qrisk, drop): return r(qrisk * (0.78 ** max(0, drop)), 1)
def month_risk(ten_year, months):
    rr=ten_year/100
    return r(100*(1-((1-rr)**(months/120))),2)

# Sidebar
st.sidebar.title("Control Room")
age=st.sidebar.number_input("Age",25,90,62)
height_cm=st.sidebar.number_input("Height cm",120,230,192)
weight_kg=st.sidebar.number_input("Weight kg",40,220,105)
qrisk=st.sidebar.number_input("Confirmed QRISK3 %",0.0,60.0,12.0,step=.1)
st.sidebar.divider(); st.sidebar.subheader("Lipids")
total=st.sidebar.number_input("Total cholesterol",1.0,15.0,6.4,step=.1)
ldl=st.sidebar.number_input("LDL",.5,10.0,4.0,step=.1)
hdl=st.sidebar.number_input("HDL",.3,4.0,1.7,step=.1)
tg=st.sidebar.number_input("Triglycerides",.3,10.0,1.8,step=.1)
st.sidebar.divider(); st.sidebar.subheader("Simulation")
weight_loss=st.sidebar.slider("Weight loss goal kg",0,30,10)
statin_reduction=st.sidebar.slider("Statin LDL reduction %",20,60,40)
adherence=st.sidebar.slider("Adherence %",40,100,90)
show_skeleton=st.sidebar.checkbox("Show skeleton / bones", True)
show_arteries=st.sidebar.checkbox("Show arteries / blood flow", True)
show_nerves=st.sidebar.checkbox("Show nerves", True)
show_organs=st.sidebar.checkbox("Show organs", True)
show_joints=st.sidebar.checkbox("Show joints / gout", True)

non_hdl=r(total-hdl,2)
bmi=r(weight_kg/((height_cm/100)**2),1)
effective_statin=statin_reduction*(adherence/100)

lifestyle_ldl=max(.5,ldl-weight_loss*.033)
statin_ldl=max(.5,ldl*(1-effective_statin/100))
combined_ldl=max(.5,lifestyle_ldl*(1-effective_statin/100))

scenarios={
 "Current":{"ldl":r(ldl,2),"risk":r(qrisk,1),"artery":"#ef4444","heart":"#dc2626","plaque":10,"label":"Highest current LDL/non-HDL artery exposure."},
 "Lifestyle":{"ldl":r(lifestyle_ldl,2),"risk":risk_after_ldl_drop(qrisk,ldl-lifestyle_ldl),"artery":"#f59e0b","heart":"#f97316","plaque":6,"label":"Lifestyle improves weight, TG and gout risk; LDL drop is typically modest."},
 "Statin":{"ldl":r(statin_ldl,2),"risk":risk_after_ldl_drop(qrisk,ldl-statin_ldl),"artery":"#84cc16","heart":"#65a30d","plaque":3,"label":"Statin pathway lowers LDL/non-HDL more strongly if clinically suitable."},
 "Combined":{"ldl":r(combined_ldl,2),"risk":risk_after_ldl_drop(qrisk,ldl-combined_ldl),"artery":"#16a34a","heart":"#15803d","plaque":1,"label":"Best modelled pathway: statin + gradual lifestyle change."}
}

st.markdown("""
<div class='hero'>
  <div class='pill'>Premium anatomy layer · local Python prototype</div>
  <h1>Cholesterol Anatomy Command Centre</h1>
  <p>More realistic educational anatomy: skeleton, arteries, nerves, organs, joints/gout, animated blood flow and scenario-driven risk. This is still not a medical scan or diagnostic 3D model.</p>
</div>
""", unsafe_allow_html=True)

c1,c2,c3,c4=st.columns(4)
with c1: st.markdown(f"<div class='kpi'><small>QRISK3</small><h2 class='red'>{qrisk}%</h2><div class='note'>Confirmed baseline</div></div>",unsafe_allow_html=True)
with c2: st.markdown(f"<div class='kpi'><small>LDL</small><h2 class='red'>{ldl}</h2><div class='note'>mmol/L</div></div>",unsafe_allow_html=True)
with c3: st.markdown(f"<div class='kpi'><small>Non-HDL</small><h2 class='amber'>{non_hdl}</h2><div class='note'>mmol/L</div></div>",unsafe_allow_html=True)
with c4: st.markdown(f"<div class='kpi'><small>BMI</small><h2 class='blue'>{bmi}</h2><div class='note'>Current BMI</div></div>",unsafe_allow_html=True)

tab1,tab2,tab3,tab4=st.tabs(["🫀 Premium anatomy", "📊 Risk simulator", "🧠 Body systems", "✅ GP plan"])

with tab1:
    st.subheader("Premium anatomy-style simulator")
    scenario=st.radio("Scenario", list(scenarios.keys()), horizontal=True)
    s=scenarios[scenario]
    plaque_positions=[(210,170),(205,210),(212,250),(172,198),(245,198),(205,315),(180,370),(235,370),(198,125),(222,278)][:s['plaque']]
    plaques="".join([f"<circle cx='{x}' cy='{y}' r='5.5' fill='#facc15' opacity='.95'><title>Plaque / LDL exposure marker</title></circle>" for x,y in plaque_positions])
    skeleton = "" if not show_skeleton else """
      <g opacity='.62' stroke='#dbeafe' stroke-width='3' fill='none'>
        <circle cx='215' cy='58' r='35'/><line x1='215' y1='95' x2='215' y2='335'/>
        <path d='M160 140 Q215 105 270 140'/><path d='M155 168 Q215 130 275 168'/><path d='M160 196 Q215 160 270 196'/>
        <path d='M178 333 Q215 365 252 333'/>
        <line x1='168' y1='145' x2='112' y2='245'/><line x1='262' y1='145' x2='318' y2='245'/>
        <line x1='190' y1='335' x2='158' y2='465'/><line x1='240' y1='335' x2='272' y2='465'/>
      </g>
    """
    nerves = "" if not show_nerves else """
      <g opacity='.7' stroke='#fde047' stroke-width='3' fill='none' stroke-linecap='round'>
        <path d='M215 82 C210 150 220 205 215 335'/>
        <path d='M215 170 C185 195 160 215 130 250'/>
        <path d='M215 170 C245 195 270 215 300 250'/>
        <path d='M215 330 C195 380 178 420 158 468'/>
        <path d='M215 330 C235 380 252 420 272 468'/>
      </g>
    """
    organs = "" if not show_organs else f"""
      <g>
        <ellipse cx='215' cy='177' rx='28' ry='31' fill='{s['heart']}' opacity='.92' class='beat'/><text x='215' y='188' text-anchor='middle' fill='white' font-size='28'>♥</text>
        <ellipse cx='190' cy='235' rx='28' ry='18' fill='#7c3aed' opacity='.75'><title>Liver area: statins work through liver cholesterol pathway</title></ellipse>
        <ellipse cx='245' cy='270' rx='12' ry='18' fill='#38bdf8' opacity='.78'><title>Kidney area: relevant for uric acid and safety checks</title></ellipse>
        <ellipse cx='185' cy='270' rx='12' ry='18' fill='#38bdf8' opacity='.78'><title>Kidney area: relevant for uric acid and safety checks</title></ellipse>
      </g>
    """
    joints = "" if not show_joints else """
      <g fill='#f97316' opacity='.85'>
        <circle cx='112' cy='245' r='7'/><circle cx='318' cy='245' r='7'/><circle cx='158' cy='465' r='7'/><circle cx='272' cy='465' r='7'/><circle cx='178' cy='345' r='6'/><circle cx='252' cy='345' r='6'/>
      </g>
    """
    arteries = "" if not show_arteries else f"""
      <g stroke='{s['artery']}' stroke-width='9' stroke-linecap='round' filter='url(#glow)'>
        <line x1='215' y1='115' x2='215' y2='455'/><line x1='215' y1='182' x2='125' y2='240'/><line x1='215' y1='182' x2='305' y2='240'/><line x1='215' y1='320' x2='160' y2='475'/><line x1='215' y1='320' x2='270' y2='475'/>
      </g>
      <g fill='white' opacity='.95'>
        <circle class='flow' cx='215' cy='128' r='6'/><circle class='flow d1' cx='165' cy='214' r='6'/><circle class='flow d2' cx='265' cy='214' r='6'/><circle class='flow d3' cx='187' cy='390' r='6'/><circle class='flow d4' cx='245' cy='390' r='6'/>
      </g>
      {plaques}
    """
    html=f"""
    <html><head><style>
      body{{margin:0;background:#020617;color:white;font-family:Inter,Arial,sans-serif}}.stage{{height:720px;border-radius:30px;background:radial-gradient(circle at 50% 20%,rgba(37,99,235,.36),transparent 36%),linear-gradient(180deg,#0f172a,#020617);padding:22px;overflow:hidden}}h2{{margin:0 0 6px;font-size:28px}}p{{color:#cbd5e1;line-height:1.45}}svg{{width:100%;height:590px}}.beat{{animation:beat 1.1s infinite;transform-origin:center}}@keyframes beat{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.12)}}}}.flow{{animation:flow 1.3s infinite}}.d1{{animation-delay:.2s}}.d2{{animation-delay:.35s}}.d3{{animation-delay:.5s}}.d4{{animation-delay:.7s}}@keyframes flow{{0%,100%{{opacity:.25;r:4}}50%{{opacity:1;r:8}}}}
    </style></head><body><div class='stage'><h2>{scenario} scenario</h2><p>{s['label']}</p><svg viewBox='0 0 430 540'>
      <defs><filter id='glow'><feGaussianBlur stdDeviation='4' result='blur'/><feMerge><feMergeNode in='blur'/><feMergeNode in='SourceGraphic'/></feMerge></filter></defs>
      <g opacity='.18' fill='#7dd3fc'><circle cx='215' cy='58' r='43'/><rect x='145' y='105' width='140' height='210' rx='64'/><rect x='92' y='128' width='42' height='160' rx='21'/><rect x='296' y='128' width='42' height='160' rx='21'/><rect x='164' y='325' width='40' height='160' rx='20'/><rect x='226' y='325' width='40' height='160' rx='20'/></g>
      {skeleton}{nerves}{arteries}{organs}{joints}
      <text x='20' y='515' fill='#94a3b8' font-size='13'>Layers: skeleton, arteries, nerves, organs, joints. Educational model, not real imaging.</text>
    </svg></div></body></html>
    """
    left,right=st.columns([1.1,1])
    with left: components.html(html,height=760,scrolling=False)
    with right:
        st.markdown(f"""<div class='card'><h2>{scenario}</h2><p class='note'>{s['label']}</p><small>MODELLED 10-YEAR RISK</small><h1 style='color:{s['artery']};font-size:56px;margin:.2rem 0'>{s['risk']}%</h1><p class='note'>LDL: <b>{s['ldl']} mmol/L</b></p></div>""",unsafe_allow_html=True)
        st.progress(min(s['ldl']/4.5,1), text=f"LDL artery load: {s['ldl']} mmol/L")
        st.progress(min(s['risk']/qrisk,1), text=f"Risk intensity: {s['risk']}%")
        st.info("This is a visual high-fidelity educational layer. True 3D bones/nerves/organs requires a licensed 3D anatomy model file.")

with tab2:
    st.subheader("Risk and LDL movement")
    df=pd.DataFrame([{"Scenario":k,"Risk":v['risk'],"LDL":v['ldl']} for k,v in scenarios.items()])
    fig=go.Figure(go.Bar(x=df['Scenario'],y=df['Risk'],marker_color=[v['artery'] for v in scenarios.values()],text=df['Risk'].astype(str)+'%',textposition='outside'))
    fig.update_layout(title="Modelled 10-year risk",height=430,template="plotly_white",yaxis_title="Risk %")
    st.plotly_chart(fig,use_container_width=True)
    fig2=go.Figure(go.Bar(x=df['Scenario'],y=df['LDL'],marker_color=[v['artery'] for v in scenarios.values()],text=df['LDL'],textposition='outside'))
    fig2.update_layout(title="LDL movement",height=430,template="plotly_white",yaxis_title="LDL mmol/L")
    st.plotly_chart(fig2,use_container_width=True)

with tab3:
    st.subheader("Body systems: what is actually affected?")
    systems=[('Heart + coronary arteries','High impact','High LDL/non-HDL affects arteries supplying the heart.'),('Brain + carotid arteries','High impact','Stroke risk relates to blood vessels supplying the brain.'),('Leg arteries','Medium','Reduced blood flow may cause exertional leg pain.'),('Liver','Monitor','Statins work through liver cholesterol pathway.'),('Muscles','Watch','Muscle symptoms can happen; speak to GP if they occur.'),('Joints / gout','Important','Gout affects joints due to uric acid crystals.'),('Kidneys','Check','Kidneys handle uric acid and medication safety.'),('Bones','Indirect','Cholesterol is not mainly a bone disease.'),('Nerves','Indirect','Cholesterol does not usually attack nerves directly.')]
    cols=st.columns(3)
    for i,(title,level,text) in enumerate(systems):
        cls='badge-red' if level=='High impact' else 'badge-green' if level=='Important' else 'badge-blue' if level in ['Monitor','Check'] else 'badge-amber'
        with cols[i%3]: st.markdown(f"<div class='card'><h3>{title}</h3><span class='badge {cls}'>{level}</span><p class='note'>{text}</p></div>",unsafe_allow_html=True)

with tab4:
    st.subheader("GP-ready plan")
    c1,c2,c3=st.columns(3)
    for col,title,items in [(c1,'Weeks 0–2',['Book GP appointment','Discuss statin suitability/alternatives','Baseline bloods: lipids, liver, HbA1c, kidney','Start diet swaps']),(c2,'Weeks 3–8',['Build walking routine','Gradual weight loss, not crash dieting','Monitor gout flares and muscle symptoms','Reduce alcohol, sugar, refined carbs']),(c3,'Weeks 9–12',['Repeat lipid profile','Check non-HDL response','Review weight trend','Adjust plan with GP'])]:
        with col: st.markdown('<div class="card"><h3>'+title+'</h3><ul>'+''.join([f'<li>{x}</li>' for x in items])+'</ul></div>',unsafe_allow_html=True)
    st.warning('Urgent symptoms: chest pain, exertional shoulder/back pain with breathlessness/sweating/nausea, jaw/arm symptoms, one-sided weakness, facial droop or speech problems need urgent medical help.')

st.caption('Educational decision-support only. Not a diagnostic, prescribing, or real imaging tool.')
