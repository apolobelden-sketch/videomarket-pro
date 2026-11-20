#!/usr/bin/env python3
"""Motor de animación gratis: convierte dibujos fijos en un video vertical animado.
Uso: python3 animar.py escenas.json salida.mp4
Sin música ni voz. Todo local con Python + ffmpeg (costo cero)."""
import json, math, sys, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
FADE = 0.7
F_TXT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
F_TIT = "/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf"

cfg = json.load(open(sys.argv[1]))
out = sys.argv[2]
escenas = cfg["escenas"]

def ease(x):  # suave al entrar y salir
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)

# ---------- imágenes base ----------
cache = {}
def base(path):
    if path not in cache:
        im = Image.open(path).convert("RGB")
        # escala para cubrir 1080x1920 con margen para la cámara
        s = max(W / im.width, H / im.height) * 1.0
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
        cache[path] = im
    return cache[path]

def camara(im, cx, cy, z, dx=0, dy=0):
    """cx,cy: centro normalizado en la imagen; z: acercamiento (1 = cuadro completo)."""
    iw, ih = im.size
    vw, vh = W / z * (iw / W), H / z * (ih / H)  # tamaño de la ventana en px de la imagen
    vw, vh = iw / z, ih / z
    x0 = min(max(cx * iw - vw / 2 + dx, 0), iw - vw)
    y0 = min(max(cy * ih - vh / 2 + dy, 0), ih - vh)
    a = vw / W
    e = vh / H
    return im.transform((W, H), Image.AFFINE, (a, 0, x0, 0, e, y0), resample=Image.BICUBIC)

