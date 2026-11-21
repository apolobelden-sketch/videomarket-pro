# Ediciones Guizar - "El leon y el raton" animado con IA (Wan 2.2 TI2V-5B) en Kaggle, gratis.
# Version rapida: las DOS tarjetas T4 trabajan al mismo tiempo (cada una su mitad de escenas, en hilos) y 25 pasos en vez de 30.
# Cada escena = 2 clips encadenados (el segundo arranca en el ultimo cuadro del primero): ~6.7 s sin ida y vuelta.
import os, subprocess, sys, time, traceback, gc, json
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
OUT = "/kaggle/working/"
BASE = "https://pnjglzuxsyahxcbgjwvq.supabase.co/storage/v1/object/public/archivos/libros/leon-raton-ia/"
ESTILO = ", smooth natural character animation, expressive, Pixar style 3D children's movie, warm light, steady camera"
NEG = "static, frozen, blurry, distorted, deformed face, extra limbs, text, letters, words, watermark, low quality, flicker, morphing, walking backwards"
ESCENAS = [
 ("e1", ["The big lion sleeps peacefully under the tree, his chest rises and falls as he breathes, his tail swishes slowly, leaves sway in a gentle breeze",
         "The lion keeps sleeping calmly, his ears twitch, he smiles in his sleep, a butterfly flies around, grass sways"]),
 ("e2", ["The tiny mouse runs quickly across the lion's nose, the lion opens his eyes wide in surprise and lifts his head",
         "The lion blinks and looks at the little mouse with surprise, the mouse freezes and looks back nervously, whiskers move"]),
 ("e3", ["The little mouse pleads with joined hands and trembles under the lion's paw, the lion looks at him closely and blinks",
         "The mouse keeps begging and nodding, the lion tilts his head, thinking, his mane moves in the breeze"]),
 ("e4", ["The lion laughs heartily shaking his mane and lifts his big paw, the little mouse runs free and waves goodbye happily",
         "The lion keeps laughing and smiling kindly, the little mouse turns and waves again, sunlight shimmers"]),
 ("e5", ["The lion struggles inside the rope net, pulling and twisting and roaring, the net swings from the tree branch",
         "The trapped lion roars sadly and pushes against the ropes, the net keeps swinging, dusk light"]),
 ("e6", ["The little mouse gnaws the thick rope quickly with his teeth, the rope strands snap one by one, the lion watches hopefully",
         "The mouse keeps biting the rope, the net loosens and opens, the lion smiles with relief"]),
 ("e7", ["The lion and the little mouse laugh together as best friends, the mouse waves from the top of the lion's head, the lion nods happily, sunset light",
         "The lion and the mouse keep smiling, the mouse dances on the lion's head, the lion closes his eyes happily, warm golden sunset"]),
]
W, H, CUADROS, PASOS = 480, 832, 81, 25

def logf(nombre):
    f = open(OUT + nombre, "a")
    def log(*a):
        s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
        print(s, flush=True); f.write(s + "\n"); f.flush()
    return log

def cargar(dev, tok):
    import torch
    from diffusers import WanImageToVideoPipeline, AutoencoderKLWan
    MID = "Wan-AI/Wan2.2-TI2V-5B-Diffusers"
    vae = AutoencoderKLWan.from_pretrained(MID, subfolder="vae", torch_dtype=torch.float32)
    pipe = WanImageToVideoPipeline.from_pretrained(MID, vae=vae, text_encoder=None, tokenizer=tok, torch_dtype=torch.float16)
    pipe.to(dev)
    try: pipe.vae.enable_tiling()
    except Exception: pass
    return pipe

def trabajador(gpu, pipe, emb, nombres):
    log = logf(f"log-gpu{gpu}.txt")
    import torch, numpy as np
    from diffusers.utils import export_to_video, load_image
    from PIL import Image
    dev = f"cuda:{gpu}"
    for nombre in nombres:
        try:
            img = load_image(BASE + nombre + ".jpg").convert("RGB")
            w, h = img.size; cw = int(h * W / H)
            x0 = int(max((w - cw) / 2, 0))
            img = img.crop((x0, 0, x0 + cw, h)).resize((W, H), Image.LANCZOS)
            todos = []
            for j in range(2):
                pe, ne = emb[f"{nombre}-{j}"]
                t0 = time.time()
                with torch.cuda.device(gpu):
                    frames = pipe(image=img, prompt_embeds=pe.to(dev), negative_prompt_embeds=ne.to(dev), height=H, width=W,
                                  num_frames=CUADROS, guidance_scale=5.0, num_inference_steps=PASOS).frames[0]
                frames = list(frames)
                todos += frames if j == 0 else frames[1:]
                ult = frames[-1]
                if hasattr(ult, "save"): img = ult
                else:
                    a = np.asarray(ult); a = a * 255 if a.max() <= 1.0 else a
                    img = Image.fromarray(np.clip(a, 0, 255).astype("uint8"))
                log("parte", nombre, j, "en", round(time.time() - t0), "s")
                with torch.cuda.device(gpu): torch.cuda.empty_cache()
            export_to_video(todos, OUT + f"clip-{nombre}.mp4", fps=24)
            log("clip", nombre, "listo", len(todos), "cuadros")
        except Exception:
            log("ERROR en", nombre, traceback.format_exc()[-1500:])
    log("fin gpu", gpu)

log = logf("log.txt")
try:
    t_ini = time.time()
    log("instalando")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "diffusers", "ftfy", "imageio-ffmpeg"], check=True)
    import torch
    from diffusers import WanImageToVideoPipeline
    MID = "Wan-AI/Wan2.2-TI2V-5B-Diffusers"
    pt = WanImageToVideoPipeline.from_pretrained(MID, transformer=None, vae=None, torch_dtype=torch.bfloat16)
    # El texto se procesa en la tarjeta 0 (mas rapido que en CPU) y luego se libera
    dev_txt = "cuda:0" if torch.cuda.get_device_capability(0)[0] >= 7 else "cpu"   # P100 no maneja bf16: el texto va en CPU
    pt.text_encoder.to(dev_txt)
    log("gpu", torch.cuda.get_device_name(0), "x", torch.cuda.device_count(), "texto en", dev_txt)
    emb = {}
    with torch.no_grad():
        for nombre, ps in ESCENAS:
            for j, p in enumerate(ps):
                pe, ne = pt.encode_prompt(prompt=p + ESTILO, negative_prompt=NEG, do_classifier_free_guidance=True, device=dev_txt)
                emb[f"{nombre}-{j}"] = (pe.to("cpu", torch.float16), ne.to("cpu", torch.float16))
    tok = pt.tokenizer
    del pt; gc.collect(); torch.cuda.empty_cache()
    log("textos listos en", round(time.time() - t_ini), "s")
    import threading
    pipes = []
    for g in range(min(2, torch.cuda.device_count())):
        pipes.append(cargar(f"cuda:{g}", tok)); gc.collect()
        log("modelo en gpu", g, round(torch.cuda.memory_allocated(g) / 1e9, 1), "GB")
    nombres = [e[0] for e in ESCENAS]
    grupos = [nombres[0::2], nombres[1::2]] if len(pipes) == 2 else [nombres]
    hilos = [threading.Thread(target=trabajador, args=(g, pipes[g], emb, grupos[g])) for g in range(len(pipes))]
    for h in hilos: h.start()
    for h in hilos: h.join()
    log("todo listo en", round((time.time() - t_ini) / 60), "min")
except Exception:
    log("ERROR", traceback.format_exc()[-3000:])
