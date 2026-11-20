#!/usr/bin/env python3
"""Video promo "Fábulas para leer y escuchar" con clips animados por IA (Wan 2.2 en Kaggle).
Sin acercamientos ni deformación propios: solo la animación de la IA, cortes suaves, textos y narración.
Uso (desde esta carpeta): python3 armar_ia.py salida.mp4"""
import sys, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, FADE = 1080, 1920, 30, 0.5
CLIPS = "../ia-kaggle/lote2/"
F_TXT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
F_TIT = "/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf"
# inicios sincronizados con narracion.wav (de armar.py)
INI = [0.0, 5.9, 11.9, 21.9, 27.3, 38.5, 42.9, 46.7, 50.5, 54.6, 58.2, 66.6]
FIN = 74.6
ESC = [
    dict(clip="carrera", titulo=["FÁBULAS", "PARA LEER", "Y ESCUCHAR"]),
    dict(clip="tortuga", texto="¡Despacito y sin rendirme!", y=1650, hasta=1.25),
    dict(pagina="portada.jpg"),
    dict(clip="leon", texto="Nadie es tan pequeño que no pueda ayudar", y=1650),
    dict(clip="nina", texto="Escanea el QR: cada palabra se ilumina", y=1650),
    dict(clip="zorra", texto="¡Preguntas para ver si pusiste atención!", y=1650),
    dict(clip="colorear", texto="Dibujos para colorear", y=330),
    dict(pagina="preguntas.jpg", texto="Moraleja, preguntas y palabras nuevas", y=1760),
    dict(pagina="sopa.jpg", texto="Sopa de letras y diploma de Gran Lector", y=1760),
    dict(clip="hormiga", texto="¡Junta las 10 estampas y gana tu diploma!", y=1650),
    dict(clip="familia", texto="Niños felices, papás orgullosos", y=1690),
    dict(pagina="portada.jpg", titulo=["$59 MXN"], y_titulo=1180, texto="PDF + 10 audios. Link en el perfil", y=1480, color=(255, 226, 120)),
]

def leer_clip(nombre):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", CLIPS + f"clip-{nombre}.mp4", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True, check=True).stdout
    w, h = 480, 832
    return np.frombuffer(p, np.uint8).reshape(-1, h, w, 3)

def a_pantalla(fr):  # escala fija a lo alto de la pantalla y recorta el sobrante lateral (sin movimiento)
    h, w = fr.shape[:2]; s = H / h; nw = round(w * s)
    big = cv2.resize(fr, (nw, H), interpolation=cv2.INTER_LANCZOS4)
    x0 = (nw - W) // 2
    return big[:, x0:x0 + W].astype(np.float32)

def pagina(archivo):  # página del libro completa, fija, sobre su propio fondo desenfocado
    im = Image.open(archivo).convert("RGB")
    fondo = im.resize((W, H)).filter(ImageFilter.GaussianBlur(40))
    fondo = Image.blend(fondo, Image.new("RGB", (W, H), (30, 20, 10)), 0.35)
    s = W / im.width; pg = im.resize((W, round(im.height * s)), Image.LANCZOS)
    fondo.paste(pg, (0, (H - pg.height) // 2))
    return np.asarray(fondo, np.float32)

def capa(e):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if e.get("titulo"):
        f = ImageFont.truetype(F_TIT, 132); y = e.get("y_titulo", 260)
        for l in e["titulo"]:
            w = d.textlength(l, font=f)
            d.text(((W - w) / 2 + 6, y + 8), l, font=f, fill=(60, 25, 0, 150))
            d.text(((W - w) / 2, y), l, font=f, fill=(255, 214, 92, 255), stroke_width=7, stroke_fill=(90, 40, 5, 255)); y += 160
    if e.get("texto"):
        f = ImageFont.truetype(F_TXT, 60); pal, lin, act = e["texto"].replace("\n", " ").split(), [], ""
        for p in pal:
            pr = (act + " " + p).strip()
            if d.textlength(pr, font=f) > W - 150: lin.append(act); act = p
            else: act = pr
        lin.append(act)
        if "\n" in e["texto"]: lin = e["texto"].split("\n")
        lh = 80; alto = lh * len(lin); y = e["y"] - alto // 2
        caja = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(caja).rounded_rectangle((45, y - 40, W - 45, y + alto + 30), 46, fill=(25, 12, 0, 150))
        im = Image.alpha_composite(caja.filter(ImageFilter.GaussianBlur(5)), im); d = ImageDraw.Draw(im)
        for i, l in enumerate(lin):
            w = d.textlength(l, font=f)
            d.text(((W - w) / 2, y + i * lh), l, font=f, fill=e.get("color", (255, 248, 230)) + (255,), stroke_width=4, stroke_fill=(40, 18, 0, 255))
    a = np.asarray(im, np.float32); return a[..., :3], a[..., 3:] / 255.0

clips = {e["clip"]: leer_clip(e["clip"]) for e in ESC if "clip" in e}
paginas = {e["pagina"]: pagina(e["pagina"]) for e in ESC if "pagina" in e}
capas = [capa(e) for e in ESC]

def cuadro(i, tl):
    e = ESC[i]
    if "pagina" in e: fr = paginas[e["pagina"]].copy()
    else:
        fs = clips[e["clip"]]; fs = fs[:int(e.get("hasta", 99) * 24)] if e.get("hasta") else fs; D = len(fs) / 24.0
        dur = (INI[i + 1] if i + 1 < len(INI) else FIN) - INI[i]
        f = min(max(dur / D, 1.0), 1.6)  # cámara lenta suave, máximo 1.6x
        tt = tl / f; m = tt % (2 * D); pos = m if m < D else 2 * D - m  # ida y vuelta si aún falta tiempo
        fr = a_pantalla(fs[min(int(pos * 24), len(fs) - 1)])
    rgb, al = capas[i]
    k = min(1.0, max(0.0, (tl - 0.3) / 0.5))
    return fr * (1 - al * k) + rgb * al * k

out = sys.argv[1]
pipe = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                         "-i", "narracion.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
n = int(FIN * FPS)
for k in range(n):
    t = k / FPS
    i = max(j for j in range(len(INI)) if INI[j] <= t)
    fr = cuadro(i, t - INI[i])
    if i > 0 and t - INI[i] < FADE:
        m = (t - INI[i]) / FADE; m = m * m * (3 - 2 * m)
        fr = cuadro(i - 1, t - INI[i - 1]) * (1 - m) + fr * m
    g = min(1.0, t / 0.5, (FIN - t) / 0.8)
    pipe.stdin.write(np.clip(fr * g, 0, 255).astype(np.uint8).tobytes())
pipe.stdin.close(); pipe.wait(); print("listo", FIN)
