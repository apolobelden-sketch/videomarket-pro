#!/usr/bin/env python3
"""Video "El león y el ratón" — formato tipo libro (Fábrica de Videos, Ediciones Guizar).
Arriba: la animación de la IA (Wan 2.2 en Kaggle), sin zoom ni efectos propios.
Abajo: el texto del cuento en una hoja color crema; la palabra que se está narrando se pinta de rojo.
Sin música (Jairo la pone al subir). Narración Gemini, tiempos por palabra con Whisper (alinear-voz).
Uso (desde esta carpeta): python3 armar.py salida.mp4"""
import sys, json, subprocess, wave, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
ALTO_VIDEO = 1290            # parte de arriba: animación
F_TXT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
F_TIT = "/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf"
SR = 24000
MAX_SILENCIO = 0.28          # acorta pausas largas de la voz (deja el ritmo natural, baja la duración total)
VEL = 1.10                   # un poquito más ágil, sin que suene acelerada
PAUSA_ESCENA = 0.25
CIERRE = 3.2

SEG = [
 ["El león y el ratón.", "Un gran león dormía tranquilo bajo la sombra de un árbol."],
 ["De pronto, un ratoncito curioso corrió por su nariz…", "¡y lo despertó!"],
 ["El león lo atrapó con su enorme garra.", "«¡Por favor, déjame ir! Algún día yo te ayudaré», suplicó el ratón."],
 ["El león se rio: «¿Tú, tan pequeñito, ayudarme a mí?».", "Y lo dejó ir."],
 ["Días después, el león cayó en la red de unos cazadores.", "Rugía y rugía, pero no podía escapar."],
 ["El ratoncito lo escuchó, llegó corriendo", "y mordió la cuerda hasta liberarlo."],
 ["Desde ese día fueron grandes amigos.", "Moraleja: nadie es tan pequeño que no pueda ayudar."],
]

def leer_wav(p):
    with wave.open(p) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)

def acortar(x, tiempos):
    """Recorta silencios > MAX_SILENCIO y devuelve el audio y los tiempos de palabra recolocados."""
    v = np.abs(x); win = int(0.02 * SR)
    env = np.convolve(v, np.ones(win) / win, "same")
    callado = env < max(250, 0.04 * np.percentile(env, 99))
    keep = np.ones(len(x), bool); i = 0
    while i < len(x):
        if callado[i]:
            j = i
            while j < len(x) and callado[j]: j += 1
            largo = j - i; maxi = int(MAX_SILENCIO * SR)
            if largo > maxi:
                a = i + maxi // 2; b = j - maxi // 2
                if i == 0: a = i + int(0.08 * SR)
                if j == len(x): b = j - int(0.15 * SR)
                keep[a:b] = False
            i = j
        else: i += 1
    mapa = np.cumsum(keep) - 1
    y = x[keep]
    def m(t):
        k = min(int(t * SR), len(x) - 1)
        return max(mapa[k], 0) / SR
    return y, [[m(a), m(b)] for a, b in tiempos]

# 1) voz por escena
audios, tiempos, dur = [], [], []
for i in range(7):
    x = leer_wav(f"voz-{i+1}.wav")
    t = json.load(open(f"voz-{i+1}.tiempos.json"))["t"]
    y, t2 = acortar(x, t)
    audios.append(y); tiempos.append(t2); dur.append(len(y) / SR / VEL)
INI = [0.4]
for d in dur[:-1]: INI.append(INI[-1] + d + PAUSA_ESCENA)
FIN_HIST = INI[-1] + dur[-1] + 0.6
FIN = FIN_HIST + CIERRE

# audio completo (se acelera con atempo al final)
total = np.zeros(int(FIN * VEL * SR) + SR, np.float32)
for i, y in enumerate(audios):
    k = int(INI[i] * VEL * SR); total[k:k + len(y)] += y
with wave.open("/tmp/voz_leon.wav", "w") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(np.clip(total, -32768, 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "/tmp/voz_leon.wav", "-af", f"atempo={VEL},loudnorm=I=-15:TP=-1.5", "-ar", "44100", "/tmp/voz_leon2.wav"], check=True)

# 2) clips IA
def leer_clip(n):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", f"clip-e{n}.mp4", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(p, np.uint8).reshape(-1, 832, 480, 3)
CL = [leer_clip(i + 1) for i in range(7)]

