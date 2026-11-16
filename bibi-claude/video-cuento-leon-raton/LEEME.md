# Video del cuento "El león y el ratón" — para Claude

## Qué es

Video de historia animada estilo 3D, hecho por Bibi para Jairo:
- **40 segundos, vertical** (720×1280 en esta copia)
- 4 escenas animadas con el mismo león y el mismo ratoncito
- Narración en español, **SIN música** (Jairo le pone su propia canción directamente en Instagram, Facebook y Pinterest)

## Archivo

El video va en base64, partido en 4 partes (por el canal solo se pueden subir archivos de texto y cada envío tiene un tamaño límite):
- `cuento-leon-raton-sin-musica.mp4.b64.00`, `.01`, `.02` y `.03`
- Para armarlo: `cat cuento-leon-raton-sin-musica.mp4.b64.00 cuento-leon-raton-sin-musica.mp4.b64.01 cuento-leon-raton-sin-musica.mp4.b64.02 cuento-leon-raton-sin-musica.mp4.b64.03 > cuento-leon-raton-sin-musica.mp4.b64`
- Luego: `base64 -d cuento-leon-raton-sin-musica.mp4.b64 > cuento-leon-raton-sin-musica.mp4`
- Verificado: al armar las 4 partes y decodificar, queda idéntico al original (sha256 comprobado)
- Esta copia es 720×1280 (6.7 MB) para que pase por el canal; el original en 1080×1920 (32 MB) lo tiene Bibi

## Lo que pide Jairo

Que Claude lo revise y le arregle lo que vea que necesita arreglo. Sobre todo:
- **Que no lleve ninguna marca de agua ni marca de ninguna aplicación.** Jairo no quiere que sus videos salgan con marcas.
- Bibi revisó el video cuadro por cuadro y no vio ninguna marca, y quitó hasta los datos internos del archivo (no trae ni el dato del programa que lo hizo). Aun así, que Claude lo revise con sus ojos y si ve algo, lo quite.
- No ponerle música: Jairo la pone él en cada app.
