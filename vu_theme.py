"""VU Academic Advisor visual theme. Presentation only; no chatbot/backend logic."""
import base64
import mimetypes
import pathlib
import streamlit as st

ROOT = pathlib.Path(__file__).parent
CAMPUS = ROOT / "campus.jpg"
LOGO = ROOT / "Logo.png"
SYMBOL = ROOT / "images.jpg"
ASSISTANT_AVATAR = str(SYMBOL)

@st.cache_data(show_spinner=False)
def _b64(path_string: str) -> str:
    path = pathlib.Path(path_string)
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return "data:" + mime + ";base64," + base64.b64encode(path.read_bytes()).decode("ascii")

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Google+Sans+Flex:opsz,wght@6..144,400;500;600;700&display=swap');
:root { --vu-blue:#21499b; --vu-red:#c71932; --vu-ink:#202b40; --vu-pale:#e3e9f8; }
html, body, [class*="css"], button, input, textarea, select {
  font-family:'Google Sans Flex','Google Sans','Product Sans',Arial,sans-serif!important;
}
.stApp {
  background:linear-gradient(rgba(244,248,255,.72),rgba(248,247,247,.72)),
    url(__CAMPUS__) center center / cover no-repeat fixed!important;
  color:var(--vu-ink)!important;
}
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stMainBlockContainer"],
[data-testid="stHeader"],[data-testid="stBottom"],[data-testid="stBottom"]>div { background:transparent!important; }
#MainMenu, footer { visibility:hidden; }
[data-testid="stMainBlockContainer"] { max-width:1160px!important; padding:1rem 2rem 1.4rem!important; }
[data-testid="stSidebar"],[data-testid="stSidebar"]>div:first-child {
 background:rgba(232,242,255,.88)!important; backdrop-filter:blur(18px)!important;
 border-right:1px solid #ffffffaa!important;
}
[data-testid="stSidebar"] * { color:var(--vu-ink)!important; }
[data-testid="stSidebar"] label { font-weight:600!important;color:#35435d!important; }
[data-testid="stSidebar"] hr { border-color:#21499b20!important; }
[data-testid="stSidebar"] [data-baseweb="select"]>div,
[data-testid="stSidebar"] [data-baseweb="input"]>div {
 background:#ffffffd9!important;border:1px solid #dfe7f2!important;border-radius:12px!important;
}
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="input"] input { color:var(--vu-ink)!important; }
[data-testid="stSidebar"] [data-testid="stExpander"] {
 background:#ffffff80!important;border:1px solid #ffffffb8!important;border-radius:16px!important;
}
[data-testid="stSidebar"] [data-testid="stButton"]>button {
 background:var(--vu-red)!important;color:#fff!important;border:0!important;border-radius:30px!important;font-weight:600!important;
}
.vu-logo { width:100%;height:auto;display:block;background:rgba(255,255,255,.92);border-radius:14px;padding:10px 14px;margin:2px 0 8px; }
.vu-pill { width:max-content;max-width:95%;margin:5px auto 22px;padding:10px 27px;border-radius:50px;
 display:flex;align-items:center;gap:14px;background:#fffffff0;border:1px solid #ffffffdf;
 box-shadow:0 8px 25px #1b30511f;color:var(--vu-blue);font-weight:700;letter-spacing:.08em;font-size:16px; }
.vu-av { width:42px;height:42px;flex:none;border-radius:50%;padding:3px;background:#fff;display:flex;align-items:center;justify-content:center; }
.vu-av img { width:34px;height:34px;object-fit:contain;border-radius:50%; }
.vu-title { color:var(--vu-blue)!important; }
.info-box { background:#ffffffe0!important;border:1px solid #ffffffd9!important;border-left:4px solid var(--vu-red)!important;
 border-radius:20px!important;padding:22px 25px!important;margin:12px 0 20px!important;box-shadow:0 8px 25px #1b305117!important;backdrop-filter:blur(13px)!important; }
.info-box h3 { color:var(--vu-blue)!important;font-size:23px;margin:0 0 8px; }
.info-box p { color:#53627a!important;line-height:1.6;margin:0; }
.bubble-user { display:flex;justify-content:flex-end;margin:16px 0; }
.bubble-user-inner { max-width:78%;background:var(--vu-blue)!important;color:white!important;padding:12px 18px;border-radius:22px 22px 6px 22px;line-height:1.55;box-shadow:0 5px 14px #21499b2b; }
.bubble-user-inner * { color:white!important; }
.bubble-bot { display:flex;align-items:flex-end;gap:10px;justify-content:flex-start;margin:16px 0; }
.bubble-bot-inner { max-width:84%;background:#ffffffe8!important;color:var(--vu-ink)!important;border:1px solid #ffffffdc!important;padding:15px 19px;border-radius:20px 20px 20px 6px;line-height:1.65;box-shadow:0 5px 17px #1b305114;backdrop-filter:blur(12px); }
.vu-bot-avatar { width:34px;height:34px;flex:0 0 34px;border-radius:50%;object-fit:contain;background:white;border:2px solid white;box-shadow:0 2px 8px #1b30511f;padding:3px; }
.st-key-whatsapp_composer { position:sticky;bottom:8px;z-index:30;background:#fffffff0!important;border:1px solid #ffffffeb!important;border-radius:38px!important;padding:9px 11px!important;margin:20px auto 6px!important;max-width:940px!important;box-shadow:0 10px 30px #1b305126!important;backdrop-filter:blur(16px)!important; }
.st-key-whatsapp_composer [data-testid="stTextInput"] input { min-height:48px!important;border-radius:30px!important;border:1px solid #e3e8f1!important;background:#fffffff5!important;color:var(--vu-ink)!important;padding:0 17px!important;box-shadow:none!important; }
.st-key-whatsapp_composer [data-testid="stTextInput"] input::placeholder { color:#8a91a0!important; }
.st-key-whatsapp_composer [data-testid="stPopover"]>button,.st-key-whatsapp_composer [data-testid="stAudioInput"] button { min-height:44px!important;width:44px!important;border-radius:50%!important;background:white!important;color:var(--vu-red)!important;border:1px solid #f2dce1!important; }
.st-key-whatsapp_composer [data-testid="stButton"]>button[kind="primary"] { min-height:46px!important;width:46px!important;border-radius:50%!important;padding:0!important;background:var(--vu-red)!important;border:0!important;color:white!important;font-size:22px!important;box-shadow:0 4px 12px #c719322b!important; }
.composer-disclaimer { max-width:940px;margin:7px auto 15px;text-align:center;color:#59657a!important;font-size:11px;background:#ffffffad;border-radius:14px;padding:7px; }
[data-testid="stMainBlockContainer"] button[kind="secondary"] { background:#ffe9ec!important;color:var(--vu-red)!important;border:1px solid #f6d2da!important;font-weight:600!important;border-radius:28px!important; }
@media(max-width:760px) { [data-testid="stMainBlockContainer"] { padding:1rem .65rem!important; }
 .bubble-user-inner,.bubble-bot-inner { max-width:94%; } .st-key-whatsapp_composer { border-radius:23px!important;padding:7px!important; }
 .vu-pill { font-size:13px;padding:9px 17px; } }
"""

def apply_theme() -> None:
    css = _CSS.replace("__CAMPUS__", _b64(str(CAMPUS)) if CAMPUS.exists() else "")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def sidebar_logo() -> None:
    if LOGO.exists():
        st.sidebar.markdown(f'<img class="vu-logo" src="{_b64(str(LOGO))}" alt="Vidyashilp University">', unsafe_allow_html=True)

def header_html(active: bool = False, turn: int = 0) -> str:
    symbol = _b64(str(SYMBOL)) if SYMBOL.exists() else (_b64(str(LOGO)) if LOGO.exists() else "")
    return ('<div class="vu-pill"><span class="vu-av"><img src="' + symbol +
            '" alt="VU Advisor"></span><span class="vu-title">VU ACADEMIC ADVISOR</span></div>')
