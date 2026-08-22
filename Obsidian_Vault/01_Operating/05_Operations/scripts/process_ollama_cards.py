#!/usr/bin/env python3
"""Quick card updates for Ollama cards."""
import sys, os, requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds['api_key'], creds['token']

# 1. Audit Ollama models card
audit_comment = (
    "OLLAMA MODEL AUDIT COMPLETE:\n"
    "- Models stored at vault path: D:/Work/.../03_AI_Operating_System/ollama/models/ (1.9GB total)\n"
    "- Active model: llama3.2:latest (only model, serving on port 11434)\n"
    "- Old C:\\Users\\torus\\AppData\\Local\\Programs\\Ollama\\models\\blobs path: EMPTY (does not exist)\n"
    "- No unused/obsolete models to clear\n"
    "- .gitignore + .git/info/exclude updated for model blobs\n"
    "- Ollama serve running with NVIDIA GeForce GT 1030 GPU detection\n"
    "- Card resolved: no action needed beyond verification."
)

r = requests.post("https://api.trello.com/1/cards/6a756b5d/actions/comments",
    params={"key": key, "token": token},
    data={"text": audit_comment}, timeout=10)
print(f"Audit comment: {r.status_code}")

r2 = requests.put("https://api.trello.com/1/cards/6a756b5d",
    params={"key": key, "token": token, "closed": "true"}, timeout=10)
print(f"Archive audit: {r2.status_code}")

# 2. Ollama K8s deployment card — Sir Green scope
k8s_comment = (
    "OODA: Ollama currently runs on PINKCADY (port 11434, llama3.2 model, GPU detected). "
    "Fleet-wide access via SQUIDSTATION k8s is a Sir Green action.\n\n"
    "STATUS: Local Ollama VERIFIED working. Vault-bound models at "
    "03_AI_Operating_System/ollama/.\n"
    "Next step: Sir Green to deploy Ollama container on SQUIDSTATION Kubernetes for fleet access.\n"
    "Owner: Sir Green | Follow-up: Sir Green"
)

r3 = requests.post("https://api.trello.com/1/cards/6a77c0b6/actions/comments",
    params={"key": key, "token": token},
    data={"text": k8s_comment}, timeout=10)
print(f"K8s comment: {r3.status_code}")
