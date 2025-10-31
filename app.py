import streamlit as st
import requests
import os
from dotenv import load_dotenv
from tavus_utils import create_conversation, end_conversation
from leads_store import save_lead, forward_to_webhook, parse_lead_from_transcript_text
from tavus_utils import get_conversation, extract_transcript_text

# --- Load environment variables ---
load_dotenv()
TAVUS_API_KEY = os.getenv("API_KEY")
BROADGATE_PERSONA_ID = os.getenv("BROADGATE_PERSONA_ID")

# --- Page setup ---
st.set_page_config(page_title="Broadgate Voice Assistant", layout="wide")

# --- Title ---
st.title("🎙️ Talk to a Broadgate Voice Assistant")
st.write("Click the button below to start a conversation with our AI-powered assistant who can answer your questions in natural voice.")

# --- Display GIF ---
GIF_PATH = os.path.join(os.path.dirname(__file__), "ezgif-72d92bc4c273d5.gif")
if os.path.exists(GIF_PATH):
    st.image(GIF_PATH, use_container_width=True)
else:
    # fallback image or hosted gif
    st.image("https://raw.githubusercontent.com/Yohanes213/tavus-demo/main/ezgif-72d92bc4c273d5.gif", use_container_width=True)

# --- Query params handling (updated API) ---
params = st.query_params

# --- Main UI logic ---
if "call_url" not in st.session_state:
    st.session_state["call_url"] = ""
if "conversation_id" not in st.session_state:
    st.session_state["conversation_id"] = ""
if "opened_call_tab" not in st.session_state:
    st.session_state["opened_call_tab"] = False

if st.button("📞 Start Call"):
    if not BROADGATE_PERSONA_ID:
        st.error("Missing BROADGATE_PERSONA_ID in environment. Please set it in your .env file.")
    else:
        try:
            resp = create_conversation(BROADGATE_PERSONA_ID)
            call_url = (
                (resp or {}).get("call_url")
                or (resp or {}).get("webrtc_url")
                or (resp or {}).get("join_url")
                or (resp or {}).get("conversation_url")
                or ""
            )
            if call_url:
                st.session_state["call_url"] = call_url
                st.session_state["conversation_id"] = (resp or {}).get("conversation_id", "")
                st.session_state["opened_call_tab"] = False
            else:
                st.warning("Conversation created but no call URL was returned.")
                st.json(resp)
        except Exception as e:
            st.error(f"Failed to start call: {e}")

# if st.button("📞 Start Call"):
#     if not BROADGATE_PERSONA_ID:
#         st.error("Missing BROADGATE_PERSONA_ID in environment. Please set it in your .env file.")
#     else:
#         try:
#             resp = create_conversation(BROADGATE_PERSONA_ID)
#             # Try common keys that may contain a playable/joinable URL
#             # st.write(resp)
#             call_url = (
#                 (resp or {}).get("call_url")
#                 or (resp or {}).get("webrtc_url")
#                 or (resp or {}).get("join_url")
#                 or (resp or {}).get("conversation_url")
#                 or ""
#             )
#             if call_url:
#                 st.session_state["call_url"] = call_url
#                 st.session_state["conversation_id"] = (resp or {}).get("conversation_id", "")
#                 st.session_state["opened_call_tab"] = False
#             else:
#                 st.warning("Conversation created but no call URL was returned.")
#                 st.json(resp)
#         except Exception as e:
#             st.error(f"Failed to start call: {e}")

# --- Display call controls if available ---
if st.session_state["call_url"]:
    url = st.session_state["call_url"]

    # Auto-open conversation in a new tab (run once per conversation)
    if not st.session_state["opened_call_tab"] and url:
        st.session_state["opened_call_tab"] = True
        st.markdown(
            f"""
            <script>
            window.open('{url}', '_blank');
            </script>
            """,
            unsafe_allow_html=True,
        )

    # st.markdown("### 🔊 Your AI Assistant is ready")
    st.link_button("📞 Start Call", url)

    st.markdown("#### Save lead from transcript")
    if st.button("Parse & Save from Transcript"):
        try:
            conv = get_conversation(st.session_state.get("conversation_id"))
            text = extract_transcript_text(conv)
            parsed = parse_lead_from_transcript_text(text)
            lead_id = save_lead(
                name=parsed.get("name"),
                email=parsed.get("email"),
                phone=parsed.get("phone"),
                company=None,
                conversation_id=st.session_state.get("conversation_id"),
                source="transcript",
                extra={"parsed": True},
            )
            st.success(f"Saved lead #{lead_id}")
        except Exception as e:
            st.error(f"Failed to parse/save lead: {e}")

    # End Call button (X)
    # if st.button("❌ End Call"):
    #     try:
    #         if st.session_state.get("conversation_id"):
    #             end_conversation(st.session_state["conversation_id"])
    #     except Exception as e:
    #         st.error(f"Failed to end call: {e}")
    #     finally:
    #         st.session_state["call_url"] = ""
    #         st.session_state["conversation_id"] = ""
    #         st.session_state["opened_call_tab"] = False

# --- About Section ---
html_code = """
<div style="margin-top:50px; text-align:center;">
  <h2>Broadgate Voice — Human-like AI Assistants</h2>
  <p>
    Build delightful voice experiences that understand context, speak naturally,
    and integrate with your stack. Our assistants handle customer support,
    booking flows, surveys, and more.
  </p>
  <a href="https://broadgatevoice.ai" target="_blank" style="text-decoration:none;">
    <button style="padding:10px 20px; border-radius:8px; background-color:#4CAF50; color:white; border:none;">
      Visit Website
    </button>
  </a>
</div>
"""
st.markdown(html_code, unsafe_allow_html=True)

st.divider()
st.caption("© 2025 Broadgate Voice — AI Assistants · Privacy · Terms")
