import streamlit as st
import requests

import os
from dotenv import load_dotenv

load_dotenv()
TAVUS_API_KEY = os.getenv("API_KEY")




st.title("Create Your Persona")

user_prompt = st.text_input("Describe the kind of person you want to talk to:")

if st.button("Create and Join Chat"):
    # 1. Create the Persona
    persona_payload = {
        "pipeline_mode": "full",
        "system_prompt": user_prompt
    }
    headers = {
        "x-api-key": TAVUS_API_KEY,
        "Content-Type": "application/json"
    }
    persona_response = requests.post("https://tavusapi.com/v2/personas", json=persona_payload, headers=headers)
    persona_data = persona_response.json()
    persona_id = persona_data.get("persona_id")

    if persona_id:
        # 2. Create the Conversation
        conversation_payload = {
            "replica_id": "rfe12d8b9597",
            "persona_id": persona_id,
            # You might need a replica_id as well, depending on your setup
        }
        conversation_response = requests.post("https://tavusapi.com/v2/conversations", json=conversation_payload, headers=headers)
        conversation_data = conversation_response.json()
        conversation_url = conversation_data.get("conversation_url")
        if conversation_url:
            # 3. Embed the Video Chat
            st.header("Join the Conversation")
            st.components.v1.iframe(conversation_url, height=600)
        else:
            st.error("Could not create the conversation.")
    else:
        st.error("Could not create the persona.")
