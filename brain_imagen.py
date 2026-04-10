#!/usr/bin/env python3
import os, requests

def crear_con_imagen(nombre, producto):
    print(f"🧠 Creando landing con imagen: {nombre}")
    
    # Generar imagen con Pollinations (gratis)
    imagen_url = f"https://image.pollinations.ai/prompt/samsung%20galaxy%20s23%20smartphone%20product%20photo%20white%20background%20professional?width=600&height=400&nologo=true"
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{producto}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: #333; color: white; padding: 20px; text-align: center; }}
        .imagen {{ width: 100%; height: auto; display: block; }}
        .contenido {{ padding: 20px; }}
        .descripcion {{ font-size: 16px; line-height: 1.6; color: #333; margin-bottom: 20px; }}
        .boton {{ display: block; width: 100%; padding: 15px; background: #3483fa; color: white; text-align: center; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 18px; }}
        .boton:hover {{ background: #2968c8; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{producto}</h1>
        </div>
        <img src="{imagen_url}" alt="{producto}" class="imagen">
        <div class="contenido">
            <p class="descripcion">El {producto} es un teléfono inteligente de última generación con pantalla AMOLED de 6.2 pulgadas, procesador octa-core, 12 GB de RAM y cámara principal de 50 MP. Disponible para entrega inmediata.</p>
            <a href="https://meli.la/11mpFrD" class="boton">🔥 Comprar en Mercado Libre</a>
        </div>
    </div>
</body>
</html>"""
    
    with open(f"output/{nombre}.html", 'w') as f:
        f.write(html)
    
    print(f"✅ output/{nombre}.html con imagen generada por IA")

if __name__ == "__main__":
    crear_con_imagen("landing-celular-con-foto", "Samsung Galaxy S23")