def zona_video(fr):  # ancho completo; recorte vertical centrado en la parte de arriba
    s = W / fr.shape[1]; nh = round(fr.shape[0] * s)
    big = cv2.resize(fr, (W, nh), interpolation=cv2.INTER_LANCZOS4)
    y0 = max((nh - ALTO_VIDEO) // 2 - 60, 0)
    return big[y0:y0 + ALTO_VIDEO]

# 3) hoja de texto
f = ImageFont.truetype(F_TXT, 64)
CREMA, TINTA, ROJO = (255, 248, 231), (74, 44, 20), (214, 30, 36)
def maquetar(i):
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    pal = " ".join(SEG[i]).split()
    lineas, act = [], []
    for p in pal:
        if d.textlength(" ".join(act + [p]), font=f) > W - 130 and act: lineas.append(act); act = [p]
        else: act.append(p)
    lineas.append(act)
    pos, lh = [], 92
    alto = lh * len(lineas); y = ALTO_VIDEO + (H - ALTO_VIDEO - alto) // 2 + 10
    for li, l in enumerate(lineas):
        x = (W - d.textlength(" ".join(l), font=f)) / 2
        for p in l:
            pos.append((p, x, y + li * lh)); x += d.textlength(p + " ", font=f)
    return pos
MAQ = [maquetar(i) for i in range(7)]

def hoja(i, t_local):
    im = Image.new("RGB", (W, H - ALTO_VIDEO), CREMA); d = ImageDraw.Draw(im)
    d.line((60, 18, W - 60, 18), fill=(222, 196, 150), width=4)
    ta = t_local * 1.0
    for k, (p, x, y) in enumerate(MAQ[i]):
        a, b = tiempos[i][k] if k < len(tiempos[i]) else (99, 99)
        a /= VEL; b /= VEL
        sig = (tiempos[i][k + 1][0] / VEL) if k + 1 < len(tiempos[i]) else b + 0.3
        col = ROJO if a - 0.04 <= ta < min(b + 0.1, sig - 0.04) else TINTA
        d.text((x, y - ALTO_VIDEO), p, font=f, fill=col)
    d.text((W - 300, H - ALTO_VIDEO - 62), "Ediciones Guizar", font=ImageFont.truetype(F_TXT, 30), fill=(180, 140, 90))
    return np.asarray(im, np.float32)

def titulo_capa():
    im = Image.new("RGBA", (W, ALTO_VIDEO), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ft = ImageFont.truetype(F_TIT, 118); y = 120
    for l in ["EL LEÓN", "Y EL RATÓN"]:
        w = d.textlength(l, font=ft)
        d.text(((W - w) / 2 + 6, y + 8), l, font=ft, fill=(60, 25, 0, 150))
        d.text(((W - w) / 2, y), l, font=ft, fill=(255, 214, 92, 255), stroke_width=7, stroke_fill=(90, 40, 5, 255)); y += 145
    a = np.asarray(im, np.float32); return a[..., :3], a[..., 3:] / 255
TIT = titulo_capa()

def cierre():
    im = Image.new("RGB", (W, H), CREMA); d = ImageDraw.Draw(im)
    try:
        p = Image.open("../promo-fabulas/portada.jpg").convert("RGB"); s = 760 / p.width
        p = p.resize((760, round(p.height * s))); im.paste(p, ((W - 760) // 2, 200))
        yb = 200 + p.height + 60
    except Exception: yb = 700
    for txt, tam, col in [("Fábulas para leer y escuchar", 58, TINTA), ("Link en el perfil", 52, ROJO)]:
        ft = ImageFont.truetype(F_TXT, tam); w = d.textlength(txt, font=ft); d.text(((W - w) / 2, yb), txt, font=ft, fill=col); yb += tam + 40
    return np.asarray(im, np.float32)
CIE = cierre()

def escena(t):
    i = max(j for j in range(7) if INI[j] <= t) if t >= INI[0] else 0
    return i

pipe = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                         "-i", "/tmp/voz_leon2.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", sys.argv[1]], stdin=subprocess.PIPE)
FADE = 0.45
def cuadro_escena(i, tl):
    fs = CL[i]; D = len(fs) / 24.0
    larga = (INI[i + 1] if i < 6 else FIN_HIST) - INI[i] + 0.3
    fct = min(max(larga / D, 1.0), 1.5)          # cámara lenta suave (máx 1.5x), nunca hacia atrás
    k = min(int(max(tl, 0) / fct * 24), len(fs) - 1)
    top = zona_video(fs[k]).astype(np.float32)
    if i == 0:
        rgb, al = TIT; m = min(1.0, max(0.0, (tl - 0.2) / 0.5)) * min(1.0, max(0.0, (3.6 - tl) / 0.5))
        top = top * (1 - al * m) + rgb * al * m
    return np.vstack([top, hoja(i, tl)])

for n in range(int(FIN * FPS)):
    t = n / FPS
    if t >= FIN_HIST:
        m = min(1.0, (t - FIN_HIST) / 0.5)
        fr = cuadro_escena(6, t - INI[6]) * (1 - m) + CIE * m
    else:
        i = escena(t); tl = t - INI[i]
        fr = cuadro_escena(i, tl)
        if i > 0 and tl < FADE:
            m = tl / FADE; m = m * m * (3 - 2 * m)
            prev = cuadro_escena(i - 1, t - INI[i - 1])
            fr[:ALTO_VIDEO] = prev[:ALTO_VIDEO] * (1 - m) + fr[:ALTO_VIDEO] * m
    g = min(1.0, t / 0.4, (FIN - t) / 0.6)
    pipe.stdin.write(np.clip(fr * g, 0, 255).astype(np.uint8).tobytes())
pipe.stdin.close(); pipe.wait()
print("listo", round(FIN, 1), "s; escenas", [round(x, 1) for x in INI])
