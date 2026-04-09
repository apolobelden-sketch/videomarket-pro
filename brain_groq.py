#!/usr/bin/env python3
import os, requests
KEY = os.getenv('GROQ_API_KEY')
if not KEY: print("❌ export GROQ_API_KEY='gsk_tu_key'"); exit(1)
def crear(n, i):
    print(f"🧠 {n}")
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": [
            {"role": "system", "content": "Experto web. Genera HTML completo."},
            {"role": "user", "content": f"Crea landing: {i}. HTML5+CSS responsive. Solo código."}
        ], "temperature": 0.7}, timeout=60)
    c = r.json()['choices'][0]['message']['content']
    c = '\n'.join([l for l in c.split('\n') if not l.strip().startswith('```')])
    with open(f"output/{n}.html", 'w') as f: f.write(c)
    print(f"✅ output/{n}.html")
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2: print("Uso: python brain_groq.py 'landing de relojes'"); exit()
    crear(sys.argv[1].replace(' ', '-')[:20], sys.argv[1])