# ---------- movimiento de personajes (deformación tipo títere) ----------
import cv2
def deforma(arr, movs, t):
    """Mueve partes del dibujo: respira, gira (cabeza, cola, red), mece (ratón, hojas, caminar)."""
    if not movs: return arr
    h, w = arr.shape[:2]; q = 4
    gy, gx = np.mgrid[0:h:q, 0:w:q].astype(np.float32)
    dx = np.zeros_like(gx); dy = np.zeros_like(gy)
    for m in movs:
        cx, cy = m["c"][0] * w, m["c"][1] * h
        R = m["r"] * w
        d2 = ((gx - cx) ** 2 + (gy - cy) ** 2) / (R * R)
        wgt = np.clip(1 - d2, 0, 1) ** 2
        s = math.sin(2 * math.pi * m["f"] * t + m.get("fase", 0))
        if m["tipo"] == "respira":
            k = m["amp"] * (0.5 + 0.5 * s)
            dx += (gx - cx) * k * wgt; dy += (gy - cy) * k * wgt * 1.3
        elif m["tipo"] == "gira":
            px, py = m.get("p", m["c"])[0] * w, m.get("p", m["c"])[1] * h
            a = math.radians(m["amp"] * s)
            rx, ry = gx - px, gy - py
            dx += (rx * math.cos(a) - ry * math.sin(a) - rx) * wgt
            dy += (rx * math.sin(a) + ry * math.cos(a) - ry) * wgt
        elif m["tipo"] == "mece":
            v = m.get("dir", [0, 1])
            val = s if not m.get("abs") else abs(s)
            dx += v[0] * m["amp"] * val * wgt; dy += v[1] * m["amp"] * val * wgt
    dx = cv2.resize(dx, (w, h)); dy = cv2.resize(dy, (w, h))
    X, Y = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    return cv2.remap(arr, X - dx, Y - dy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

# ---------- capas de efectos ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIGN = (1 - 0.38 * np.clip(r - 0.55, 0, 1) ** 1.6)[..., None].astype(np.float32)

def rayos():
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    rnd = random.Random(3)
    for _ in range(9):
        x = rnd.randint(-200, W)
        w = rnd.randint(40, 140)
        d.polygon([(x, -50), (x + w, -50), (x + w + 700, H), (x + 700, H)], fill=rnd.randint(40, 90))
    im = im.filter(ImageFilter.GaussianBlur(45))
    return (np.asarray(im, np.float32) / 255.0)[..., None] * np.array([1.0, 0.85, 0.55], np.float32)
RAYOS = rayos()

def sprite(rad):
    s = np.zeros((rad * 2 + 1, rad * 2 + 1), np.float32)
    y, x = np.mgrid[-rad:rad + 1, -rad:rad + 1]
    s = np.exp(-(x * x + y * y) / (2 * (rad / 3) ** 2))
    return s.astype(np.float32)
SPR = {k: sprite(k) for k in (10, 16, 24)}
rnd = random.Random(11)
PART = [dict(x=rnd.random() * W, y=rnd.random() * H, vx=rnd.uniform(-12, 12), vy=rnd.uniform(-35, -10),
             f=rnd.uniform(0.6, 1.8), ph=rnd.random() * 6.28, k=rnd.choice((10, 16, 24))) for _ in range(38)]

def particulas(fr, t, fuerza):
    if fuerza <= 0: return fr
    add = np.zeros((H, W), np.float32)
    for p in PART:
        x = (p["x"] + p["vx"] * t + 25 * math.sin(t * 0.7 + p["ph"])) % W
        y = (p["y"] + p["vy"] * t) % H
        a = (0.5 + 0.5 * math.sin(t * p["f"] * 2 + p["ph"])) * fuerza
        k = p["k"]; s = SPR[k]
        xi, yi = int(x), int(y)
        x0, y0, x1, y1 = max(xi - k, 0), max(yi - k, 0), min(xi + k + 1, W), min(yi + k + 1, H)
        if x1 <= x0 or y1 <= y0: continue
        add[y0:y1, x0:x1] += s[y0 - yi + k:y1 - yi + k, x0 - xi + k:x1 - xi + k] * a
    return fr + add[..., None] * np.array([255, 225, 140], np.float32)

# ---------- textos ----------
def capa_texto(e):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if e.get("titulo"):
        f = ImageFont.truetype(F_TIT, 132)
        y = 260
        for linea in e["titulo"]:
            w = d.textlength(linea, font=f)
            d.text(((W - w) / 2 + 6, y + 8), linea, font=f, fill=(60, 25, 0, 150))
            d.text(((W - w) / 2, y), linea, font=f, fill=(255, 214, 92, 255), stroke_width=7, stroke_fill=(90, 40, 5, 255))
            y += 160
    if e.get("texto"):
        size = e.get("tam", 62)
        f = ImageFont.truetype(F_TXT, size)
        palabras, lineas, act = e["texto"].split(), [], ""
        for p in palabras:
            prueba = (act + " " + p).strip()
            if d.textlength(prueba, font=f) > W - 150: lineas.append(act); act = p
            else: act = prueba
        lineas.append(act)
        lh = int(size * 1.32)
        alto = lh * len(lineas)
        y = e.get("y_texto", 1440) - alto // 2
        caja = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(caja).rounded_rectangle((45, y - 40, W - 45, y + alto + 30), 46, fill=(25, 12, 0, 120))
        caja = caja.filter(ImageFilter.GaussianBlur(6))
        im = Image.alpha_composite(caja, im); d = ImageDraw.Draw(im)
        for i, l in enumerate(lineas):
            w = d.textlength(l, font=f)
            color = tuple(e.get("color", (255, 248, 230))) + (255,)
            d.text(((W - w) / 2, y + i * lh), l, font=f, fill=color, stroke_width=4, stroke_fill=(40, 18, 0, 255))
    if e.get("marca"):
        f = ImageFont.truetype(F_TXT, 46)
        w = d.textlength(e["marca"], font=f)
        d.text(((W - w) / 2, H - 230), e["marca"], font=f, fill=(255, 240, 210, 255), stroke_width=3, stroke_fill=(40, 18, 0, 255))
    a = np.asarray(im, np.float32)
    return a[..., :3], a[..., 3:] / 255.0

TXT = [capa_texto(e) for e in escenas]

# ---------- línea de tiempo ----------
inicios, t = [], 0.0
for i, e in enumerate(escenas):
    inicios.append(t); t += e["dur"] - (FADE if i < len(escenas) - 1 else 0)
TOTAL = t

def cuadro_escena(i, tl):
    e = escenas[i]; u = ease(tl / e["dur"])
    a, b = e["de"], e["a"]
    cx = a[0] + (b[0] - a[0]) * u; cy = a[1] + (b[1] - a[1]) * u; z = a[2] + (b[2] - a[2]) * u
    z *= 1 + e.get("respira", 0) * math.sin(tl * 2 * math.pi / 3.2)
    dx = dy = 0
    if e.get("tiembla"):
        dx = e["tiembla"] * math.sin(tl * 23); dy = e["tiembla"] * math.cos(tl * 19)
    src = deforma(np.asarray(base(e["img"])), e.get("mueve"), tl)
    ih, iw = src.shape[:2]; vw, vh = iw / z, ih / z
    x0 = min(max(cx * iw - vw / 2 + dx, 0), iw - vw); y0 = min(max(cy * ih - vh / 2 + dy, 0), ih - vh)
    M = np.float32([[W / vw, 0, -x0 * W / vw], [0, H / vh, -y0 * H / vh]])
    fr = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_CUBIC).astype(np.float32)
    if e.get("rayos", 0):
        fr = 255 - (255 - fr) * (1 - RAYOS * e["rayos"] * (0.75 + 0.25 * math.sin(tl * 1.3)))
    fr = particulas(fr, tl + i * 7, e.get("chispas", 0.0))
    # texto con entrada suave
    rgb, al = TXT[i]
    ti = e.get("texto_desde", 0.5)
    k = ease((tl - ti) / 0.6) * (1 - ease((tl - (e["dur"] - FADE - 0.1)) / 0.5) if i < len(escenas) - 1 else 1)
    if k > 0:
        fr = fr * (1 - al * k) + rgb * al * k
    return fr

pipe = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                         "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
n = int(TOTAL * FPS)
for f in range(n):
    t = f / FPS
    i = max(j for j in range(len(escenas)) if inicios[j] <= t)
    fr = cuadro_escena(i, t - inicios[i])
    if i + 1 < len(escenas) and t >= inicios[i + 1] - 0 and False: pass
    # mezcla con la escena anterior durante la transición
    if i > 0 and t - inicios[i] < FADE:
        m = ease((t - inicios[i]) / FADE)
        prev = cuadro_escena(i - 1, t - inicios[i - 1])
        fr = prev * (1 - m) + fr * m
    # entrada y salida a negro
    g = min(ease(t / 0.6), ease((TOTAL - t) / 0.8))
    fr = fr * VIGN * g
    pipe.stdin.write(np.clip(fr, 0, 255).astype(np.uint8).tobytes())
    if f % 150 == 0: print(f"{f}/{n}", flush=True)
pipe.stdin.close(); pipe.wait()
print("listo", round(TOTAL, 1), "s")
