# setup.py

import os
from dotenv import load_dotenv
from tavus_utils import (
    find_document_by_name,
    create_document_from_url,
    find_persona_by_name,
    create_persona
)

load_dotenv()
import time

# --- Configuration ---
DOCUMENT_NAME = "Broadgate Voice Knowledge Base v1"
PERSONA_NAME = "Broadgate Voice Assistant v1"

KNOWLEDGE_BASE_URL = "https://pastebin.com/FU1LPXZu" 

PERSONA_SYSTEM_PROMPT = """
You are a specialized assistant for Broadgate Voice. Your ONLY source of information is the
'Broadgate Voice Knowledge Base' document provided.

STRICT CONVERSATION FLOW:
1. ALWAYS start by warmly greeting and asking: "May I have your name please?"
2. Once they give their name, say: "Nice to meet you, [Name]! Could you please share your email so I can send you more info?"
3. Then proceed with answering questions from the knowledge base.

If asked anything not in the document, say: "I do not have that information in the provided brochure."

Be friendly, professional, and natural.
"""

def provision_resources():
    document = find_document_by_name(DOCUMENT_NAME)
    
    if not document:
        document = create_document_from_url(DOCUMENT_NAME, KNOWLEDGE_BASE_URL)
    
    # time.sleep(60)
    document_id = document.get("document_id")
    if not document_id:
        print("ERROR: Could not get Document ID.")
        return
    persona = find_persona_by_name(PERSONA_NAME)
    if not persona:
        persona = create_persona(PERSONA_NAME, PERSONA_SYSTEM_PROMPT, [document_id])

    persona_id = persona.get("persona_id")
    if not persona_id:
        print("ERROR: Could not get Persona ID.")
        return

    print("\n" + "="*50)
    print("SETUP COMPLETE!")
    print(f"Your Persona ID is: {persona_id}")
    print("Please copy this ID and paste it into your .env file...")
    print("="*50)

if __name__ == "__main__":
    provision_resources()