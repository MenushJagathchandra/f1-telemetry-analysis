import streamlit as st
import fastf1
import fastf1.plotting
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="F1 Analyzer · Intelligence",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# GLOBAL CSS — Dark racing aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Inter:wght@300;400;500;600&display=swap');

/* ════ ANIMATED CANVAS BACKGROUND ════ */
#f1-bg-canvas {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    z-index: -1 !important;
    pointer-events: none !important;
    background: #04040c !important;
}

/* ════ ROOT TOKENS ════ */
:root {
    --red:    #e8002d;
    --gold:   #ffd700;
    --bg:     #04040c;
    --surface:#0a0a16;
    --card:   rgba(14,14,26,0.82);
    --border: rgba(255,255,255,0.07);
    --text:   #e4e4f0;
    --muted:  #6b6b8a;
    --accent: #00d4ff;
    --green:  #00ff88;
}

/* ════ BASE ════ */
html, body {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif;
    overflow-x: hidden;
}
[data-testid="stAppViewContainer"] {
    background: transparent !important;
    position: relative; z-index: 1;
}
[data-testid="stAppViewContainer"] > .main { background: transparent !important; }
[data-testid="stHeader"] { background: transparent !important; }
/* ════ SIDEBAR — FROSTED GLASS ════ */
[data-testid="stSidebar"] {
    background: rgba(8,8,18,0.75) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(232,0,45,0.15) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
.main .block-container { padding: 0 2.5rem 3rem; max-width: 1600px; position: relative; z-index: 2; }

/* ════ SCROLLBAR ════ */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(232,0,45,.4); border-radius: 3px; }

/* ════ STICKY FROSTED HEADER ════ */
.apex-sticky-header {
    position: sticky;
    top: 0;
    z-index: 999;
    margin: 0 -2.5rem 1.8rem;
    padding: 0 2.5rem;
    background: rgba(4,4,12,0.55);
    backdrop-filter: blur(28px) saturate(180%);
    -webkit-backdrop-filter: blur(28px) saturate(180%);
    border-bottom: 1px solid rgba(232,0,45,0.25);
    box-shadow: 0 4px 30px rgba(0,0,0,0.6), 0 1px 0 rgba(232,0,45,0.3), inset 0 1px 0 rgba(255,255,255,0.04);
}
.apex-sticky-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, transparent 0%, var(--red) 20%, #ff6b00 45%, var(--gold) 55%, var(--red) 80%, transparent 100%);
    background-size: 200% 100%;
    animation: stripe-flow 3s linear infinite;
}
@keyframes stripe-flow { 0%{background-position:200% 0} 100%{background-position:-200% 0} }
.apex-sticky-header::after {
    content: '🏎';
    position: absolute; right: 3rem; top: 50%; transform: translateY(-50%);
    font-size: 3.5rem; opacity: 0.06; filter: blur(1px); pointer-events: none;
}
.apex-header-inner { display:flex; align-items:center; gap:1.5rem; padding:.9rem 0; }
.apex-logo {
    font-family: 'Orbitron', sans-serif; font-size: 1.6rem; font-weight: 900;
    color: #fff; letter-spacing: 3px; text-shadow: 0 0 30px rgba(232,0,45,0.5); flex-shrink:0;
}
.apex-logo span { color: var(--red); }
.apex-header-divider { width:1px; height:28px; background:rgba(255,255,255,0.1); }
.apex-header-sub { font-size:.68rem; text-transform:uppercase; letter-spacing:2.5px; color:var(--muted); line-height:1.4; }
.apex-header-badge {
    margin-left:auto; font-family:'Orbitron',sans-serif; font-size:.6rem; font-weight:700;
    letter-spacing:2px; color:var(--red); border:1px solid rgba(232,0,45,0.4);
    padding:.25rem .7rem; border-radius:20px; background:rgba(232,0,45,0.08); text-transform:uppercase;
}

