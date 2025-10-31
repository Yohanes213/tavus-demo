# tavus_utils.py

import requests
import os
from dotenv import load_dotenv

load_dotenv() 

def _get_headers():
    """Returns the authorization headers for Tavus API calls."""
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY is not set in the environment.")
    return {"x-api-key": api_key}

def find_document_by_name(name):
    """Finds a Tavus document by its name. Returns the document object or None."""
    print(f"Searching for document named '{name}'...")
    response = requests.get("https://tavusapi.com/v2/documents", headers=_get_headers())
    response.raise_for_status()
    documents = response.json()
    for doc in documents["data"]:
        print(doc)
        if doc.get("document_name") == name:
            print("Found existing document.")
            return doc
    print("Document not found.")
    return None

def create_document_from_url(name, url):
    """Creates a new document in Tavus from a public URL."""
    print(f"Creating new document '{name}' from URL...")
    payload = {
        "document_url": url,
        "document_name": name
    }
    response = requests.post("https://tavusapi.com/v2/documents", json=payload, headers=_get_headers())
    response.raise_for_status()
    print("Successfully created document.")
    return response.json()

def find_persona_by_name(name):
    """Finds a Tavus persona by its name. Returns the persona object or None."""
    print(f"Searching for persona named '{name}'...")
    response = requests.get("https://tavusapi.com/v2/personas", headers=_get_headers())
    response.raise_for_status()
    personas = response.json()
    for persona in personas["data"]:
        print(persona.get("persona_name"))
        if persona.get("persona_name") == name:
            print("Found existing persona.")
            return persona
    print("Persona not found.")
    return None

def create_persona(name, system_prompt, document_ids):
    """Creates a new persona in Tavus."""
    print(f"Creating new persona named '{name}'...")
    payload = {
        "pipeline_mode": "full",
        "persona_name": name,
        "system_prompt": system_prompt,
        "document_ids": document_ids
    }
    response = requests.post("https://tavusapi.com/v2/personas", json=payload, headers=_get_headers())
    response.raise_for_status()
    print("Successfully created persona.")
    return response.json()

def create_conversation(persona_id, replica_id="rfe12d8b9597"):
    """Creates a new conversation with a given persona.
    metadata: Optional dict passed through to Tavus to associate lead/contact context.
    """
    payload = {
        "replica_id": replica_id,
        "persona_id": persona_id,
    }
    response = requests.post("https://tavusapi.com/v2/conversations", json=payload, headers=_get_headers())
    response.raise_for_status()
    return response.json()

def end_conversation(conversation_id):
    """Ends an active conversation by ID."""
    if not conversation_id:
        raise ValueError("conversation_id is required to end a conversation")
    url = f"https://tavusapi.com/v2/conversations/{conversation_id}/end"
    response = requests.post(url, headers=_get_headers())
    response.raise_for_status()
    return response.json()

def get_conversation(conversation_id):
    if not conversation_id:
        raise ValueError("conversation_id is required")
    url = f"https://tavusapi.com/v2/conversations/{conversation_id}"
    response = requests.get(url, headers=_get_headers())
    response.raise_for_status()
    return response.json()


def get_conversation_messages(conversation_id):
    if not conversation_id:
        raise ValueError("conversation_id is required")
    url = f"https://tavusapi.com/v2/conversations/{conversation_id}/messages"
    response = requests.get(url, headers=_get_headers())
    if response.status_code == 404:
        return []
    response.raise_for_status()
    data = response.json()
    # Normalize to a list of strings if possible
    if isinstance(data, dict) and "data" in data:
        return data["data"]
    if isinstance(data, list):
        return data
    return []


def extract_transcript_text(conv_payload):
    """Try common fields to obtain a plaintext transcript."""
    if not conv_payload:
        return ""
    for key in ["transcript", "full_transcript", "conversation_transcript"]:
        val = conv_payload.get(key)
        if isinstance(val, str) and val.strip():
            return val
    messages = conv_payload.get("messages")
    if isinstance(messages, list) and messages:
        parts = []
        for msg in messages:
            text = msg.get("text") or msg.get("content") or ""
            if text:
                parts.append(text)
        if parts:
            return "\n".join(parts)
    return ""