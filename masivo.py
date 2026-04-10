import sys, time, os
with open(sys.argv[1]) as f:
    items = [l.strip() for l in f if l.strip()]
for i, item in enumerate(items, 1):
    print(f"\n🎯 {i}/{len(items)}: {item}")
    os.system(f'python brain_groq.py "landing de {item}"')
    if i < len(items):
        print("⏳ Esperando 3s...")
        time.sleep(3)
print(f"\n✅ {len(items)} landings creadas!")
