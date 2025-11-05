import streamlit as st
import streamlit.components.v1 as components
import os
from dotenv import load_dotenv
from tavus_utils import create_conversation
import traceback

# --- Load environment variables ---
load_dotenv()
TAVUS_API_KEY = os.getenv("API_KEY")
BROADGATE_PERSONA_ID = os.getenv("BROADGATE_PERSONA_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Google Sheets webhook URL

# --- Page setup ---
st.set_page_config(page_title="Broadgate Voice Assistant", layout="wide")

# --- Custom CSS for a MUCH WIDER Modal ---
# This CSS is more specific and uses !important to force the override.
st.markdown("""
<style>
    /* Target the root of the dialog/modal by its role attribute */
    div[role="dialog"] > div:first-child {
        width: 90vw !important;         /* Use 90% of the viewport width */
        max-width: 1400px !important;   /* Set a very large max-width */
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
# Manages the state of the modal and call URL.
if "call_url" not in st.session_state:
    st.session_state.call_url = None
if "show_modal" not in st.session_state:
    st.session_state.show_modal = False
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = ""

# --- Dialog/Modal for the Call ---
# This dialog will only be displayed when st.session_state.show_modal is True.
@st.dialog("Join the Conversation")
def show_call_modal():
    if st.session_state.call_url:
        # Embed the Tavus call within an iframe inside the modal with a larger height
        components.iframe(st.session_state.call_url, height=750, width=3000)
    else:
        st.error("Call URL not found. Please try starting the call again.")
    if st.button("End Call & Close"):
        st.session_state.show_modal = False
        st.rerun()

# --- Main Page UI ---
st.title("🎙️ Talk to a Broadgate Voice Assistant")
st.write("Click the animation below to start a conversation with our AI-powered assistant.")


# --- Clickable GIF using st.html (with controlled size) ---
GIF_URL = "https://raw.githubusercontent.com/Yohanes213/tavus-demo/main/ezgif-72d92bc4c273d5.gif"

# Wrap in a container to apply centering and max-width
with st.container():
    st.html(f"""
        <div style="display: flex; justify-content: center;">
            <a href="?start_call=true" target="_self" style="max-width: 700px; width: 100%;">
                <img src="{GIF_URL}" style="width: 100%; border-radius: 12px; cursor: pointer;">
            </a>
        </div>
    """)


# --- Main Logic: Triggered by Query Parameter ---
# This block checks if the user has clicked the GIF link.
if "start_call" in st.query_params:
    if not BROADGATE_PERSONA_ID:
        st.error("Missing BROADGATE_PERSONA_ID in environment. Please set it in your .env file.")
    else:
        with st.spinner("🚀 Connecting you to the assistant..."):
            try:
                # Use webhook if URL is provided
                if WEBHOOK_URL:
                    resp = create_conversation(BROADGATE_PERSONA_ID, callback_url=WEBHOOK_URL)
                else:
                    st.warning("⚠️ WEBHOOK_URL not set. Webhooks will not work.", icon="🤖")
                    resp = create_conversation(BROADGATE_PERSONA_ID)

                call_url = (
                    (resp or {}).get("call_url")
                    or (resp or {}).get("webrtc_url")
                    or (resp or {}).get("join_url")
                    or (resp or {}).get("conversation_url")
                    or ""
                )

                if call_url:
                    st.session_state.call_url = call_url
                    st.session_state.conversation_id = (resp or {}).get("conversation_id", "")
                    st.session_state.show_modal = True  # Set the flag to show the modal
                else:
                    st.warning("Conversation created, but no call URL was returned by the API.")
                    st.json(resp)

            except Exception as e:
                st.error(f"Failed to start the call: {e}")
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())

    # IMPORTANT: Clear the query parameter to prevent re-triggering
    st.query_params.clear()


# --- Display the Modal if the flag is set ---
if st.session_state.show_modal:
    show_call_modal()


# --- About Section (No changes needed below) ---
html_code = """
<div style="margin-top:50px; text-align:center;">
  <h2>Broadgate Voice — Human-like AI Assistants</h2>
  <p>
    Build delightful voice experiences that understand context, speak naturally,
    and integrate with your stack. Our assistants handle customer support,
    booking flows, surveys, and more.
  </p>
  <a href="https://broadgatevoice.ai" target="_blank" style="text-decoration:none;">
    <button style="padding:10px 20px; border-radius:8px; background-color:#4CAF50; color:white; border:none; cursor:pointer;">
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