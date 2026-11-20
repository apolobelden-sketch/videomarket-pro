# Ediciones Guizar - lote de clips con IA (Wan 2.2 TI2V-5B) en Kaggle, gratis (T4). Video promo Fabulas.
import os, subprocess, sys, time, traceback, gc
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
LOG = open("/kaggle/working/log.txt", "w")
def log(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(s, flush=True); LOG.write(s + "\n"); LOG.flush()
BASE = "https://pnjglzuxsyahxcbgjwvq.supabase.co/storage/v1/object/public/archivos/libros/promo-fabulas/"
ESTILO = ", smooth natural character animation, expressive, Pixar style 3D children's movie, warm light"
CLIPS = [
 ("tortuga", "02-tortuga-meta.jpg", 0.5, "A cute cartoon turtle jumps with joy crossing the finish line, waving both arms and cheering, the forest animals behind clap and bounce happily, colorful confetti falls"),
 ("leon", "03-leon-raton.jpg", 0.55, "A big friendly cartoon lion laughs warmly and nods, the tiny grey mouse sitting on his paw waves and smiles at him, sun rays shimmer, leaves sway in the breeze"),
 ("nina", "04-nina-lee.jpg", 0.62, "A little girl reads a storybook, turns the page and smiles with wonder, magical golden sparkles float up from the book, the small toy animals beside her nod and wiggle"),
 ("zorra", "05-zorra.jpg", 0.42, "A clever cartoon fox tilts its head curiously, blinks, and raises its paw as if asking a question, the question mark bounces, grapes sway, autumn leaves drift down"),
 ("colorear", "06-colorear.jpg", 0.5, "Children's hands color the turtle drawing with crayons, moving back and forth filling it with green color, top view, gentle movement"),
 ("hormiga", "07-hormiga-cigarra.jpg", 0.5, "A cute cartoon ant and a cute cicada lift a shining golden star trophy together and dance happily, sparkles shine around the trophy"),
 ("familia", "08-familia.jpg", 0.55, "A happy family laughs together reading a storybook on the sofa, the kids point at the pictures, the parents smile and hug them, cozy living room"),
]
NEG = "static, frozen, blurry, distorted, deformed face, extra limbs, text, letters, watermark, low quality, flicker"
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
        for nombre, _, _, p in CLIPS:
            pe, ne = pt.encode_prompt(prompt=p + ESTILO, negative_prompt=NEG, do_classifier_free_guidance=True, device="cpu")
            emb[nombre] = (pe.to(torch.float16), ne.to(torch.float16))
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
    for nombre, archivo, cx, _ in CLIPS:
        try:
            img = load_image(BASE + archivo).convert("RGB")
            w, h = img.size; cw = int(h * W / H)
            x0 = int(min(max(cx * w - cw / 2, 0), w - cw))
            img = img.crop((x0, 0, x0 + cw, h)).resize((W, H))
            pe, ne = emb[nombre]
            t0 = time.time()
            frames = pipe(image=img, prompt_embeds=pe.to("cuda:0"), negative_prompt_embeds=ne.to("cuda:0"), height=H, width=W,
                          num_frames=81, guidance_scale=5.0, num_inference_steps=30).frames[0]
            export_to_video(frames, f"/kaggle/working/clip-{nombre}.mp4", fps=24)
            log("clip", nombre, "en", round(time.time() - t0), "s")
            torch.cuda.empty_cache()
        except Exception:
            log("ERROR en", nombre, traceback.format_exc()[-1500:])
    log("listo")
except Exception:
    log("ERROR", traceback.format_exc()[-3000:])
