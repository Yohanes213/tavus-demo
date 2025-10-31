import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
TAVUS_API_KEY = os.getenv("API_KEY")
BROADGATE_PERSONA_ID = os.getenv("BROADGATE_PERSONA_ID")
st.set_page_config(page_title="Broadgate Voice Assistant", layout="wide")

st.title("Talk to a Broadgate Voice Assistant")
st.write("Click the button below to start a conversation with our AI-powered assistant who can answer questions about our phone systems.")

if not BROADGATE_PERSONA_ID:
    st.error("Application is not configured correctly. Persona ID is missing.")
else:
    if st.button("Start Chat"):
        with st.spinner("Setting up your conversation..."):
            
            headers = {
                "x-api-key": TAVUS_API_KEY,
                "Content-Type": "application/json"
            }
            
            conversation_payload = {
                "replica_id": "rfe12d8b9597",  # Make sure this is a replica you want to use
                "persona_id": BROADGATE_PERSONA_ID, # <-- Use the predefined ID
                "document_ids": [
                    "d8-39ab4b27436b"
                ],
            }
            
            try:
                st.write("g")
                conversation_response = requests.post(
                    "https://tavusapi.com/v2/conversations", 
                    json=conversation_payload, 
                    headers=headers
                )
                conversation_response.raise_for_status()  # This will raise an error for bad responses (4xx or 5xx)
                conversation_data = conversation_response.json()
                conversation_url = conversation_data.get("conversation_url")

                if conversation_url:
                    # Embed the Video Chat
                    st.header("Join the Conversation")
                    st.components.v1.iframe(conversation_url, height=600, scrolling=True)
                else:
                    st.error("Could not retrieve the conversation URL. Please try again.")
                    st.write("API Response:", conversation_data) # For debugging

            except requests.exceptions.RequestException as e:
                st.error(f"An API error occurred: {e}")