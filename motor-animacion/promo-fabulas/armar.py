#!/usr/bin/env python3
"""Arma la línea de tiempo del video promocional de "Fábulas para leer y escuchar"
sincronizada con la narración, y une los audios. Luego: python3 ../animar.py escenas.json video.mp4"""
import json, subprocess
TEMPO = 1.05; GAP = 0.25; FADE = 0.7
files = ['promo-a1', 'promo-a2', 'promo-a3', 'promo-a4', 'promo-a5']
dur = lambda f: float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))
durs = [dur(f + '.wav') for f in files]
# cortes dentro de cada audio (cambio de quien habla o de tema)
cortes = {0: [6.2], 1: [10.5], 2: [11.8], 3: [4.0, 8.0, 12.3], 4: [8.8]}
offs, t = [], 0
for d in durs: offs.append(t); t += d + GAP
total = (t - GAP) / TEMPO
starts = []
for i in range(len(files)):
    starts.append(offs[i]); starts += [offs[i] + c for c in cortes[i]]
starts = [s / TEMPO for s in starts]

M = lambda **k: k
sc = [
 M(img="01-carrera.jpg", de=[0.5,0.45,1.05], a=[0.5,0.5,1.15], rayos=0.4, chispas=0.7, titulo=["FÁBULAS","PARA LEER","Y ESCUCHAR"], texto_desde=0.3,
   mueve=[M(tipo="mece",c=[0.3,0.42],r=0.16,amp=26,f=2.6,dir=[0,-1],abs=True), M(tipo="gira",c=[0.3,0.35],p=[0.3,0.5],r=0.14,amp=5,f=1.3),
          M(tipo="mece",c=[0.68,0.56],r=0.16,amp=10,f=1.8,dir=[0,-1],abs=True), M(tipo="gira",c=[0.7,0.5],p=[0.7,0.62],r=0.14,amp=4,f=0.9),
          M(tipo="mece",c=[0.5,0.05],r=0.5,amp=14,f=0.4,dir=[1,0.2])]),
 M(img="02-tortuga-meta.jpg", de=[0.5,0.35,2.3], a=[0.5,0.34,2.45], chispas=1.0, texto="¡Despacito y sin rendirme!", y_texto=1600,
   mueve=[M(tipo="gira",c=[0.5,0.3],p=[0.5,0.55],r=0.2,amp=7,f=1.6), M(tipo="mece",c=[0.5,0.32],r=0.18,amp=14,f=3.2,dir=[0,-1],abs=True),
          M(tipo="mece",c=[0.3,0.38],r=0.08,amp=10,f=2.4,abs=True,dir=[0,-1]), M(tipo="mece",c=[0.72,0.38],r=0.08,amp=10,f=2.2,abs=True,dir=[0,-1],fase=1)]),
 M(img="portada.jpg", de=[0.5,0.5,1.05], a=[0.5,0.45,1.2], chispas=0.8, rayos=0.3, mueve=[]),
 M(img="03-leon-raton.jpg", de=[0.55,0.45,1.15], a=[0.6,0.5,1.35], rayos=0.5, chispas=0.6, texto="Nadie es tan pequeño que no pueda ayudar", y_texto=1640,
   mueve=[M(tipo="gira",c=[0.48,0.33],p=[0.5,0.7],r=0.32,amp=3.5,f=0.9), M(tipo="mece",c=[0.48,0.4],r=0.2,amp=8,f=2.4,dir=[0,1],abs=True),
          M(tipo="mece",c=[0.67,0.62],r=0.09,amp=12,f=2.2,dir=[0.3,-1],abs=True), M(tipo="gira",c=[0.67,0.58],p=[0.67,0.68],r=0.08,amp=8,f=1.1)]),
 M(img="04-nina-lee.jpg", de=[0.68,0.45,1.1], a=[0.62,0.5,1.3], chispas=1.0, texto="Escanea el QR: cada palabra se ilumina", y_texto=1640,
   mueve=[M(tipo="respira",c=[0.73,0.48],r=0.18,amp=0.03,f=0.4), M(tipo="gira",c=[0.75,0.25],p=[0.75,0.38],r=0.14,amp=4,f=0.45),
          M(tipo="mece",c=[0.6,0.6],r=0.1,amp=6,f=0.8,dir=[1,0]), M(tipo="mece",c=[0.98,0.65],r=0.1,amp=10,f=1.6,dir=[0,-1],abs=True),
          M(tipo="mece",c=[0.97,0.69],r=0.08,amp=8,f=1.9,dir=[0,-1],abs=True,fase=1)]),
 M(img="05-zorra.jpg", de=[0.45,0.5,1.1], a=[0.45,0.55,1.25], rayos=0.3, chispas=0.5, texto="¡Preguntas para ver si pusiste atención!", y_texto=1640,
   mueve=[M(tipo="gira",c=[0.45,0.45],p=[0.45,0.75],r=0.3,amp=5,f=0.9), M(tipo="mece",c=[0.2,0.38],r=0.08,amp=12,f=1.3,dir=[0,-1]),
          M(tipo="mece",c=[0.45,0.05],r=0.3,amp=10,f=0.6,dir=[1,0]), M(tipo="gira",c=[0.75,0.85],p=[0.62,0.85],r=0.18,amp=12,f=1.2)]),
 M(img="06-colorear.jpg", de=[0.5,0.55,1.05], a=[0.5,0.58,1.2], chispas=0.4, texto="Dibujos para colorear", y_texto=380,
   mueve=[M(tipo="mece",c=[0.33,0.86],r=0.16,amp=22,f=3.2,dir=[1,0.4]), M(tipo="mece",c=[0.65,0.85],r=0.16,amp=18,f=2.7,dir=[-1,0.5],fase=1)]),
 M(img="preguntas.jpg", de=[0.5,0.35,1.1], a=[0.5,0.55,1.1], chispas=0.3, texto="Moraleja, preguntas y palabras nuevas", y_texto=1650, mueve=[]),
 M(img="sopa.jpg", de=[0.5,0.55,1.2], a=[0.5,0.45,1.05], chispas=0.4, texto="Sopa de letras y diploma de Gran Lector", y_texto=1650, mueve=[]),
 M(img="07-hormiga-cigarra.jpg", de=[0.5,0.45,1.1], a=[0.5,0.42,1.3], rayos=0.5, chispas=1.0, texto="¡Junta las 10 estampas y gana tu diploma!", y_texto=1640,
   mueve=[M(tipo="mece",c=[0.27,0.5],r=0.2,amp=14,f=2.0,dir=[0,-1],abs=True), M(tipo="mece",c=[0.73,0.5],r=0.2,amp=14,f=2.0,dir=[0,-1],abs=True,fase=1.5),
          M(tipo="gira",c=[0.5,0.42],p=[0.5,0.5],r=0.1,amp=8,f=1.0), M(tipo="gira",c=[0.27,0.33],p=[0.27,0.45],r=0.1,amp=6,f=1.0),
          M(tipo="gira",c=[0.73,0.36],p=[0.73,0.48],r=0.1,amp=6,f=1.0,fase=1)]),
 M(img="08-familia.jpg", de=[0.55,0.5,1.05], a=[0.55,0.48,1.2], rayos=0.3, chispas=0.6, texto="Niños felices, papás orgullosos", y_texto=1650,
   mueve=[M(tipo="mece",c=[0.55,0.4],r=0.28,amp=7,f=2.2,dir=[0,1],abs=True), M(tipo="gira",c=[0.35,0.35],p=[0.35,0.5],r=0.1,amp=4,f=1.1),
          M(tipo="gira",c=[0.7,0.32],p=[0.7,0.48],r=0.1,amp=4,f=1.0,fase=1), M(tipo="mece",c=[0.8,0.85],r=0.12,amp=8,f=1.5,dir=[0,-1],abs=True)]),
 M(img="portada.jpg", de=[0.5,0.45,1.25], a=[0.5,0.5,1.0], rayos=0.5, chispas=1.0, titulo=["$59 MXN"], y_titulo=1180, texto="PDF + 10 audios. Link en el perfil", tam=60, color=[255,226,120], y_texto=1480, texto_desde=0.3, mueve=[]),
]
assert len(sc) == len(starts), (len(sc), len(starts))
for i, s in enumerate(sc):
    nxt = starts[i + 1] if i + 1 < len(starts) else total + 0.8
    s["dur"] = round(nxt - starts[i] + (FADE if i + 1 < len(sc) else 0), 3)
json.dump({"escenas": sc}, open('escenas.json', 'w'), ensure_ascii=False, indent=1)
inp, flt = [], ""
for i, f in enumerate(files):
    inp += ['-i', f + '.wav']; flt += f"[{i}]aresample=48000,apad=pad_dur={GAP}[x{i}];"
flt += "".join(f"[x{i}]" for i in range(len(files))) + f"concat=n={len(files)}:v=0:a=1,atempo={TEMPO},loudnorm=I=-15:TP=-1.5[a]"
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inp, '-filter_complex', flt, '-map', '[a]', '-ar', '48000', 'narracion.wav'], check=True)
print([round(s, 1) for s in starts], round(total, 1), dur('narracion.wav'))
