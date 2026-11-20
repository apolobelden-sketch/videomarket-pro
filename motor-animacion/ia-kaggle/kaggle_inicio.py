# Ediciones Guizar - clips encadenados con IA (Wan 2.2 TI2V-5B) para los primeros 15 s del video de Fabulas.
# Cada escena = 2 clips seguidos: el segundo empieza en el ultimo cuadro del primero (sin ida y vuelta).
import os, subprocess, sys, time, traceback, gc
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
LOG = open("/kaggle/working/log.txt", "w")
def log(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(s, flush=True); LOG.write(s + "\n"); LOG.flush()
BASE = "https://pnjglzuxsyahxcbgjwvq.supabase.co/storage/v1/object/public/archivos/libros/promo-fabulas/"
ESTILO = ", smooth natural character animation, expressive, Pixar style 3D children's movie, warm light, steady camera"
ESCENAS = [
 ("carrera", "01-carrera.jpg", 0.5, ["A cute cartoon hare hops forward along a forest path while a cheerful cartoon turtle walks steadily forward beside him, both racing ahead, leaves swaying, butterflies flying",
                                    "The cartoon hare and the cartoon turtle keep racing forward along the sunny forest path, the turtle smiles determined, the hare hops ahead, flowers sway"]),
 ("tortuga", "02b-tortuga-feliz.jpg", 0.5, ["A happy cartoon turtle jumps with joy and raises both arms celebrating, the forest animals around clap and cheer, colorful confetti falls",
                                          "The happy cartoon turtle dances and waves at the camera with a big smile, the forest animals cheer and bounce, confetti keeps falling"]),
]
NEG = "static, frozen, blurry, distorted, deformed face, extra limbs, text, letters, words, banner, sign, watermark, low quality, flicker, walking backwards"
try:
    log("instalando")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "diffusers", "ftfy", "imageio-ffmpeg"], check=True)
    import torch
    from diffusers import WanImageToVideoPipeline, AutoencoderKLWan
    from diffusers.utils import export_to_video, load_image
    MID = "Wan-AI/Wan2.2-TI2V-5B-Diffusers"
    pt = WanImageToVideoPipeline.from_pretrained(MID, transformer=None, vae=None, torch_dtype=torch.bfloat16)
    emb = {}
    with torch.no_grad():
        for nombre, _, _, ps in ESCENAS:
            for j, p in enumerate(ps):
                pe, ne = pt.encode_prompt(prompt=p + ESTILO, negative_prompt=NEG, do_classifier_free_guidance=True, device="cpu")
                emb[(nombre, j)] = (pe.to(torch.float16), ne.to(torch.float16))
    tok = pt.tokenizer
    del pt; gc.collect()
    log("textos listos")
    vae = AutoencoderKLWan.from_pretrained(MID, subfolder="vae", torch_dtype=torch.float32)
    pipe = WanImageToVideoPipeline.from_pretrained(MID, vae=vae, text_encoder=None, tokenizer=tok, torch_dtype=torch.float16)
    pipe.to("cuda:0")
    try: pipe.vae.enable_tiling()
    except Exception as e: log("sin tiling", e)
    log("modelo en gpu")
    W, H = 480, 832
    for nombre, archivo, cx, ps in ESCENAS:
        try:
            img = load_image(BASE + archivo).convert("RGB")
            w, h = img.size; cw = int(h * W / H)
            x0 = int(min(max(cx * w - cw / 2, 0), w - cw))
            img = img.crop((x0, 0, x0 + cw, h)).resize((W, H))
            todos = []
            for j in range(len(ps)):
                pe, ne = emb[(nombre, j)]
                t0 = time.time()
                frames = pipe(image=img, prompt_embeds=pe.to("cuda:0"), negative_prompt_embeds=ne.to("cuda:0"), height=H, width=W,
                              num_frames=81, guidance_scale=5.0, num_inference_steps=30).frames[0]
                todos += list(frames) if j == 0 else list(frames)[1:]
                img = frames[-1]
                if not hasattr(img, "save"):
                    from PIL import Image; import numpy as np
                    img = Image.fromarray((np.asarray(img) * (255 if np.asarray(img).max() <= 1 else 1)).astype("uint8"))
                log("parte", nombre, j, "en", round(time.time() - t0), "s")
                torch.cuda.empty_cache()
            export_to_video(todos, f"/kaggle/working/clip-{nombre}-largo.mp4", fps=24)
            log("clip", nombre, "listo", len(todos), "cuadros")
        except Exception:
            log("ERROR en", nombre, traceback.format_exc()[-1500:])
    log("listo")
except Exception:
    log("ERROR", traceback.format_exc()[-3000:])
