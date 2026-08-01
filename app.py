"""
Pantry to Plate — AI sous-chef, Streamlit edition.

Run locally:
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=sk-ant-...   (or put it in .streamlit/secrets.toml)
    streamlit run app.py
"""

import json
import os
import time

import anthropic
import streamlit as st

# ──────────────────────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pantry to Plate",
    page_icon="🍳",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────
# Global styles — dark night-kitchen theme with animated copper pot
# ──────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,400;1,9..144,600&family=Outfit:wght@300;400;500;600;700&display=swap');

:root{
  --night:#16130f; --panel:#221d16; --panel-edge:#362d21;
  --copper:#d98e4a; --copper-hot:#f2a65a; --copper-deep:#a8642a;
  --flame:#ff8a3d; --flame-core:#ffc46b;
  --magic:#b78cff; --magic-2:#7ee0d2;
  --cream:#faf4e8; --ink:#241d14; --ink-2:#5d5344; --ink-3:#94897a;
}

html, body, .stApp{
  background:
    radial-gradient(90% 70% at 50% 115%, rgba(255,138,61,0.09), transparent 60%),
    var(--night) !important;
  font-family:'Outfit',sans-serif;
}
#MainMenu, footer, header{ visibility:hidden; }
.block-container{ padding-top:2.4rem; padding-bottom:5rem; max-width:880px; }

/* hero */
.hero-badge{
  display:inline-flex; align-items:center; gap:8px;
  border:1px solid var(--panel-edge); background:rgba(255,255,255,0.03);
  border-radius:999px; padding:8px 18px;
  font-size:12.5px; font-weight:500; color:#cdbfa8;
}
.flame-dot{
  width:8px; height:8px; border-radius:50%; background:var(--flame);
  animation:flicker 1.6s ease-in-out infinite;
}
@keyframes flicker{
  0%,100%{ box-shadow:0 0 6px 2px rgba(255,138,61,.5); transform:scale(1); }
  50%{ box-shadow:0 0 12px 4px rgba(255,138,61,.8); transform:scale(1.2); }
}
.hero-title{
  font-family:'Fraunces',serif; font-weight:600;
  font-size:clamp(40px,6.5vw,64px); line-height:1.04;
  letter-spacing:-0.025em; color:var(--cream);
  margin:18px 0 14px; animation:fadeUp .7s ease both;
}
.hero-title .glow{
  font-style:italic;
  background:linear-gradient(115deg,var(--flame-core),var(--copper-hot) 55%,var(--flame));
  -webkit-background-clip:text; background-clip:text; color:transparent;
}
.hero-sub{
  font-size:16.5px; font-weight:300; line-height:1.65; color:#b6a98f;
  max-width:52ch; animation:fadeUp .7s .1s ease both;
}
.hero-sub strong{ color:var(--cream); font-weight:500; }
@keyframes fadeUp{ from{opacity:0; transform:translateY(16px);} to{opacity:1; transform:translateY(0);} }

