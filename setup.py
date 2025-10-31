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
'Broadgate Voice Knowledge Base' document provided. When asked a question, you must find 
the answer within that document. If the information is not in the document, you must clearly 
state 'I do not have that information in the provided brochure.' Do not make up answers. 
Be precise and quote prices and features directly from the text.
"""

def provision_resources():
    document = find_document_by_name(DOCUMENT_NAME)
    
    if not document:
        document = create_document_from_url(DOCUMENT_NAME, KNOWLEDGE_BASE_URL)
    
    time.sleep(60)
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