/* ════ KPI CARDS — FROSTED GLASS ════ */
.kpi-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.kpi {
    flex: 1; min-width: 160px;
    background: rgba(14,14,26,0.6);
    backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px; padding: 1.1rem 1.4rem;
    position: relative; overflow: hidden;
    transition: transform .25s, border-color .25s, box-shadow .25s;
}
.kpi:hover { transform: translateY(-4px); border-color: rgba(232,0,45,0.4); box-shadow: 0 8px 32px rgba(232,0,45,0.15); }
.kpi::after { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,var(--red),transparent); }
.kpi-label { font-size:.72rem; text-transform:uppercase; letter-spacing:1.5px; color:var(--muted); margin-bottom:.4rem; }
.kpi-value { font-family:'Orbitron',sans-serif; font-size:1.3rem; font-weight:700; color:#fff; }
.kpi-sub   { font-size:.8rem; color:var(--muted); margin-top:.2rem; }
.kpi-icon  { position:absolute; right:1rem; top:50%; transform:translateY(-50%); font-size:1.8rem; opacity:.1; }

/* ════ SECTION TITLE ════ */
.section-title { font-family:'Orbitron',sans-serif; font-size:1rem; font-weight:700; color:var(--text); text-transform:uppercase; letter-spacing:2px; padding-bottom:.6rem; border-bottom:1px solid rgba(255,255,255,0.07); margin-bottom:1.2rem; }
.section-title span { color:var(--red); }

/* ════ TABS — FROSTED ════ */
.stTabs [data-baseweb="tab-list"] { background:rgba(10,10,22,0.7) !important; backdrop-filter:blur(12px) !important; border-radius:10px; padding:5px; gap:4px; border:1px solid rgba(255,255,255,0.07) !important; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:var(--muted) !important; font-family:'Orbitron',sans-serif; font-size:.72rem; font-weight:600; letter-spacing:1px; border-radius:7px; padding:.5rem 1.1rem; border:none !important; transition:all .2s; }
.stTabs [aria-selected="true"] { background:var(--red) !important; color:#fff !important; box-shadow:0 2px 12px rgba(232,0,45,0.4) !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top:1.5rem !important; }

/* ════ SIDEBAR ELEMENTS ════ */
.sidebar-logo { font-family:'Orbitron',sans-serif; font-size:1.3rem; font-weight:900; color:#fff; padding:.5rem 0 1.5rem; letter-spacing:1px; }
.sidebar-logo span { color:var(--red) !important; }
.sidebar-section { font-size:.7rem; text-transform:uppercase; letter-spacing:2px; color:var(--muted); margin:1.2rem 0 .5rem; }

/* ════ INPUTS — FROSTED ════ */
.stSelectbox > div > div, .stMultiSelect > div > div { background:rgba(14,14,26,0.7) !important; backdrop-filter:blur(8px) !important; border-color:rgba(255,255,255,0.08) !important; color:var(--text) !important; border-radius:8px !important; }
.stSelectbox label, .stMultiSelect label, .stSlider label, .stRadio label { color:var(--muted) !important; font-size:.8rem !important; text-transform:uppercase; letter-spacing:1px; }

/* ════ BUTTON ════ */
.stButton > button { background:var(--red) !important; color:white !important; border:none !important; border-radius:8px !important; font-family:'Orbitron',sans-serif !important; font-size:.75rem !important; font-weight:700 !important; letter-spacing:1.5px !important; padding:.6rem 1.5rem !important; width:100%; transition:all .2s !important; box-shadow:0 4px 15px rgba(232,0,45,.35) !important; }
.stButton > button:hover { background:#ff1a3d !important; box-shadow:0 6px 24px rgba(232,0,45,.6) !important; transform:translateY(-2px); }

/* ════ DATAFRAME — FROSTED ════ */
.stDataFrame { background:rgba(14,14,26,0.6) !important; backdrop-filter:blur(10px) !important; border-radius:10px; border:1px solid rgba(255,255,255,0.06); overflow:hidden; }
.stDataFrame thead tr th { background:rgba(10,10,22,0.9) !important; color:var(--muted) !important; font-family:'Orbitron',sans-serif; font-size:.7rem; letter-spacing:1px; text-transform:uppercase; }
.stDataFrame tbody tr:hover td { background:rgba(232,0,45,.05) !important; }

/* ════ ALERTS / SPINNER / DIVIDER ════ */
.stAlert { background:rgba(14,14,26,0.7) !important; backdrop-filter:blur(10px) !important; border-radius:10px !important; border-left:3px solid var(--red) !important; }
.stSpinner > div { border-top-color:var(--red) !important; }
hr { border-color:rgba(255,255,255,0.07) !important; margin:1.5rem 0 !important; }

/* ════ PLOTLY CHARTS ════ */
[data-testid="stPlotlyChart"] { border-radius:12px; overflow:hidden; border:1px solid rgba(255,255,255,0.06); background:rgba(10,10,20,0.5) !important; backdrop-filter:blur(8px); }

/* ════ PROGRESS ════ */
.stProgress > div > div { background:var(--red) !important; }

/* ════ BADGES ════ */
.driver-badge { display:inline-block; background:rgba(14,14,26,0.8); border:1px solid rgba(255,255,255,0.1); border-radius:6px; padding:.3rem .7rem; font-family:'Orbitron',sans-serif; font-size:.75rem; font-weight:700; color:#fff; margin:.2rem; letter-spacing:1px; }
.pos-badge { display:inline-flex; align-items:center; justify-content:center; width:28px; height:28px; border-radius:50%; font-family:'Orbitron',sans-serif; font-size:.7rem; font-weight:900; }
.pos-1 { background:var(--gold); color:#000; }
.pos-2 { background:#c0c0c0; color:#000; }
.pos-3 { background:#cd7f32; color:#000; }
.pos-other { background:rgba(255,255,255,0.08); color:var(--text); }

/* ════ WELCOME CARD — FROSTED ════ */
.welcome-card { background:rgba(14,14,26,0.55); backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px); border:1px solid rgba(255,255,255,0.07); border-radius:16px; padding:3rem 2rem; text-align:center; margin-bottom:1rem; position:relative; overflow:hidden; }
.welcome-card::before { content:''; position:absolute; inset:0; background:radial-gradient(ellipse at 60% 0%, rgba(232,0,45,0.08) 0%, transparent 60%), radial-gradient(ellipse at 20% 100%, rgba(0,212,255,0.05) 0%, transparent 60%); pointer-events:none; }
.feature-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; margin-top:1.5rem; }
.feature-item { background:rgba(255,255,255,0.03); backdrop-filter:blur(10px); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:1.2rem; text-align:left; transition:border-color .2s, transform .2s; }
.feature-item:hover { border-color:rgba(232,0,45,0.3); transform:translateY(-2px); }
.feature-item h4 { font-family:'Orbitron',sans-serif; font-size:.8rem; color:var(--red); margin-bottom:.5rem; }
.feature-item p  { font-size:.82rem; color:var(--muted); margin:0; line-height:1.5; }

/* ════ PULSE DOT ════ */
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(.85)} }
.live-dot { display:inline-block; width:7px; height:7px; border-radius:50%; background:var(--green); animation:pulse 1.8s ease-in-out infinite; margin-right:6px; vertical-align:middle; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════
# ANIMATED CANVAS BACKGROUND
# ════════════════════════════════════════════
st.markdown("""
<canvas id="f1-bg-canvas"></canvas>
<script>
(function(){
  console.log('🏎️ F1 Analyzer Background Script Starting...');
  const canvas = document.getElementById('f1-bg-canvas');
  if(!canvas) {
    console.error('❌ Canvas not found!');
    return;
  }
  console.log('✅ Canvas found:', canvas);
  const ctx = canvas.getContext('2d');
  let W, H, particles=[], lines=[], trackElements=[];

  function resize(){ 
    W=canvas.width=window.innerWidth; 
    H=canvas.height=window.innerHeight; 
    console.log(`📏 Canvas resized: ${W}x${H}`);
  }
  resize();
  window.addEventListener('resize', resize);

  class Particle {
    constructor(){ this.reset(true); }
    reset(init){
      this.x = Math.random()*W;
      this.y = init ? Math.random()*H : H+10;
      this.r = Math.random()*1.8+.3;
      this.vy = -(Math.random()*.5+.15);
      this.vx = (Math.random()-.5)*.3;
      this.alpha = Math.random()*.6+.15;
      const colors = ['#e8002d','#ffd700','#ffffff','#00d4ff','#ff6b00'];
      this.color = colors[Math.floor(Math.random()*colors.length)];
    }
    update(){ this.x+=this.vx; this.y+=this.vy; this.alpha-=.0007; if(this.y<-10||this.alpha<=0) this.reset(false); }
    draw(){
      ctx.save(); ctx.globalAlpha=Math.max(0,this.alpha); ctx.fillStyle=this.color;
      ctx.shadowColor=this.color; ctx.shadowBlur=8;
      ctx.beginPath(); ctx.arc(this.x,this.y,this.r,0,Math.PI*2); ctx.fill(); ctx.restore();
    }
  }

  class SpeedLine {
    constructor(){ this.init(); }
    init(){
      this.x = -300;
      this.y = Math.random()*H;
      this.len = Math.random()*200+80;
      this.speed = Math.random()*8+3;
      this.alpha = Math.random()*.15+.04;
      this.width = Math.random()*1.5+.3;
      const colors = ['#e8002d','#ffffff','#00d4ff'];
      this.color = colors[Math.floor(Math.random()*colors.length)];
    }
    update(){ this.x+=this.speed; if(this.x>W+400) this.init(); }
    draw(){
      const grad=ctx.createLinearGradient(this.x,this.y,this.x+this.len,this.y);
      grad.addColorStop(0,'transparent'); grad.addColorStop(.35,this.color); grad.addColorStop(1,'transparent');
      ctx.save(); ctx.globalAlpha=this.alpha; ctx.strokeStyle=grad; ctx.lineWidth=this.width;
      ctx.beginPath(); ctx.moveTo(this.x,this.y); ctx.lineTo(this.x+this.len,this.y); ctx.stroke(); ctx.restore();
    }
  }

  class TrackElement {
    constructor(){
      this.reset();
    }
    reset(){
      this.x = Math.random()*W;
      this.y = Math.random()*H;
      this.size = Math.random()*3+1;
      this.angle = Math.random()*Math.PI*2;
      this.rotationSpeed = (Math.random()-.5)*0.02;
      this.alpha = Math.random()*.3+.1;
      this.type = Math.random()>.5 ? 'tire' : 'flag';
      this.fadeSpeed = Math.random()*.002+.001;
    }
    update(){
      this.angle += this.rotationSpeed;
      this.alpha -= this.fadeSpeed;
      if(this.alpha <= 0) this.reset();
    }
    draw(){
      ctx.save();
      ctx.globalAlpha = Math.max(0, this.alpha);
      ctx.translate(this.x, this.y);
      ctx.rotate(this.angle);
      
      if(this.type === 'tire'){
        // F1 tire mark
        ctx.strokeStyle = '#333';
        ctx.lineWidth = this.size;
        ctx.beginPath();
        ctx.arc(0, 0, this.size*2, 0, Math.PI*2);
        ctx.stroke();
      } else {
        // Checkered flag element
        const squareSize = this.size;
        for(let i = 0; i < 3; i++){
          for(let j = 0; j < 3; j++){
            ctx.fillStyle = (i+j)%2 === 0 ? '#ffffff' : '#000000';
            ctx.fillRect(i*squareSize, j*squareSize, squareSize, squareSize);
          }
        }
      }
      ctx.restore();
    }
  }

  for(let i=0;i<140;i++) particles.push(new Particle());
  for(let i=0;i<22;i++){ const l=new SpeedLine(); l.x=Math.random()*W; lines.push(l); }
  for(let i=0;i<50;i++) trackElements.push(new TrackElement());

  let tick=0;
  function drawGrid(){
    ctx.save(); ctx.strokeStyle='rgba(232,0,45,0.022)'; ctx.lineWidth=1;
    for(let x=0;x<W;x+=90){ ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke(); }
    for(let y=0;y<H;y+=90){ ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke(); }
    ctx.restore();
  }

  function drawGlows(){
    const g1=ctx.createRadialGradient(W*.85,H*.1,0,W*.85,H*.1,W*.38);
    g1.addColorStop(0,'rgba(232,0,45,0.07)'); g1.addColorStop(1,'transparent');
    ctx.fillStyle=g1; ctx.fillRect(0,0,W,H);
    const g2=ctx.createRadialGradient(W*.08,H*.88,0,W*.08,H*.88,W*.28);
    g2.addColorStop(0,'rgba(0,80,220,0.05)'); g2.addColorStop(1,'transparent');
    ctx.fillStyle=g2; ctx.fillRect(0,0,W,H);
    // Breathing center glow
    const pulse=0.5+0.5*Math.sin(tick*0.012);
    const g3=ctx.createRadialGradient(W*.5,H*.5,0,W*.5,H*.5,W*.45);
    g3.addColorStop(0,'rgba(232,0,45,'+(0.015*pulse)+')'); g3.addColorStop(1,'transparent');
    ctx.fillStyle=g3; ctx.fillRect(0,0,W,H);
  }

  function loop(){
    tick++;
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle='#04040c'; ctx.fillRect(0,0,W,H);
    drawGrid(); drawGlows();
    lines.forEach(l=>{ l.update(); l.draw(); });
    particles.forEach(p=>{ p.update(); p.draw(); });
    trackElements.forEach(t=>{ t.update(); t.draw(); });
    requestAnimationFrame(loop);
  }
  loop();
})();
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FASTF1 CACHE
# ─────────────────────────────────────────────
@st.cache_resource
def setup_cache():
    import os
    cache_dir = 'data_cache'
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    fastf1.Cache.enable_cache(cache_dir)
    return True

setup_cache()

# ─────────────────────────────────────────────
# COLOUR HELPERS
# ─────────────────────────────────────────────
COMPOUND_COLORS = {
    'SOFT':         '#e8002d',
    'MEDIUM':       '#ffd700',
    'HARD':         '#e8e8e8',
    'INTERMEDIATE': '#39b54a',
    'WET':          '#0067ff',
    'UNKNOWN':      '#888888',
}

TEAM_COLORS = {
    'Red Bull Racing':   '#3671C6',
    'Mercedes':          '#27F4D2',
    'Ferrari':           '#E8002D',
    'McLaren':           '#FF8000',
    'Aston Martin':      '#358C75',
    'Alpine':            '#FF87BC',
    'Williams':          '#64C4FF',
    'RB':                '#6692FF',
    'Haas F1 Team':      '#B6BABD',
    'Kick Sauber':       '#52E252',
}

PLOTLY_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor='#0f0f1a',
        plot_bgcolor='#0a0a14',
        font=dict(family='Inter, sans-serif', color='#a0a0b8', size=12),
        xaxis=dict(gridcolor='#1a1a2e', showgrid=True, zeroline=False),
        yaxis=dict(gridcolor='#1a1a2e', showgrid=True, zeroline=False),
        legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='#1e1e32', borderwidth=1),
        margin=dict(l=50, r=30, t=50, b=50),
    )
)

def apply_template(fig, height=480, title=''):
    fig.update_layout(
        **PLOTLY_TEMPLATE['layout'],
        height=height,
        title=dict(text=title, font=dict(family='Orbitron, sans-serif', size=13, color='#e4e4f0'), x=0),
        hovermode='x unified',
    )
    return fig

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class='sidebar-logo'><span style='color: #e8002d;'>F1</span> Analyzer</div>
    """, unsafe_allow_html=True)
    st.markdown("<div class='sidebar-section'>Session Configuration</div>", unsafe_allow_html=True)

    year = st.selectbox("Season", options=list(range(2025, 2018, -1)), index=0)

    @st.cache_data
    def get_schedule(y):
        try:
            return fastf1.get_event_schedule(y)
        except:
            return None

    schedule = get_schedule(year)

    if schedule is not None:
        race_names = schedule['EventName'].tolist()
        gp = st.selectbox("Grand Prix", options=race_names,
                          index=race_names.index('Abu Dhabi Grand Prix') if 'Abu Dhabi Grand Prix' in race_names else 0)
        session_type = st.selectbox("Session", options=["Race", "Qualifying", "Sprint", "FP1", "FP2", "FP3"], index=0)
        session_map = {"Race": "R", "Qualifying": "Q", "Sprint": "S", "FP1": "FP1", "FP2": "FP2", "FP3": "FP3"}

        st.markdown("")
        load_btn = st.button("🏁  LOAD SESSION")

        if load_btn:
            with st.spinner(f"Loading {gp} — {session_type}..."):
                try:
                    session = fastf1.get_session(year, gp, session_map[session_type])
                    session.load()
                    st.session_state['session'] = session
                    st.session_state['laps']    = session.laps
                    st.success("Session loaded successfully!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    st.markdown("---")
    st.markdown("<div style='font-size:.7rem;color:#444;text-align:center;'>Powered by FastF1 · <span style='color: #e8002d;'>F1</span> Analyzer</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

# ── Sticky Frosted Header ──
st.markdown("""
<div class='apex-sticky-header'>
  <div class='apex-header-inner'>
    <div class='apex-logo'><span style='color: #e8002d;'>F1</span> Analyzer</div>
    <div class='apex-header-divider'></div>
    <div class='apex-header-sub'>Formula 1<br>Performance Intelligence</div>
    <div class='apex-header-badge'>🏎 <span style='color: #e8002d;'>F1</span> · Live Data</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION LOADED
# ─────────────────────────────────────────────
if 'session' in st.session_state:
    session = st.session_state['session']
    laps    = st.session_state['laps']
    drivers = sorted(laps['Driver'].unique())

    # ── KPI Row ──
    laps_clean = laps.copy()
    laps_clean['LapTime_sec'] = laps_clean['LapTime'].dt.total_seconds()
    laps_clean = laps_clean[(laps_clean['LapTime_sec'] > 60) & (laps_clean['LapTime_sec'] < 300)]

    try:
        fastest_driver = laps_clean.loc[laps_clean['LapTime_sec'].idxmin(), 'Driver']
        fastest_time   = laps_clean['LapTime_sec'].min()
        ft_str = f"{int(fastest_time//60)}:{fastest_time%60:06.3f}"
    except:
        fastest_driver, ft_str = "N/A", "N/A"

    try:
        winner_row = session.results.iloc[0]
        winner = f"{winner_row.get('Abbreviation', winner_row.get('Driver','N/A'))}"
        pole   = session.results.loc[session.results['GridPosition']==1].iloc[0].get('Abbreviation','N/A') if 'GridPosition' in session.results.columns else 'N/A'
    except:
        winner, pole = "N/A", "N/A"

    total_laps = len(laps)
    n_drivers  = len(drivers)

    st.markdown(f"""
    <div class='kpi-row'>
      <div class='kpi'>
        <div class='kpi-label'>Event</div>
        <div class='kpi-value' style='font-size:1rem'>{session.event['EventName']}</div>
        <div class='kpi-sub'>{session.event['Location']} · {year}</div>
        <div class='kpi-icon'>🏟️</div>
      </div>
      <div class='kpi'>
        <div class='kpi-label'>Race Winner</div>
        <div class='kpi-value'>{winner}</div>
        <div class='kpi-sub'>P1 Finisher</div>
        <div class='kpi-icon'>🏆</div>
      </div>
      <div class='kpi'>
        <div class='kpi-label'>Pole Position</div>
        <div class='kpi-value'>{pole}</div>
        <div class='kpi-sub'>Qualifying P1</div>
        <div class='kpi-icon'>⚡</div>
      </div>
      <div class='kpi'>
        <div class='kpi-label'>Fastest Lap</div>
        <div class='kpi-value'>{fastest_driver}</div>
        <div class='kpi-sub'>{ft_str}</div>
        <div class='kpi-icon'>⏱️</div>
      </div>
      <div class='kpi'>
        <div class='kpi-label'>Total Laps</div>
        <div class='kpi-value'>{total_laps:,}</div>
        <div class='kpi-sub'>{n_drivers} drivers</div>
        <div class='kpi-icon'>🔢</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ──
    tab_labels = ["🏁 Results", "📍 Positions", "⏱ Lap Times", "🔧 Strategy", "📡 Telemetry", "📈 Evolution", "📊 Statistics"]
    tabs = st.tabs(tab_labels)

    # ══════════════════════════════════════════
    # TAB 0 — RESULTS
    # ══════════════════════════════════════════
    with tabs[0]:
        st.markdown("<div class='section-title'><span>Session</span> Results</div>", unsafe_allow_html=True)

        try:
            results = session.results.copy()
            display_cols = [c for c in ['Position','Abbreviation','FullName','TeamName','GridPosition','Status','Points'] if c in results.columns]
            results_disp = results[display_cols].copy()

            # Medal badges
            def pos_badge(pos):
                try:
                    p = int(pos)
                    cls = {1:'pos-1', 2:'pos-2', 3:'pos-3'}.get(p,'pos-other')
                    return f"<span class='pos-badge {cls}'>{p}</span>"
                except:
                    return str(pos)

            st.dataframe(
                results_disp.reset_index(drop=True),
                use_container_width=True,
                height=520,
                hide_index=True
            )

            # Podium highlight
            st.markdown("---")
            st.markdown("<div class='section-title'>Podium</div>", unsafe_allow_html=True)
            podium_cols = st.columns(3)
            for i, col in enumerate(podium_cols):
                try:
                    row = results.iloc[i]
                    name = row.get('FullName', row.get('Abbreviation',''))
                    team = row.get('TeamName','')
                    pts  = row.get('Points','')
                    icon = ['🥇','🥈','🥉'][i]
                    col.markdown(f"""
                    <div class='kpi' style='text-align:center'>
                        <div style='font-size:2rem'>{icon}</div>
                        <div class='kpi-value' style='font-size:1rem'>{name}</div>
                        <div class='kpi-sub'>{team}</div>
                        <div style='margin-top:.5rem;font-family:Orbitron;font-size:.8rem;color:#ffd700'>{pts} pts</div>
                    </div>
                    """, unsafe_allow_html=True)
                except:
                    pass
        except Exception as e:
            st.warning(f"Results not available: {e}")

    # ══════════════════════════════════════════
    # TAB 1 — POSITIONS
    # ══════════════════════════════════════════
    with tabs[1]:
        st.markdown("<div class='section-title'><span>Race</span> Position Changes</div>", unsafe_allow_html=True)

        try:
            pos_data = []
            for drv in drivers:
                drv_laps = laps.pick_driver(drv)
                for _, row in drv_laps.iterrows():
                    if pd.notna(row.get('Position')):
                        pos_data.append({'Driver': drv, 'LapNumber': row['LapNumber'], 'Position': row['Position']})

            if pos_data:
                pos_df = pd.DataFrame(pos_data)
                fig = go.Figure()
                palette = px.colors.qualitative.Bold + px.colors.qualitative.Set2
                for idx, drv in enumerate(drivers):
                    d = pos_df[pos_df['Driver']==drv].sort_values('LapNumber')
                    fig.add_trace(go.Scatter(
                        x=d['LapNumber'], y=d['Position'],
                        name=drv,
                        mode='lines',
                        line=dict(color=palette[idx % len(palette)], width=2.5),
                        hovertemplate=f'<b>{drv}</b><br>Lap %{{x}}<br>P%{{y}}<extra></extra>'
                    ))
                fig.update_yaxes(autorange='reversed', dtick=1)
                apply_template(fig, height=540, title='Race Position by Lap')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Position data not available for this session.")
        except Exception as e:
            st.warning(f"Could not generate position chart: {e}")

    # ══════════════════════════════════════════
    # TAB 2 — LAP TIMES
    # ══════════════════════════════════════════
    with tabs[2]:
        st.markdown("<div class='section-title'><span>Lap Time</span> Comparison</div>", unsafe_allow_html=True)

        col_sel, col_gap = st.columns([3,1])
        with col_sel:
            selected_drivers = st.multiselect("Select Drivers", options=drivers, default=drivers[:3])
        with col_gap:
            show_smoothed = st.checkbox("Smooth Lines", value=True)

        if selected_drivers:
            fig = go.Figure()
            palette = px.colors.qualitative.Bold
            lap_stats = []

            for idx, drv in enumerate(selected_drivers):
                drv_laps = laps.pick_driver(drv).copy()
                drv_laps['LapTime_sec'] = drv_laps['LapTime'].dt.total_seconds()
                drv_laps = drv_laps[(drv_laps['LapTime_sec'] > 60) & (drv_laps['LapTime_sec'] < 300)].sort_values('LapNumber')

                color = palette[idx % len(palette)]

                if show_smoothed and len(drv_laps) > 5:
                    y_smooth = drv_laps['LapTime_sec'].rolling(3, center=True).mean()
                    fig.add_trace(go.Scatter(
                        x=drv_laps['LapNumber'], y=drv_laps['LapTime_sec'],
                        mode='markers', name=f'{drv} raw',
                        marker=dict(color=color, size=4, opacity=.35),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                    fig.add_trace(go.Scatter(
                        x=drv_laps['LapNumber'], y=y_smooth,
                        mode='lines', name=drv,
                        line=dict(color=color, width=3),
                        hovertemplate=f'<b>{drv}</b><br>Lap %{{x}}<br>%{{y:.3f}}s<extra></extra>'
                    ))
                else:
                    fig.add_trace(go.Scatter(
                        x=drv_laps['LapNumber'], y=drv_laps['LapTime_sec'],
                        mode='lines+markers', name=drv,
                        line=dict(color=color, width=2.5),
                        marker=dict(size=5),
                        hovertemplate=f'<b>{drv}</b><br>Lap %{{x}}<br>%{{y:.3f}}s<extra></extra>'
                    ))

                lap_stats.append({
                    'Driver': drv,
                    'Fastest (s)': round(drv_laps['LapTime_sec'].min(), 3),
                    'Average (s)': round(drv_laps['LapTime_sec'].mean(), 3),
                    'Std Dev':     round(drv_laps['LapTime_sec'].std(), 3),
                    'Total Laps':  len(drv_laps),
                })

            apply_template(fig, height=500, title='Lap Time Comparison')
            fig.update_yaxes(title='Lap Time (seconds)')
            fig.update_xaxes(title='Lap Number')
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("<div class='section-title' style='margin-top:1.5rem'>Driver Statistics</div>", unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(lap_stats), use_container_width=True, hide_index=True)

            # ── Delta chart ──
            if len(selected_drivers) >= 2:
                st.markdown("<div class='section-title' style='margin-top:1.5rem'><span>Gap</span> to Leader</div>", unsafe_allow_html=True)
                ref_drv = selected_drivers[0]
                ref_laps = laps.pick_driver(ref_drv).copy()
                ref_laps['LapTime_sec'] = ref_laps['LapTime'].dt.total_seconds()
                ref_laps = ref_laps[(ref_laps['LapTime_sec']>60)&(ref_laps['LapTime_sec']<300)].set_index('LapNumber')

                fig2 = go.Figure()
                for idx, drv in enumerate(selected_drivers[1:]):
                    d = laps.pick_driver(drv).copy()
                    d['LapTime_sec'] = d['LapTime'].dt.total_seconds()
                    d = d[(d['LapTime_sec']>60)&(d['LapTime_sec']<300)].set_index('LapNumber')
                    common = d.index.intersection(ref_laps.index)
                    delta = d.loc[common,'LapTime_sec'] - ref_laps.loc[common,'LapTime_sec']
                    color = palette[(idx+1) % len(palette)]
                    fig2.add_trace(go.Bar(x=delta.index, y=delta.values, name=f'{drv} vs {ref_drv}',
                                         marker_color=color, opacity=.8))

                apply_template(fig2, height=320, title=f'Lap Delta vs {ref_drv}')
                fig2.update_yaxes(title='Delta (s)')
                fig2.update_xaxes(title='Lap Number')
                fig2.add_hline(y=0, line_color='#ffffff', line_dash='dash', opacity=.3)
                st.plotly_chart(fig2, use_container_width=True)

    # ══════════════════════════════════════════
    # TAB 3 — STRATEGY
    # ══════════════════════════════════════════
    with tabs[3]:
        st.markdown("<div class='section-title'><span>Tyre</span> Strategy</div>", unsafe_allow_html=True)

        # All-drivers strategy overview
        try:
            strat_drivers = sorted(laps['Driver'].unique())
            fig_strat = go.Figure()

            for i, drv in enumerate(strat_drivers):
                drv_laps = laps.pick_driver(drv).copy()
                drv_laps['LapTime_sec'] = drv_laps['LapTime'].dt.total_seconds()
                drv_laps = drv_laps[drv_laps['LapTime_sec'] < 300]

                stints = drv_laps.groupby('Stint').agg(
                    start=('LapNumber','min'),
                    end=('LapNumber','max'),
                    compound=('Compound','first'),
                    laps=('LapNumber','count')
                ).reset_index()

                for _, stint in stints.iterrows():
                    comp = str(stint['compound']).upper()
                    color = COMPOUND_COLORS.get(comp, '#888')
                    fig_strat.add_trace(go.Bar(
                        x=[stint['end'] - stint['start'] + 1],
                        y=[drv],
                        base=[stint['start']],
                        orientation='h',
                        name=comp,
                        marker_color=color,
                        marker_line=dict(color='#080810', width=1),
                        showlegend=False,
                        hovertemplate=f'<b>{drv}</b><br>{comp}<br>L{stint["start"]}–L{stint["end"]} ({stint["laps"]} laps)<extra></extra>',
                        width=.7,
                    ))

            # Legend traces
            for comp, col in COMPOUND_COLORS.items():
                fig_strat.add_trace(go.Bar(x=[None], y=[None], name=comp,
                                           marker_color=col, orientation='h'))

            apply_template(fig_strat, height=max(380, len(strat_drivers)*28), title='Race Tyre Strategy — All Drivers')
            fig_strat.update_xaxes(title='Lap Number')
            fig_strat.update_layout(barmode='overlay', bargap=.3, legend=dict(orientation='h', yanchor='bottom', y=1.01))
            st.plotly_chart(fig_strat, use_container_width=True)
        except Exception as e:
            st.warning(f"Strategy chart: {e}")

        # Per-driver degradation
        st.markdown("<div class='section-title' style='margin-top:1.5rem'><span>Tyre</span> Degradation</div>", unsafe_allow_html=True)
        strategy_driver = st.selectbox("Driver", options=strat_drivers, key='strat_drv')

        drv_laps = laps.pick_driver(strategy_driver).copy()
        drv_laps['LapTime_sec'] = drv_laps['LapTime'].dt.total_seconds()
        drv_laps = drv_laps[(drv_laps['LapTime_sec']>60)&(drv_laps['LapTime_sec']<300)]

        fig_deg = go.Figure()
        for stint in sorted(drv_laps['Stint'].unique()):
            sd = drv_laps[drv_laps['Stint']==stint]
            comp = str(sd['Compound'].iloc[0]).upper() if len(sd)>0 else 'UNKNOWN'
            color = COMPOUND_COLORS.get(comp,'#888')
            fig_deg.add_trace(go.Scatter(
                x=sd['TyreLife'], y=sd['LapTime_sec'],
                mode='lines+markers', name=f'Stint {int(stint)} ({comp})',
                line=dict(color=color, width=2.5),
                marker=dict(size=6, color=color),
                hovertemplate=f'Tyre Age: %{{x}}<br>Lap Time: %{{y:.3f}}s<extra></extra>'
            ))
        apply_template(fig_deg, height=420, title=f'{strategy_driver} — Tyre Degradation')
        fig_deg.update_xaxes(title='Tyre Age (Laps)')
        fig_deg.update_yaxes(title='Lap Time (s)')
        st.plotly_chart(fig_deg, use_container_width=True)

    # ══════════════════════════════════════════
    # TAB 4 — TELEMETRY
    # ══════════════════════════════════════════
    with tabs[4]:
        st.markdown("<div class='section-title'><span>Driver</span> Telemetry</div>", unsafe_allow_html=True)

        c1, c2 = st.columns([2,2])
        with c1:
            driver_tel = st.selectbox("Driver", options=drivers, key='tel_drv')
        with c2:
            compare_driver = st.selectbox("Compare With (optional)", options=['None'] + [d for d in drivers if d != driver_tel], key='tel_cmp')

        drv_laps = laps.pick_driver(driver_tel)
        lap_nums = sorted(drv_laps['LapNumber'].dropna().astype(int).tolist())
        lap_choice = st.selectbox("Lap", options=['Fastest'] + lap_nums, key='tel_lap')

        try:
            if lap_choice == 'Fastest':
                lap1 = drv_laps.pick_fastest()
            else:
                lap1 = drv_laps[drv_laps['LapNumber'] == lap_choice].iloc[0]

            tel1 = lap1.get_telemetry().add_distance()

            lap2 = None
            if compare_driver != 'None':
                try:
                    cmp_laps = laps.pick_driver(compare_driver)
                    if lap_choice == 'Fastest':
                        lap2 = cmp_laps.pick_fastest()
                    else:
                        lap2 = cmp_laps[cmp_laps['LapNumber'] == lap_choice].iloc[0]
                    tel2 = lap2.get_telemetry().add_distance()
                except:
                    tel2, lap2 = None, None

            # Subplots: Speed, Throttle, Brake, Gear, RPM, DRS
            channels = [('Speed','Speed (km/h)'), ('Throttle','Throttle (%)'), ('Brake','Brake'),
                        ('nGear','Gear'), ('RPM','RPM'), ('DRS','DRS')]

            fig_tel = make_subplots(rows=3, cols=2,
                                    subplot_titles=[c[1] for c in channels],
                                    vertical_spacing=.1, horizontal_spacing=.08)

            positions = [(1,1),(1,2),(2,1),(2,2),(3,1),(3,2)]

            for (ch, label), (r, c) in zip(channels, positions):
                if ch in tel1.columns:
                    fig_tel.add_trace(go.Scatter(
                        x=tel1['Distance'], y=tel1[ch],
                        name=driver_tel, line=dict(color='#e8002d', width=2),
                        showlegend=(r==1 and c==1),
                    ), row=r, col=c)
                if lap2 is not None and tel2 is not None and ch in tel2.columns:
                    fig_tel.add_trace(go.Scatter(
                        x=tel2['Distance'], y=tel2[ch],
                        name=compare_driver, line=dict(color='#00d4ff', width=2, dash='dash'),
                        showlegend=(r==1 and c==1),
                    ), row=r, col=c)

            fig_tel.update_layout(
                **PLOTLY_TEMPLATE['layout'],
                height=750,
                title=dict(text=f"Telemetry — {driver_tel}" + (f" vs {compare_driver}" if compare_driver!='None' else ""),
                           font=dict(family='Orbitron', size=13, color='#e4e4f0'), x=0),
            )
            for i in range(1, 7):
                fig_tel.update_xaxes(gridcolor='#1a1a2e', row=(i-1)//2+1, col=(i-1)%2+1)
                fig_tel.update_yaxes(gridcolor='#1a1a2e', row=(i-1)//2+1, col=(i-1)%2+1)

            st.plotly_chart(fig_tel, use_container_width=True)

            # ── Gear map ──
            st.markdown("<div class='section-title' style='margin-top:1.5rem'>Gear Shift Map</div>", unsafe_allow_html=True)
            if 'X' in tel1.columns and 'Y' in tel1.columns and 'nGear' in tel1.columns:
                gear_colors = ['#440154','#3b528b','#21918c','#5ec962','#fde725','#f77f00','#e8002d','#9b0000']
                fig_gear_map = go.Figure()
                for g in sorted(tel1['nGear'].dropna().unique()):
                    d = tel1[tel1['nGear']==g]
                    fig_gear_map.add_trace(go.Scatter(
                        x=d['X'], y=d['Y'],
                        mode='markers',
                        name=f'Gear {int(g)}',
                        marker=dict(color=gear_colors[int(g)-1 if int(g)<=8 else 0], size=3),
                    ))
                apply_template(fig_gear_map, height=440, title=f'{driver_tel} Gear Usage Map')
                fig_gear_map.update_xaxes(visible=False)
                fig_gear_map.update_yaxes(visible=False)
                fig_gear_map.update_layout(plot_bgcolor='#080810')
                st.plotly_chart(fig_gear_map, use_container_width=True)

        except Exception as e:
            st.warning(f"Telemetry error: {e}")

    # ══════════════════════════════════════════
    # TAB 5 — EVOLUTION
    # ══════════════════════════════════════════
    with tabs[5]:
        st.markdown("<div class='section-title'><span>Track</span> Evolution</div>", unsafe_allow_html=True)

        try:
            evo_data = []
            for drv in drivers:
                d = laps.pick_driver(drv).copy()
                d['LapTime_sec'] = d['LapTime'].dt.total_seconds()
                d = d[(d['LapTime_sec']>60)&(d['LapTime_sec']<300)]
                evo_data.append(d)

            evo_df = pd.concat(evo_data)

            # Rolling 5-lap avg per driver
            fig_evo = go.Figure()
            palette = px.colors.qualitative.Bold + px.colors.qualitative.Pastel
            for idx, drv in enumerate(drivers):
                d = evo_df[evo_df['Driver']==drv].sort_values('LapNumber')
                if len(d) < 3:
                    continue
                rolled = d.set_index('LapNumber')['LapTime_sec'].rolling(5, center=True).mean()
                fig_evo.add_trace(go.Scatter(
                    x=rolled.index, y=rolled.values,
                    name=drv,
                    mode='lines',
                    line=dict(color=palette[idx % len(palette)], width=2),
                    hovertemplate=f'<b>{drv}</b><br>Lap %{{x}}<br>%{{y:.3f}}s<extra></extra>'
                ))

            apply_template(fig_evo, height=520, title='Track Evolution (5-Lap Rolling Average)')
            fig_evo.update_yaxes(title='Lap Time (s)')
            fig_evo.update_xaxes(title='Lap Number')
            st.plotly_chart(fig_evo, use_container_width=True)

            # Compound performance box plot
            st.markdown("<div class='section-title' style='margin-top:1.5rem'><span>Compound</span> Performance</div>", unsafe_allow_html=True)
            fig_box = go.Figure()
            for comp in sorted(evo_df['Compound'].dropna().unique()):
                color = COMPOUND_COLORS.get(str(comp).upper(),'#888888')
                d = evo_df[evo_df['Compound']==comp]['LapTime_sec']
                fig_box.add_trace(go.Box(
                    y=d, name=comp,
                    boxmean='sd',
                    marker_color=color,
                    line_color=color,
                    fillcolor=color.replace(')', ',0.2)').replace('rgb', 'rgba') if 'rgb' in color else f'rgba{tuple(int(color[i:i+2], 16) for i in (1, 3, 5)) + (0.2,)}'.replace(' ', ''),
                ))
            apply_template(fig_box, height=420, title='Lap Time by Tyre Compound')
            fig_box.update_yaxes(title='Lap Time (s)')
            st.plotly_chart(fig_box, use_container_width=True)

        except Exception as e:
            st.warning(f"Evolution error: {e}")

    # ══════════════════════════════════════════
    # TAB 6 — STATISTICS
    # ══════════════════════════════════════════
    with tabs[6]:
        st.markdown("<div class='section-title'><span>Session</span> Statistics</div>", unsafe_allow_html=True)

        laps_s = laps.copy()
        laps_s['LapTime_sec'] = laps_s['LapTime'].dt.total_seconds()
        laps_s = laps_s[(laps_s['LapTime_sec']>60)&(laps_s['LapTime_sec']<300)]

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("<div class='section-title'>⚡ Fastest Laps</div>", unsafe_allow_html=True)
            fastest = laps_s.groupby('Driver')['LapTime_sec'].min().sort_values().head(10).reset_index()
            fastest.columns = ['Driver','Time (s)']
            fastest['Time (s)'] = fastest['Time (s)'].round(3)
            st.dataframe(fastest, use_container_width=True, hide_index=True)

        with c2:
            st.markdown("<div class='section-title'>📊 Average Pace</div>", unsafe_allow_html=True)
            avg_pace = laps_s.groupby('Driver')['LapTime_sec'].mean().sort_values().head(10).reset_index()
            avg_pace.columns = ['Driver','Avg (s)']
            avg_pace['Avg (s)'] = avg_pace['Avg (s)'].round(3)
            st.dataframe(avg_pace, use_container_width=True, hide_index=True)

        with c3:
            st.markdown("<div class='section-title'>🎯 Consistency</div>", unsafe_allow_html=True)
            consist = laps_s.groupby('Driver')['LapTime_sec'].std().sort_values().head(10).reset_index()
            consist.columns = ['Driver','Std Dev (s)']
            consist['Std Dev (s)'] = consist['Std Dev (s)'].round(3)
            st.dataframe(consist, use_container_width=True, hide_index=True)

        # Pace comparison bar chart
        st.markdown("<div class='section-title' style='margin-top:1.5rem'><span>Pace</span> Overview</div>", unsafe_allow_html=True)

        pace_all = laps_s.groupby('Driver').agg(
            fastest=('LapTime_sec','min'),
            average=('LapTime_sec','mean'),
        ).reset_index().sort_values('fastest')

        fig_pace = go.Figure()
        fig_pace.add_trace(go.Bar(
            x=pace_all['Driver'], y=pace_all['fastest'],
            name='Fastest', marker_color='#e8002d',
            hovertemplate='%{x}<br>Fastest: %{y:.3f}s<extra></extra>'
        ))
        fig_pace.add_trace(go.Bar(
            x=pace_all['Driver'], y=pace_all['average'],
            name='Average', marker_color='#ffd700',
            hovertemplate='%{x}<br>Average: %{y:.3f}s<extra></extra>'
        ))
        apply_template(fig_pace, height=420, title='Fastest vs Average Lap Per Driver')
        fig_pace.update_layout(barmode='group')
        fig_pace.update_yaxes(title='Lap Time (s)')
        st.plotly_chart(fig_pace, use_container_width=True)

        # Lap count per driver
        st.markdown("<div class='section-title' style='margin-top:1.5rem'><span>Laps</span> Completed</div>", unsafe_allow_html=True)
        lap_counts = laps_s.groupby('Driver').size().sort_values(ascending=False).reset_index()
        lap_counts.columns = ['Driver','Laps']

        fig_lc = go.Figure(go.Bar(
            x=lap_counts['Driver'], y=lap_counts['Laps'],
            marker_color='#00d4ff',
            hovertemplate='%{x}<br>%{y} laps<extra></extra>'
        ))
        apply_template(fig_lc, height=320, title='Total Laps Completed per Driver')
        fig_lc.update_yaxes(title='Laps')
        st.plotly_chart(fig_lc, use_container_width=True)

# ─────────────────────────────────────────────
# WELCOME SCREEN
# ─────────────────────────────────────────────
else:
    st.markdown("""
    <div class='welcome-card'>
        <div style='font-size:3.5rem;margin-bottom:.5rem'>🏎️</div>
        <div style='font-family:Orbitron,sans-serif;font-size:1.5rem;font-weight:900;color:#fff;margin-bottom:.5rem'>
            Welcome to <span style='color:#e8002d'>APEX</span>
        </div>
        <div style='color:#6b6b8a;max-width:500px;margin:0 auto;line-height:1.7'>
            Select a season, Grand Prix, and session type from the sidebar,
            then click <strong style='color:#fff'>Load Session</strong> to begin your analysis.
        </div>
        <div class='feature-grid'>
            <div class='feature-item'>
                <h4>🏁 Race Results</h4>
                <p>Full finishing order, podium highlights, grid vs finish position comparisons.</p>
            </div>
            <div class='feature-item'>
                <h4>📍 Position Tracker</h4>
                <p>Live lap-by-lap position changes across the entire field throughout the race.</p>
            </div>
            <div class='feature-item'>
                <h4>⏱ Lap Analysis</h4>
                <p>Side-by-side lap time comparison with smoothing and delta to leader charts.</p>
            </div>
            <div class='feature-item'>
                <h4>🔧 Tyre Strategy</h4>
                <p>Full-grid strategy overview with per-driver degradation curves.</p>
            </div>
            <div class='feature-item'>
                <h4>📡 Telemetry</h4>
                <p>Speed, throttle, brake, gear, RPM & DRS traces with head-to-head driver comparison.</p>
            </div>
            <div class='feature-item'>
                <h4>📊 Statistics</h4>
                <p>Fastest laps, average pace, consistency rankings, and compound performance.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)