/* ═══ the pot ═══ */
.stove{ position:relative; height:280px; display:flex; justify-content:center; align-items:flex-end; margin:6px auto 2px; }
.pot-scene{ position:relative; width:340px; height:270px; }
.wisp{
  position:absolute; top:12px; width:5px; height:46px; border-radius:6px;
  background:linear-gradient(to top, rgba(250,244,232,.28), transparent);
  filter:blur(2px); opacity:0; animation:wisp 3s ease-in-out infinite;
}
.cooking .wisp{ animation-duration:1.3s; background:linear-gradient(to top, rgba(250,244,232,.5), transparent); }
.wisp.w1{ left:44%; }
.wisp.w2{ left:52%; animation-delay:1s; height:60px; }
.wisp.w3{ left:60%; animation-delay:1.9s; height:40px; }
@keyframes wisp{
  0%{ transform:translateY(10px) scaleY(.7); opacity:0; }
  25%{ opacity:.9; }
  100%{ transform:translateY(-46px) scaleY(1.3) translateX(8px); opacity:0; }
}
.lid{
  position:absolute; left:50%; top:68px; transform:translateX(-50%);
  width:216px; height:34px; z-index:5; transform-origin:80% 100%;
  transition:transform .7s cubic-bezier(.3,1.3,.4,1), opacity .5s;
}
.cooking .lid{ animation:lidRattle .5s ease-in-out infinite; }
.revealing .lid{ transform:translateX(-50%) translateY(-120px) rotate(24deg); opacity:0; }
@keyframes lidRattle{
  0%,100%{ transform:translateX(-50%) translateY(0) rotate(0); }
  25%{ transform:translateX(calc(-50% - 1.5px)) translateY(-2.5px) rotate(-.8deg); }
  75%{ transform:translateX(calc(-50% + 1.5px)) translateY(-1.5px) rotate(.7deg); }
}
.lid .dome{
  position:absolute; inset:8px 0 0; border-radius:100px 100px 8px 8px;
  background:linear-gradient(180deg,#f0b877,var(--copper) 55%,var(--copper-deep));
  box-shadow:inset 0 2px 3px rgba(255,255,255,.5), 0 3px 8px rgba(0,0,0,.4);
}
.lid .knob{
  position:absolute; left:50%; top:0; transform:translateX(-50%);
  width:26px; height:14px; border-radius:8px 8px 3px 3px;
  background:linear-gradient(180deg,#5c4326,#3a2a16);
  box-shadow:0 2px 4px rgba(0,0,0,.5);
}
.pot{ position:absolute; left:50%; top:94px; transform:translateX(-50%); width:230px; height:120px; z-index:4; }
.pot-body{
  position:absolute; inset:0; border-radius:14px 14px 60px 60px;
  background:linear-gradient(180deg,#e8a35e 0%,var(--copper) 30%,var(--copper-deep) 80%,#7c4a20);
  box-shadow:inset 0 3px 4px rgba(255,255,255,.4), inset 0 -8px 16px rgba(0,0,0,.3), 0 16px 32px -8px rgba(0,0,0,.6);
}
.pot-rim{
  position:absolute; top:-4px; left:-8px; right:-8px; height:14px; border-radius:8px;
  background:linear-gradient(180deg,#f5c084,var(--copper-deep));
  box-shadow:0 2px 5px rgba(0,0,0,.4), inset 0 1px 2px rgba(255,255,255,.5);
}
.handle{ position:absolute; top:18px; width:34px; height:46px; border:8px solid var(--copper-deep); border-radius:20px; }
.handle.left{ left:-34px; border-right:none; border-radius:20px 0 0 20px; }
.handle.right{ right:-34px; border-left:none; border-radius:0 20px 20px 0; }
.pot-shine{
  position:absolute; top:18px; left:22px; width:26px; height:66px; border-radius:20px;
  background:linear-gradient(180deg, rgba(255,255,255,.4), transparent); filter:blur(3px);
}
.bubbles{
  position:absolute; left:50%; top:86px; transform:translateX(-50%);
  width:190px; height:16px; z-index:3; opacity:0; transition:opacity .3s;
}
.cooking .bubbles{ opacity:1; }
.bubble{
  position:absolute; bottom:0; border-radius:50%;
  background:radial-gradient(circle at 35% 30%, #fff8, var(--flame-core));
  animation:bubblePop 1.1s ease-in infinite; opacity:0;
}
.magic .bubble{ background:radial-gradient(circle at 35% 30%, #fff8, var(--magic-2)); }
@keyframes bubblePop{
  0%{ transform:translateY(4px) scale(.4); opacity:0; }
  40%{ opacity:.9; }
  100%{ transform:translateY(-14px) scale(1.1); opacity:0; }
}
.burner{
  position:absolute; left:50%; top:212px; transform:translateX(-50%);
  width:190px; height:46px; z-index:2;
  display:flex; justify-content:center; gap:7px; align-items:flex-end; opacity:.85;
}
.flame{
  width:14px; height:26px;
  border-radius:50% 50% 50% 50% / 62% 62% 38% 38%;
  background:linear-gradient(to top, var(--flame) 15%, var(--flame-core) 70%, #fff3d6);
  transform-origin:bottom center;
  animation:flameDance .5s ease-in-out infinite alternate;
  filter:blur(.5px);
}
.magic .flame{ background:linear-gradient(to top, var(--magic) 10%, var(--magic-2) 75%, #f2fffb); }
.flame:nth-child(odd){ height:20px; animation-duration:.42s; }
.flame:nth-child(3n){ animation-delay:.12s; }
.flame:nth-child(4n){ animation-delay:.2s; height:30px; }
.cooking .flame{ animation-duration:.22s !important; height:34px; }
@keyframes flameDance{
  from{ transform:scaleY(.85) scaleX(1.06) translateY(1px); }
  to{ transform:scaleY(1.12) scaleX(.92) translateY(-2px); }
}
.stove-glow{
  position:absolute; left:50%; top:184px; transform:translateX(-50%);
  width:320px; height:90px; z-index:1;
  background:radial-gradient(ellipse, rgba(255,138,61,.28), transparent 65%);
  animation:glowPulse 2.4s ease-in-out infinite;
}
.magic .stove-glow{ background:radial-gradient(ellipse, rgba(183,140,255,.3), transparent 65%); }
.cooking .stove-glow{ animation-duration:.8s; }
@keyframes glowPulse{ 50%{ opacity:.6; transform:translateX(-50%) scale(1.06); } }
.base{
  position:absolute; left:50%; top:246px; transform:translateX(-50%);
  width:280px; height:12px; border-radius:8px; z-index:2;
  background:linear-gradient(180deg,#2e2619,#1c1710);
  box-shadow:0 6px 14px rgba(0,0,0,.5);
}
.stove-status{
  text-align:center; font-family:'Fraunces',serif; font-style:italic;
  font-size:15.5px; color:#c4b298; margin:2px 0 18px; min-height:24px;
}

/* pantry chips (streamlit buttons restyled) */
div[data-testid="stHorizontalBlock"] .stButton > button{
  background:var(--cream); color:var(--ink);
  border:none; border-radius:999px;
  font-family:'Outfit',sans-serif; font-size:13px; font-weight:600;
  padding:7px 14px; box-shadow:0 3px 10px rgba(0,0,0,.3);
  transition:transform .15s;
}
div[data-testid="stHorizontalBlock"] .stButton > button:hover{
  transform:translateY(-2px) rotate(-1deg); color:var(--copper-deep);
}

/* primary action buttons */
.stButton > button[kind="primary"]{
  background:linear-gradient(135deg,var(--flame-core),var(--flame) 60%,#e06a1f) !important;
  color:#331a05 !important; border:none !important; border-radius:15px !important;
  font-weight:700 !important; font-size:15px !important; padding:14px 18px !important;
  box-shadow:0 10px 26px -6px rgba(255,138,61,.55) !important;
  transition:transform .15s, box-shadow .25s !important; width:100%;
}
.stButton > button[kind="primary"]:hover{
  transform:translateY(-2px); box-shadow:0 16px 34px -6px rgba(255,138,61,.65) !important;
}
.stButton > button[kind="secondary"]{
  background:rgba(183,140,255,.08) !important; color:#cbb2f5 !important;
  border:1.5px solid rgba(183,140,255,.45) !important; border-radius:15px !important;
  font-weight:700 !important; font-size:15px !important; padding:14px 18px !important;
  transition:transform .15s, box-shadow .25s !important; width:100%;
}
.stButton > button[kind="secondary"]:hover{
  background:rgba(183,140,255,.16) !important; border-color:var(--magic) !important;
  transform:translateY(-2px); box-shadow:0 12px 28px -8px rgba(183,140,255,.4) !important;
}

/* text input */
.stTextInput input{
  background:rgba(0,0,0,.35) !important; color:var(--cream) !important;
  border:1.5px solid var(--panel-edge) !important; border-radius:15px !important;
  font-family:'Outfit',sans-serif !important; font-size:15px !important; padding:13px 18px !important;
}
.stTextInput input:focus{
  border-color:var(--copper) !important;
  box-shadow:0 0 0 4px rgba(217,142,74,.18) !important;
}
.stTextInput input::placeholder{ color:#6e6350 !important; }

.count-note{ text-align:center; font-size:12px; color:#6e6350; margin-top:6px; }

/* login gate */
.login-shell{
  max-width:440px; margin:12vh auto 0; text-align:center;
  animation:fadeUp .7s ease both;
}
.login-flames{
  display:flex; justify-content:center; gap:6px;
  align-items:flex-end; height:30px; margin-bottom:6px;
}
.login-flames .lf{
  width:10px; height:20px;
  border-radius:50% 50% 50% 50% / 62% 62% 38% 38%;
  background:linear-gradient(to top, var(--flame) 15%, var(--flame-core) 70%, #fff3d6);
  transform-origin:bottom center;
  animation:loginFlame .5s ease-in-out infinite alternate;
  filter:blur(.4px);
}
.login-flames .lf:nth-child(2){ height:26px; animation-delay:.1s; }
.login-flames .lf:nth-child(3){ height:16px; animation-delay:.22s; }
.login-flames .lf:nth-child(4){ height:24px; animation-delay:.05s; }
.login-flames .lf:nth-child(5){ height:18px; animation-delay:.15s; }
@keyframes loginFlame{
  from{ transform:scaleY(.82) scaleX(1.08); }
  to{ transform:scaleY(1.14) scaleX(.9) translateY(-2px); }
}
.login-shell .login-mark{
  width:60px; height:60px; margin:0 auto 22px; border-radius:18px;
  background:linear-gradient(135deg,var(--copper-hot),var(--copper-deep));
  display:flex; align-items:center; justify-content:center; color:#2a1c0d;
  box-shadow:0 10px 26px rgba(217,142,74,.45), inset 0 1px 0 rgba(255,255,255,.35);
}
.login-shell h2{
  font-family:'Fraunces',serif; font-weight:600; font-size:32px;
  letter-spacing:-.02em; color:var(--cream); margin:0 0 10px;
}
.login-shell .login-tag{
  font-family:'Fraunces',serif; font-style:italic;
  font-size:15.5px; color:#c4b298; line-height:1.6; margin:0 0 26px; font-weight:400;
}
.login-error{
  text-align:center; font-size:13px; color:#e8a08a;
  background:rgba(193,68,14,.12);
  border:1px solid rgba(193,68,14,.35);
  border-radius:12px; padding:11px 16px; margin-top:12px;
  animation:errShake .4s ease;
}
@keyframes errShake{
  0%,100%{ transform:translateX(0); }
  20%{ transform:translateX(-6px); }
  40%{ transform:translateX(6px); }
  60%{ transform:translateX(-4px); }
  80%{ transform:translateX(4px); }
}

/* user chip in sidebar */
.user-chip{
  display:flex; align-items:center; gap:10px;
  background:rgba(255,255,255,0.04); border:1px solid var(--panel-edge);
  border-radius:12px; padding:10px 12px; margin-bottom:10px;
}
.user-chip img{ width:30px; height:30px; border-radius:50%; }
.user-chip .initial-avatar{
  width:32px; height:32px; border-radius:50%;
  background:linear-gradient(135deg,var(--copper-hot),var(--copper-deep));
  color:#2a1c0d; font-weight:700; font-size:15px;
  display:flex; align-items:center; justify-content:center;
  box-shadow:0 3px 8px rgba(217,142,74,.35);
}
.user-chip .name{ font-size:13.5px; font-weight:600; color:var(--cream); }
.user-chip .email{ font-size:11.5px; color:#a3947c; }

/* diet toggle — radio restyled as segmented pills */
div[role="radiogroup"]{
  display:flex; justify-content:center; gap:8px;
  background:rgba(0,0,0,.3);
  border:1px solid var(--panel-edge);
  border-radius:999px; padding:5px;
  width:fit-content; margin:14px auto 4px;
}
div[role="radiogroup"] label{
  border-radius:999px !important; padding:8px 18px !important;
  transition:background .2s, color .2s; cursor:pointer;
  background:transparent;
}
div[role="radiogroup"] label p{
  color:#a3947c !important; font-family:'Outfit',sans-serif !important;
  font-size:13.5px !important; font-weight:600 !important;
}
div[role="radiogroup"] label:has(input:checked){
  background:linear-gradient(135deg,var(--copper-hot),var(--copper-deep));
  box-shadow:0 4px 12px rgba(217,142,74,.35);
}
div[role="radiogroup"] label:has(input:checked) p{ color:#2a1c0d !important; }
div[role="radiogroup"] label > div:first-child{ display:none; } /* hide radio circle */

/* diet pills on recipe card */
.meta-pill.diet-veg{ background:#e8efdf; border-color:#c6d6b4; color:#48603d; }
.meta-pill.diet-nonveg{ background:#f9e3dc; border-color:#eac2b3; color:#9c3f1e; }
.meta-pill.cuisine{ background:#ede7f6; border-color:#d5c8ec; color:#5b3f8f; }

/* ═══ recipe card ═══ */
.recipe{
  background:var(--cream); color:var(--ink); border-radius:24px;
  overflow:hidden; margin-top:30px;
  box-shadow:0 40px 90px -30px rgba(0,0,0,.75);
  animation:plateUp .8s cubic-bezier(.16,1.1,.3,1) both;
}
@keyframes plateUp{
  0%{ opacity:0; transform:translateY(60px) scale(.95); }
  100%{ opacity:1; transform:translateY(0) scale(1); }
}
.recipe-hero{
  background:
    radial-gradient(130% 180% at 92% -30%, rgba(217,142,74,.28), transparent 55%),
    radial-gradient(110% 150% at -5% 120%, rgba(95,122,82,.16), transparent 50%),
    linear-gradient(160deg,#fffdf7,#f6edd9);
  border-bottom:1px solid rgba(36,29,20,.1);
  padding:36px 40px 30px;
}
.recipe-eyebrow{
  display:inline-flex; align-items:center; gap:9px;
  font-size:11.5px; font-weight:700; letter-spacing:.15em; text-transform:uppercase;
  color:var(--copper-deep); margin-bottom:12px;
}
.recipe-eyebrow::before{ content:""; width:24px; height:2px; background:var(--copper); border-radius:2px; }
.recipe-title{
  font-family:'Fraunces',serif; font-weight:600;
  font-size:clamp(26px,4vw,38px); letter-spacing:-.02em; line-height:1.08;
  margin:0 0 10px; color:var(--ink);
}
.recipe-desc{
  font-family:'Fraunces',serif; font-style:italic; font-size:16.5px;
  color:var(--ink-2); line-height:1.55; max-width:52ch; margin:0;
}
.meta{ display:flex; gap:10px; margin-top:20px; flex-wrap:wrap; }
.meta-pill{
  display:inline-flex; align-items:center; gap:7px;
  background:#fff; border:1px solid rgba(36,29,20,.1); border-radius:999px;
  padding:8px 16px; font-size:13px; font-weight:600; color:var(--ink-2);
  box-shadow:0 2px 8px rgba(36,29,20,.07);
}
.recipe-body{ padding:32px 40px 36px; display:grid; grid-template-columns:1fr 1fr; gap:30px 40px; }
@media (max-width:640px){ .recipe-body{ grid-template-columns:1fr; } .recipe-hero,.recipe-body{ padding-left:24px; padding-right:24px; } }
.col-label{
  display:flex; align-items:center; gap:9px;
  font-size:11.5px; font-weight:700; letter-spacing:.14em; text-transform:uppercase;
  margin-bottom:14px;
}
.col-label .dot{ width:9px; height:9px; border-radius:3px; }
.uses .col-label{ color:#48603d; } .uses .dot{ background:#5f7a52; }
.extras .col-label{ color:var(--copper-deep); } .extras .dot{ background:var(--copper); }
.ing{ display:flex; gap:11px; align-items:flex-start; font-size:14.5px; line-height:1.5; padding:8px 0; border-bottom:1px solid rgba(36,29,20,.06); }
.ing:last-child{ border-bottom:none; }
.ing-icon{
  flex:none; width:23px; height:23px; border-radius:8px;
  display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700;
}
.uses .ing-icon{ background:#e8efdf; color:#48603d; }
.extras .ing-icon{ background:#f9e8d3; color:var(--copper-deep); }
.none-needed{ font-size:14.5px; color:var(--ink-3); font-style:italic; padding:8px 0; }
.steps-wrap{ grid-column:1 / -1; border-top:1px solid rgba(36,29,20,.1); padding-top:26px; }
.steps-wrap .col-label{ color:var(--ink); } .steps-wrap .dot{ background:var(--ink); }
.step{
  display:flex; gap:16px; padding:13px 16px; border-radius:15px;
  font-size:14.5px; line-height:1.6; color:var(--ink-2);
  transition:background .2s, transform .2s;
}
.step:hover{ background:#f4ecdb; transform:translateX(4px); }
.step-num{
  flex:none; font-family:'Fraunces',serif; font-weight:600; font-size:16px;
  color:var(--copper-deep); width:32px; margin-top:1px;
}
.recipe-footer{
  border-top:1px solid rgba(36,29,20,.1); padding:18px 40px;
  font-size:12.5px; color:var(--ink-3); background:#f6efdf;
}
</style>
""",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────
# Name-based login gate (no Google / OAuth involved)
# ──────────────────────────────────────────────────────────────
# Only these first names may enter. Matching is case-insensitive.
ALLOWED_NAMES = {"biplav", "abhishek", "sonali", "anwesh", "sourav", "kirtiman","manisha"}


def _check_name(raw: str) -> str | None:
    """Return the canonical (title-cased) name if allowed, else None."""
    cleaned = (raw or "").strip().lower()
    if not cleaned:
        return None
    # accept "kirtiman" as well as "Kirtiman Sarangi"
    if cleaned in ALLOWED_NAMES:
        return cleaned.title()
    first_word = cleaned.split()[0]
    if first_word in ALLOWED_NAMES:
        return first_word.title()
    return None


def _attempt_login():
    name = _check_name(st.session_state.get("login_name", ""))
    if name:
        st.session_state.auth_name = name
        st.session_state.login_error = False
    else:
        st.session_state.login_error = True


if "auth_name" not in st.session_state:
    st.session_state.auth_name = None
if "login_error" not in st.session_state:
    st.session_state.login_error = False

if st.session_state.auth_name is None:
    st.markdown(
        """
        <div class="login-shell">
          <div class="login-flames" aria-hidden="true">
            <span class="lf"></span><span class="lf"></span><span class="lf"></span>
            <span class="lf"></span><span class="lf"></span>
          </div>
          <div class="login-mark">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 11h18"/><path d="M5 11a7 7 0 0 1 14 0"/><path d="M12 4v1"/><path d="M8 15l-2 5"/><path d="M16 15l2 5"/>
            </svg>
          </div>
          <h2>Pantry to Plate</h2>
          <p class="login-tag">A private kitchen &mdash; tell us who's cooking tonight.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_a, col_b, col_c = st.columns([1, 1.6, 1])
    with col_b:
        st.text_input(
            "Your name",
            key="login_name",
            placeholder="Type your name and press Enter…",
            label_visibility="collapsed",
            on_change=_attempt_login,
        )
        if st.button("🔥 Enter the kitchen", type="primary", use_container_width=True):
            _attempt_login()
            if st.session_state.auth_name:
                st.rerun()

        if st.session_state.login_error:
            st.markdown(
                '<p class="login-error">Hmm, that name isn\u2019t on tonight\u2019s guest list. '
                "Check the spelling, or ask the host for an invite.</p>",
                unsafe_allow_html=True,
            )
    st.stop()

# ──────────────────────────────────────────────────────────────
# State
# ──────────────────────────────────────────────────────────────
if "ingredients" not in st.session_state:
    st.session_state.ingredients = []
if "recipe" not in st.session_state:
    st.session_state.recipe = None
if "recipe_mode" not in st.session_state:
    st.session_state.recipe_mode = False  # False = classic, True = surprise
if "error" not in st.session_state:
    st.session_state.error = None
if "recipe_diet" not in st.session_state:
    st.session_state.recipe_diet = "Anything"
if "recipe_cuisine" not in st.session_state:
    st.session_state.recipe_cuisine = ""

DIET_OPTIONS = ["Anything", "🌿 Veg", "🍗 Non-veg"]

QUICK = ["eggs", "garlic", "onion", "rice", "pasta", "canned tomatoes",
         "olive oil", "chicken", "potatoes", "cheese", "spinach", "lemon"]

COOK_LINES = ["Sizzling ideas…", "Tasting for balance…", "Adjusting the seasoning…", "Letting flavours mingle…"]
MAGIC_LINES = ["Consulting the spice cabinet of the unknown…", "Bending a few culinary rules…", "Adding a pinch of the unexpected…"]


def get_api_key() -> str | None:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        try:
            key = st.secrets["ANTHROPIC_API_KEY"]
        except Exception:
            key = None
    if not key:
        key = st.session_state.get("manual_api_key") or None
    return key


def add_ingredients_from_input():
    raw = st.session_state.get("ing_input", "")
    for part in raw.split(","):
        cleaned = part.strip().lower()
        if cleaned and cleaned not in st.session_state.ingredients:
            st.session_state.ingredients.append(cleaned)
    st.session_state.ing_input = ""


def stove_html(state: str = "idle", magic: bool = False) -> str:
    """Render the copper pot. state: idle | cooking | revealing"""
    cls = f"stove {state if state != 'idle' else ''} {'magic' if magic else ''}".strip()
    flames = "".join('<span class="flame"></span>' for _ in range(11))
    import random
    bubbles = "".join(
        f'<span class="bubble" style="width:{5 + random.random()*8:.0f}px;height:{5 + random.random()*8:.0f}px;'
        f'left:{5 + random.random()*88:.0f}%;animation-delay:{random.random()*1.1:.2f}s"></span>'
        for _ in range(9)
    )
    return f"""
    <div class="{cls}">
      <div class="pot-scene">
        <span class="wisp w1"></span><span class="wisp w2"></span><span class="wisp w3"></span>
        <div class="lid"><span class="knob"></span><span class="dome"></span></div>
        <div class="bubbles">{bubbles}</div>
        <div class="pot">
          <div class="pot-rim"></div><div class="pot-body"></div><div class="pot-shine"></div>
          <div class="handle left"></div><div class="handle right"></div>
        </div>
        <div class="burner">{flames}</div>
        <div class="stove-glow"></div>
        <div class="base"></div>
      </div>
    </div>
    """


def render_recipe_card(recipe: dict, surprise: bool, n_ingredients: int, diet: str = "Anything", cuisine: str = ""):
    import html as html_mod

    def e(s):
        return html_mod.escape(str(s))

    uses = "".join(
        f'<div class="ing"><span class="ing-icon">✓</span><span>{e(i)}</span></div>'
        for i in recipe.get("uses", [])
    )
    extras_list = recipe.get("extras", [])
    if extras_list:
        extras = "".join(
            f'<div class="ing"><span class="ing-icon">+</span><span>{e(i)}</span></div>'
            for i in extras_list
        )
    else:
        extras = '<p class="none-needed">Nothing — your pantry covers it all.</p>'
    steps = "".join(
        f'<div class="step"><span class="step-num">{i+1:02d}</span><span>{e(s)}</span></div>'
        for i, s in enumerate(recipe.get("steps", []))
    )
    meta = ""
    if recipe.get("time_minutes"):
        meta += f'<span class="meta-pill">⏱ ~{e(recipe["time_minutes"])} min</span>'
    if recipe.get("serves"):
        meta += f'<span class="meta-pill">👤 Serves {e(recipe["serves"])}</span>'
    meta += f'<span class="meta-pill">✦ {"Adventurous" if surprise else "Weeknight-easy"}</span>'
    if "Veg" in diet and "Non" not in diet:
        meta += '<span class="meta-pill diet-veg">🌿 Vegetarian</span>'
    elif "Non-veg" in diet:
        meta += '<span class="meta-pill diet-nonveg">🍗 Non-veg</span>'
    if cuisine:
        meta += f'<span class="meta-pill cuisine">🌍 {e(cuisine)}</span>'

    st.markdown(
        f"""
        <div class="recipe">
          <div class="recipe-hero">
            <span class="recipe-eyebrow">{'A creative detour' if surprise else 'Fresh off the stove'}</span>
            <h3 class="recipe-title">{e(recipe.get('dish_name', 'Untitled dish'))}</h3>
            <p class="recipe-desc">{e(recipe.get('description', ''))}</p>
            <div class="meta">{meta}</div>
          </div>
          <div class="recipe-body">
            <div class="uses">
              <p class="col-label"><span class="dot"></span> From your pantry</p>
              {uses}
            </div>
            <div class="extras">
              <p class="col-label"><span class="dot"></span> You'll also need</p>
              {extras}
            </div>
            <div class="steps-wrap">
              <p class="col-label"><span class="dot"></span> Method</p>
              {steps}
            </div>
          </div>
          <div class="recipe-footer">Composed by Claude from your {n_ingredients} ingredient{'s' if n_ingredients != 1 else ''}.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def diet_instruction(diet: str) -> str:
    if "Veg" in diet and "Non" not in diet:
        return (
            " The dish MUST be strictly vegetarian: no meat, poultry, fish, seafood or eggs. "
            "If my ingredient list contains any non-vegetarian items, ignore them and do not "
            "include them in the 'uses' list."
        )
    if "Non-veg" in diet:
        return (
            " The dish should be non-vegetarian, featuring meat, poultry, fish or seafood as a "
            "central component. If my list has no non-veg ingredient, choose one common, "
            "affordable option and put it in 'extras'."
        )
    return ""


def cuisine_instruction(cuisine: str) -> str:
    cuisine = (cuisine or "").strip()[:60]
    if cuisine:
        return (
            f" The dish should be in the style of {cuisine} cuisine, "
            "using flavours and techniques typical of it."
        )
    return ""


def cook(surprise: bool, diet: str, cuisine: str):
    api_key = get_api_key()
    if not api_key:
        st.session_state.error = "no_key"
        return

    ingredients = st.session_state.ingredients
    base = f"I have these ingredients at home: {', '.join(ingredients)}."
    style = (
        "Suggest one creative, slightly unexpected or fusion dish I could make that mostly uses "
        "these ingredients (a few sensible extras are fine). Be adventurous but keep it realistically "
        "cookable in a home kitchen. Avoid suggesting the most obvious dish for these ingredients."
        if surprise
        else "Suggest one simple, delicious, practical dish I could make using mostly these "
        "ingredients, needing as few extra items as possible."
    )
    system = (
        "You are an expert home cooking assistant. Respond with ONLY a single valid JSON object and "
        "nothing else — no markdown, no code fences, no commentary.\n"
        "The JSON object must have exactly these fields:\n"
        '{ "dish_name": string, "description": string (one short, appetising sentence), '
        '"time_minutes": number, "serves": number, '
        '"uses": array of strings (ingredients from the list this dish actually uses), '
        '"extras": array of strings (items needed that were NOT in the list; empty array if none; '
        "assume salt, pepper and water are always available and never list them), "
        '"steps": array of strings (5 to 8 clear, imperative, one-sentence steps) }\n'
        "Keep everything concise. No text outside the JSON object."
    )

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1000,
            system=system,
            messages=[{"role": "user", "content": f"{base} {style}{diet_instruction(diet)}{cuisine_instruction(cuisine)}"}],
        )
        text = "".join(b.text for b in response.content if b.type == "text").strip()
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        st.session_state.recipe = json.loads(text)
        st.session_state.recipe_mode = surprise
        st.session_state.recipe_diet = diet
        st.session_state.recipe_cuisine = (cuisine or "").strip()[:60]
        st.session_state.error = None
    except Exception as exc:  # noqa: BLE001
        st.session_state.recipe = None
        st.session_state.error = str(exc)


# ──────────────────────────────────────────────────────────────
# Sidebar — account + API key fallback
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Settings")

    if st.session_state.auth_name:
        initial = st.session_state.auth_name[0].upper()
        st.markdown(
            f"""
            <div class="user-chip">
              <div class="initial-avatar">{initial}</div>
              <div>
                <div class="name">{st.session_state.auth_name}</div>
                <div class="email">In the kitchen tonight</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Leave the kitchen", use_container_width=True):
            st.session_state.auth_name = None
            st.session_state.login_error = False
            st.rerun()
        st.divider()

    if not (os.environ.get("ANTHROPIC_API_KEY") or "ANTHROPIC_API_KEY" in st.secrets):
        st.text_input(
            "Anthropic API key",
            type="password",
            key="manual_api_key",
            help="Set ANTHROPIC_API_KEY in Streamlit secrets to skip this.",
        )
    else:
        st.success("API key configured ✓")

# ──────────────────────────────────────────────────────────────
# Layout
# ──────────────────────────────────────────────────────────────
st.markdown('<div class="hero-badge"><span class="flame-dot"></span>&nbsp;Powered by Claude</div>', unsafe_allow_html=True)
st.markdown(
    '<h1 class="hero-title">Toss it in.<br>We\u2019ll make it <span class="glow">delicious.</span></h1>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<p class="hero-sub">Welcome back, <strong>{st.session_state.auth_name}</strong>. '
    "Toss in whatever\u2019s at home — our stove does the thinking: "
    "<strong>one great dish</strong>, the shortest shopping list, and every step to get there.</p>",
    unsafe_allow_html=True,
)

# The pot (idle) + status — placeholders so we can animate during cooking
pot_slot = st.empty()
status_slot = st.empty()
pot_slot.markdown(stove_html("idle"), unsafe_allow_html=True)
n = len(st.session_state.ingredients)
idle_status = (
    "The pot is waiting." if n == 0
    else "A promising start…" if n < 3
    else "That\u2019s enough to cook with."
)
status_slot.markdown(f'<p class="stove-status">{idle_status}</p>', unsafe_allow_html=True)

# Ingredient input
st.text_input(
    "Add ingredients",
    key="ing_input",
    placeholder="What's in your kitchen? e.g. chicken thighs, lemon, rice — press Enter",
    label_visibility="collapsed",
    on_change=add_ingredients_from_input,
)

# Chips — click to remove
if st.session_state.ingredients:
    cols = st.columns(4)
    for i, item in enumerate(list(st.session_state.ingredients)):
        with cols[i % 4]:
            if st.button(f"{item}  ✕", key=f"chip_{item}"):
                st.session_state.ingredients.remove(item)
                st.rerun()

# Quick adds
remaining_quick = [q for q in QUICK if q not in st.session_state.ingredients]
if remaining_quick:
    with st.expander("Quick add staples"):
        qcols = st.columns(4)
        for i, item in enumerate(remaining_quick):
            with qcols[i % 4]:
                if st.button(f"+ {item}", key=f"quick_{item}"):
                    st.session_state.ingredients.append(item)
                    st.rerun()

st.markdown(
    f'<p class="count-note">{n} ingredient{"s" if n != 1 else ""} ready for the pot</p>'
    if n else '<p class="count-note">Add at least one ingredient to light the stove</p>',
    unsafe_allow_html=True,
)

# Diet toggle
diet = st.radio(
    "Diet preference",
    DIET_OPTIONS,
    horizontal=True,
    key="diet_choice",
    label_visibility="collapsed",
)

# Cuisine style (optional)
cuisine = st.text_input(
    "Cuisine style",
    key="cuisine_input",
    placeholder="🌍 Cuisine style (optional) — e.g. Odia, South Indian, Italian, Thai…",
    label_visibility="collapsed",
)

# Action buttons
c1, c2 = st.columns(2)
cook_clicked = c1.button("🔥 Cook something up", type="primary", disabled=(n == 0), use_container_width=True)
magic_clicked = c2.button("✦ Surprise me", type="secondary", disabled=(n == 0), use_container_width=True)

if cook_clicked or magic_clicked:
    surprise = magic_clicked
    # animate: cooking pot + rotating status lines while the API call runs
    pot_slot.markdown(stove_html("cooking", magic=surprise), unsafe_allow_html=True)
    lines = MAGIC_LINES if surprise else COOK_LINES
    status_slot.markdown(f'<p class="stove-status">{lines[0]}</p>', unsafe_allow_html=True)

    with st.spinner(""):
        cook(surprise, diet, cuisine)

    if st.session_state.recipe:
        # reveal: lid lifts, brief pause, then card renders below
        pot_slot.markdown(stove_html("revealing", magic=surprise), unsafe_allow_html=True)
        status_slot.markdown(
            f'<p class="stove-status">{"Behold… something unexpected." if surprise else "Dinner is served."}</p>',
            unsafe_allow_html=True,
        )
        time.sleep(0.6)
        pot_slot.markdown(stove_html("idle"), unsafe_allow_html=True)

# Result / errors
if st.session_state.error == "no_key":
    st.warning("Add your Anthropic API key in the sidebar (or Streamlit secrets) to start cooking.")
elif st.session_state.error:
    st.error(f"The pot boiled over — {st.session_state.error}")
    if st.button("Try again"):
        st.session_state.error = None
        st.rerun()
elif st.session_state.recipe:
    render_recipe_card(
        st.session_state.recipe,
        st.session_state.recipe_mode,
        n,
        st.session_state.recipe_diet,
        st.session_state.recipe_cuisine,
    )
