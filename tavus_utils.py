# tavus_utils.py
import os
import re
import json
import sqlite3
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

# ---------- API ----------
def _headers():
    key = os.getenv("API_KEY")
    if not key:
        raise ValueError("API_KEY missing in .env")
    return {"x-api-key": key}

# ---- documents ----
def find_document_by_name(name: str):
    r = requests.get("https://tavusapi.com/v2/documents", headers=_headers())
    r.raise_for_status()
    for d in r.json().get("data", []):
        if d.get("document_name") == name:
            return d
    return None

def create_document_from_url(name: str, url: str):
    payload = {"document_name": name, "document_url": url}
    r = requests.post("https://tavusapi.com/v2/documents", json=payload, headers=_headers())
    r.raise_for_status()
    return r.json()

# ---- personas ----
def find_persona_by_name(name: str):
    r = requests.get("https://tavusapi.com/v2/personas", headers=_headers())
    r.raise_for_status()
    for p in r.json().get("data", []):
        if p.get("persona_name") == name:
            return p
    return None

def create_persona(name: str, system_prompt: str, document_ids: list):
    payload = {
        "pipeline_mode": "full",
        "persona_name": name,
        "system_prompt": system_prompt,
        "document_ids": document_ids,
    }
    r = requests.post("https://tavusapi.com/v2/personas", json=payload, headers=_headers())
    r.raise_for_status()
    return r.json()

# ---- conversations ----
def create_conversation(persona_id: str, replica_id: str = "rfe12d8b9597", callback_url: str = None):
    payload = {"persona_id": persona_id, "replica_id": replica_id}
    if callback_url:
        payload["callback_url"] = callback_url
    r = requests.post("https://tavusapi.com/v2/conversations", json=payload, headers=_headers())
    r.raise_for_status()
    return r.json()

def end_conversation(conv_id: str):
    if not conv_id:
        raise ValueError("conv_id required")
    r = requests.post(f"https://tavusapi.com/v2/conversations/{conv_id}/end", headers=_headers())
    r.raise_for_status()
    # Check if the response has content and is JSON before trying to parse
    if r.status_code == 200 and r.headers.get('Content-Type', '').startswith('application/json'):
        return r.json()
    return {"status": "success", "message": "Conversation ended, no JSON response."} # Return a default success message or handle as needed

def get_conversation_messages(conv_id: str):
    if not conv_id:
        return []
    r = requests.get(f"https://tavusapi.com/v2/conversations/{conv_id}/messages", headers=_headers())
    if r.status_code == 404:
        return []
    r.raise_for_status()
    data = r.json()
    return data.get("data", data if isinstance(data, list) else [])

def extract_transcript_text(conv_id: str) -> str:
    """
    Extract transcript text from conversation messages.
    Returns a single string containing all message text.
    """
    messages = get_conversation_messages(conv_id)
    if not messages:
        return ""
    
    transcript_parts = []
    for msg in messages:
        # Try different possible keys for message text
        text = (
            msg.get("text") or 
            msg.get("content") or 
            msg.get("message") or 
            msg.get("transcript") or
            ""
        )
        if text:
            transcript_parts.append(str(text))
    
    return "\n".join(transcript_parts)

# ---------- SQLite ----------
DB_PATH = "leads.db"

# === DB: Auto-migrate ===
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conv_id TEXT,
            name TEXT,
            email TEXT
        )
    """)
    cur.execute("PRAGMA table_info(leads)")
    cols = [c[1] for c in cur.fetchall()]
    if 'ts' not in cols:
        cur.execute("ALTER TABLE leads ADD COLUMN ts TEXT")
    conn.commit()
    conn.close()

def save_lead(conv_id, name=None, email=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO leads (conv_id, name, email, ts) VALUES (?, ?, ?, ?)",
        (conv_id, name, email, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

# === Webhook: Instant ===
def send_to_webhook(conv_id, name=None, email=None, transcript_text=""):
    url = os.getenv("WEBHOOK_URL")
    if not url:
        return
    payload = {
        "conversation_id": conv_id,
        "name": name or "",
        "email": email or "",
        "transcript": transcript_text,
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        requests.post(url, json=payload, timeout=5)
        print(f"Webhook sent: {payload}")
    except Exception as e:
        print(f"Webhook failed: {e}")

def extract_info_and_send_webhook(conv_id: str):
    if not conv_id:
        print("No conversation ID provided for webhook processing.")
        return

    transcript_text = extract_transcript_text(conv_id)
    name = None
    email = None

    # Simple regex to extract name (assuming "My name is [Name]" or similar)
    name_match = re.search(r"(?:my name is|i'm)\s+([a-zA-Z\s]+)", transcript_text, re.IGNORECASE)
    if name_match:
        name = name_match.group(1).strip()

    # Simple regex to extract email
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", transcript_text)
    if email_match:
        email = email_match.group(0)

    print(f"Extracted Name: {name}, Email: {email} from conversation {conv_id}")
    send_to_webhook(conv_id, name, email, transcript_text)
    save_lead(conv_id, name, email) # Also save to local SQLite DB