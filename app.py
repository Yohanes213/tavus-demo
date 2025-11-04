import streamlit as st
import streamlit.components.v1 as components
import os
from dotenv import load_dotenv
from tavus_utils import create_conversation

# --- Load environment variables ---
load_dotenv()
TAVUS_API_KEY = os.getenv("API_KEY")
BROADGATE_PERSONA_ID = os.getenv("BROADGATE_PERSONA_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Google Sheets webhook URL

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

# Single "Start Call" button that creates conversation and opens tab
if st.button("📞 Start Call"):
    if not BROADGATE_PERSONA_ID:
        st.error("Missing BROADGATE_PERSONA_ID in environment. Please set it in your .env file.")
    elif not WEBHOOK_URL:
        st.warning("⚠️ WEBHOOK_URL not set. Webhooks will not work. Please set WEBHOOK_URL in your .env file with your Google Sheets webhook URL.")
        st.info("Continuing without webhook...")
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
                components.html(
                    f"""
                    <script>
                      window.open('{call_url}', '_blank');
                    </script>
                    """,
                    height=0,
                )
                st.success("Call started! If a new tab didn't open, use the link below.")
            else:
                st.warning("Conversation created but no call URL was returned.")
                st.json(resp)
        except Exception as e:
            st.error(f"Failed to start call: {e}")
    else:
        try:
            # Create conversation with webhook URL (Tavus will automatically send events to Google Sheets)
            resp = create_conversation(BROADGATE_PERSONA_ID, callback_url=WEBHOOK_URL)
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
                # Immediately open the call in a new tab (reliable via components)
                components.html(
                    f"""
                    <script>
                      window.open('{call_url}', '_blank');
                    </script>
                    """,
                    height=0,
                )
                st.success("✅ Call started! Webhooks are enabled. Your conversation data will be automatically saved to Google Sheets.")
                # st.info(f"📞 **Call URL:** {call_url}")
                # st.info(f"🆔 **Conversation ID:** {st.session_state['conversation_id']}")
            else:
                st.warning("Conversation created but no call URL was returned.")
                st.json(resp)
        except Exception as e:
            st.error(f"Failed to start call: {e}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())

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

st.header("Our Mission")
st.write(
    """
    At Broadgate Voice, our mission is to revolutionize communication through advanced AI. 
    We believe in creating seamless, intuitive, and highly intelligent voice assistants 
    that empower businesses and individuals to connect more effectively. 
    Our goal is to bridge the gap between human interaction and artificial intelligence, 
    making technology more accessible and helpful for everyone.
    """
)

st.header("Key Features")
st.markdown(
    """
    - **Natural Language Understanding:** Our AI comprehends complex queries with remarkable accuracy.
    - **Dynamic Personalities:** Customize your assistant's tone and style to match your brand.
    - **Seamless Integration:** Easily connect with your existing CRM, support, and sales platforms.
    - **Real-time Analytics:** Gain insights into conversation trends and agent performance.
    - **Multi-channel Support:** Deploy across web, mobile, and IVR systems.
    """
)

st.header("What Our Clients Say")
st.write(
    """
    "Broadgate Voice has transformed our customer support. The efficiency and customer satisfaction 
    have skyrocketed since we implemented their AI assistants." - **Jane Doe, CEO of Tech Innovations**

    "The natural voice and understanding of the AI is simply astounding. It feels like talking to a real person!" 
    - **John Smith, Founder of Global Solutions**
    """
)

st.divider()
st.caption("© 2025 Broadgate Voice — AI Assistants · Privacy · Terms")
