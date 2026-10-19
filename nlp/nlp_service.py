from flask import Flask, request, jsonify
from groq import Groq
import os, json, requests, sys
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))
load_dotenv(ENV_PATH)
app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PROVIDER = os.getenv("AURA_LLM_PROVIDER", "GROQ")

def call_groq(text):
    try:
        model = os.getenv("GROQ_NLP_MODEL", "groq/compound-mini")
        response = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f'User said: "{text}"'}
            ],
            temperature=0.1,
            max_tokens=300,
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as e:
        print(f"[NLP GROQ ERROR] {e}")
        return None

def call_ollama(text):
    try:
        url = os.getenv("OLLAMA_NLP_URL", "http://localhost:11434/api/chat")
        model = os.getenv("OLLAMA_NLP_MODEL", "llama3.2")
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f'User said: "{text}"'}
            ],
            "options": {
                "temperature": 0.1
            },
            "stream": False
        }
        r = requests.post(url, json=payload, timeout=15)
        r.raise_for_status()
        raw = r.json()["message"]["content"].strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as e:
        print(f"[NLP OLLAMA ERROR] {e}")
        return None

def call_llm(text):
    if PROVIDER == "OLLAMA":
        print("[NLP] Parsing via local Ollama...")
        res = call_ollama(text)
        if res is not None:
            return res
        print("[NLP WARNING] Ollama failed, falling back to Groq...")
    
    return call_groq(text) or {"intent": "general", "tool": "general", "params": {"response": "Sorry, NLP services are currently unavailable."}}

@app.route('/parse', methods=['POST'])
def parse():
    data = request.get_json() or {}
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "No text provided"}), 400
    result = call_llm(text)
    if not isinstance(result, dict):
        result = {"intent": "general", "tool": "general", "params": {"response": "Sorry, I couldn't understand that."}}
    print(f"[NLP] '{text}' -> {result}")
    return jsonify(result)

if __name__ == '__main__':
    print("NLP Service running on port 5002...")
    app.run(port=5002, debug=False)
