"""VU Academic Advisor visual theme. Presentation only; no chatbot/backend logic."""
import base64
import mimetypes
import pathlib

import streamlit as st

ROOT = pathlib.Path(__file__).parent
CAMPUS = ROOT / "campus.jpg"
LOGO = ROOT / "Logo.png"
SYMBOL = ROOT / "images.jpg"          # the red/blue swoosh
ASSISTANT_AVATAR = str(SYMBOL)


@st.cache_data(show_spinner=False)
def _b64(path_string: str) -> str:
    path = pathlib.Path(path_string)
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return "data:" + mime + ";base64," + base64.b64encode(path.read_bytes()).decode("ascii")


_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
:root { --vu-blue:#1F3F9E; --vu-red:#C8202F; --vu-pale:#E3E9F8; --vu-tint:#FBE3E5; --vu-ink:#1F1F2E; }

/* ---------- base + ONE campus photo, 75% visible ---------- */
.stApp, .stApp p, .stApp label, .stApp button, .stApp input, .stApp textarea, .stApp li, .stApp h3 {
  font-family: 'Poppins', Arial, sans-serif;
}
.stApp {
  background: linear-gradient(rgba(255,255,255,.25), rgba(255,255,255,.25)),
              url(__CAMPUS__) center center / cover no-repeat fixed !important;
  color: var(--vu-ink);
}
[data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"],
[data-testid="stBottom"], [data-testid="stBottom"] > div { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }
[data-testid="stMainBlockContainer"] { max-width: 1100px !important; padding: .6rem 2rem 1.4rem !important; }

/* ---------- sidebar: light frosted glass, collapsible with the native chevron ---------- */
[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
  background: rgba(255,255,255,.4) !important;
  backdrop-filter: blur(2px) !important; -webkit-backdrop-filter: blur(2px) !important;
  border-right: 0 !important;
}
[data-testid="stSidebar"][aria-expanded="true"] { min-width: 360px !important; max-width: 360px !important; }
[data-testid="stSidebar"] h3 { color: var(--vu-blue); font-size: 15px; font-weight: 600; margin: .4rem 0 .2rem; }
[data-testid="stSidebar"] label p { color: var(--vu-blue) !important; font-weight: 600; }
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-baseweb="base-input"],
[data-testid="stSidebar"] [data-baseweb="input"] > div {
  background: var(--vu-pale) !important; border: 0 !important; border-radius: 16px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] input { color: var(--vu-blue) !important; font-weight: 600; }
[data-testid="stSidebar"] input::placeholder { color: #7184BD !important; font-weight: 500; }
[data-testid="stSidebar"] [data-testid="stButton"] > button {
  background: var(--vu-red) !important; color: #fff !important; border: 0 !important;
  border-radius: 999px !important; font-weight: 600 !important; padding: .6rem 1rem !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover { background: #A91A27 !important; }
.vu-logo { width: 100%; height: auto; display: block; background: rgba(255,255,255,.85);
           border-radius: 14px; padding: 10px 14px; margin: 2px 0 10px; }

/* ---------- header pill: fixed at the top, fully round ---------- */
[data-testid="stElementContainer"]:has(.vu-pill), .element-container:has(.vu-pill) {
  position: sticky; top: .6rem; z-index: 100; }
.vu-pill { display: flex; align-items: center; gap: 14px; width: max-content; max-width: 95%;
           margin: 6px auto 18px; padding: 8px 30px 8px 10px; background: rgba(255,255,255,.95);
           border-radius: 999px; box-shadow: 0 2px 10px rgba(31,63,158,.18); }
.vu-av { position: relative; width: 58px; height: 58px; flex: none; }
.vu-ring { position: absolute; inset: 0; border-radius: 50%; opacity: 0;
           background: linear-gradient(135deg, #4BE87F, #12A150); }          /* green story ring */
.vu-av.on .vu-ring { opacity: 1; }                                           /* advisor is typing */
.vu-av.fade-a .vu-ring { animation: vuFadeA 5.5s forwards; }                 /* gone 5s after the reply */
.vu-av.fade-b .vu-ring { animation: vuFadeB 5.5s forwards; }
@keyframes vuFadeA { 0%, 91% { opacity: 1 } 100% { opacity: 0 } }
@keyframes vuFadeB { 0%, 91% { opacity: 1 } 100% { opacity: 0 } }
.vu-in { position: absolute; inset: 4px; border-radius: 50%; background: #fff;
         display: flex; align-items: center; justify-content: center; }
.vu-in img { width: 34px; height: 34px; object-fit: contain; }
.vu-title { color: var(--vu-blue); font-weight: 700; font-size: 16px; letter-spacing: .1em; }

/* ---------- chat bubbles ---------- */
.bubble-user { display: flex; justify-content: flex-end; margin: 14px 0; }
.bubble-user-inner { max-width: 70%; background: var(--vu-blue) !important; color: #fff !important;
                     padding: 13px 20px; border-radius: 24px 24px 6px 24px; line-height: 1.55; font-weight: 500; }
.bubble-user-inner * { color: #fff !important; }
.bubble-bot { display: flex; align-items: flex-end; gap: 10px; justify-content: flex-start; margin: 14px 0; }
.bubble-bot-inner { max-width: 78%; background: #fff !important; color: var(--vu-ink) !important;
                    padding: 15px 20px; border-radius: 24px 24px 24px 6px; line-height: 1.6;
                    box-shadow: 0 2px 14px rgba(31,63,158,.14); }
.vu-bot-av { position: relative; flex: 0 0 36px; width: 36px; height: 36px; }
.vu-bot-avatar { width: 36px; height: 36px; border-radius: 50%; object-fit: contain; background: #fff;
                 box-shadow: 0 0 0 2px var(--vu-pale); padding: 5px; display: block; }
.vu-bot-av.live::after { content: ""; position: absolute; right: -1px; bottom: -1px; width: 11px; height: 11px;
                         border-radius: 50%; background: #2ECC71; border: 2px solid #fff;
                         animation: vuDot 5.5s forwards; }                    /* green dot, gone after 5s */
@keyframes vuDot { 0%, 91% { opacity: 1 } 100% { opacity: 0 } }

/* ---------- suggestion chips: VU red ---------- */
[data-testid="stMainBlockContainer"] button[kind="secondary"] {
  background: var(--vu-tint) !important; color: var(--vu-red) !important; border: 0 !important;
  font-weight: 600 !important; border-radius: 999px !important; padding: .5rem 1rem !important; }
[data-testid="stMainBlockContainer"] button[kind="secondary"]:hover { background: #F5CDD1 !important; }

/* ---------- bottom bar: one pill with the attach / mic / send icons in VU red ---------- */
.st-key-whatsapp_composer { position: sticky; bottom: 8px; z-index: 30; background: #fff !important;
  border: 0 !important; border-radius: 999px !important; padding: 8px 10px 8px 14px !important;
  margin: 20px auto 6px !important; max-width: 940px !important; box-shadow: 0 4px 22px rgba(31,63,158,.2) !important; }
.st-key-whatsapp_composer [data-testid="stTextInput"] input {
  min-height: 46px !important; border: 0 !important; background: transparent !important;
  color: var(--vu-ink) !important; box-shadow: none !important; padding: 0 12px !important; }
.st-key-whatsapp_composer [data-testid="stTextInput"] input::placeholder { color: #8E8E9A !important; }
.st-key-whatsapp_composer [data-testid="stTextInput"] > div,
.st-key-whatsapp_composer [data-baseweb="input"],
.st-key-whatsapp_composer [data-baseweb="base-input"] { background: transparent !important; border: 0 !important; }
.st-key-whatsapp_composer [data-testid="stPopover"] > button,
.st-key-whatsapp_composer [data-testid="stAudioInput"] button {
  min-height: 44px !important; width: 44px !important; border-radius: 50% !important;
  background: #fff !important; color: var(--vu-red) !important; border: 0 !important; }
.st-key-whatsapp_composer [data-testid="stPopover"] > button *,
.st-key-whatsapp_composer [data-testid="stAudioInput"] button * { color: var(--vu-red) !important; fill: var(--vu-red) !important; }
.st-key-whatsapp_composer [data-testid="stButton"] > button[kind="primary"] {
  min-height: 44px !important; width: 44px !important; border-radius: 50% !important; padding: 0 !important;
  background: var(--vu-red) !important; border: 0 !important; color: #fff !important; font-size: 22px !important; }
.composer-disclaimer { max-width: 940px; margin: 8px auto 14px; text-align: center; color: #3B3B4B !important;
                       font-size: 12px; background: rgba(255,255,255,.82); border-radius: 14px; padding: 7px 12px; }

@media (max-width: 760px) {
  [data-testid="stMainBlockContainer"] { padding: .6rem .65rem !important; }
  .bubble-user-inner, .bubble-bot-inner { max-width: 92%; }
  .st-key-whatsapp_composer { border-radius: 28px !important; padding: 7px !important; }
  .vu-title { font-size: 13px; letter-spacing: .06em; } .vu-pill { padding: 8px 18px 8px 8px; }
}
"""


def apply_theme() -> None:
    css = _CSS.replace("__CAMPUS__", _b64(str(CAMPUS)) if CAMPUS.exists() else "none")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def sidebar_logo() -> None:
    if LOGO.exists():
        st.sidebar.markdown(
            f'<img class="vu-logo" src="{_b64(str(LOGO))}" alt="Vidyashilp University">',
            unsafe_allow_html=True,
        )


def header_html(active: bool = False, turn: int = 0) -> str:
    """Fixed top pill.
    active=True           -> green ring on (advisor is typing)
    active=False, turn=0  -> ring hidden (idle / empty chat)
    active=False, turn>0  -> ring shows, then disappears after 5 seconds (pass a new turn per reply)
    """
    if active:
        state = "on"
    elif turn:
        state = "fade-a" if turn % 2 else "fade-b"
    else:
        state = ""
    symbol = _b64(str(SYMBOL)) if SYMBOL.exists() else (_b64(str(LOGO)) if LOGO.exists() else "")
    return (
        '<div class="vu-pill">'
        f'<div class="vu-av {state}"><div class="vu-ring"></div>'
        f'<div class="vu-in"><img src="{symbol}" alt="VU Academic Advisor"></div></div>'
        '<span class="vu-title">VU ACADEMIC ADVISOR</span></div>'
    )
