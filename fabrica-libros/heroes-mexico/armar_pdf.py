# Fábrica de Libros · Ediciones Guizar — arma el PDF "Héroes de México: lee, escribe y cuenta"
# Corre en Kaggle (sin GPU). Baja dibujos y fuentes, arma el libro (carta), una muestra y una hoja de revisión.
import os, sys, subprocess, urllib.request, random, base64, io
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "reportlab", "pymupdf"])
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.utils import ImageReader
os.chdir("/kaggle/working")
# Contenido del libro "Héroes de México: lee, escribe y cuenta" (Ediciones Guizar)
# Cada personaje: bio (lectura), dato, preguntas (comprensión), escritura, mates (problema, respuesta), año para la línea del tiempo.
LIBRO = {
 "titulo": "Héroes de México",
 "subtitulo": "Lee, escribe y cuenta con 10 grandes personajes",
 "grado": "2.º a 4.º de primaria",
}
P = [
 {"slug": "nezahualcoyotl", "nombre": "Nezahualcóyotl", "apodo": "El rey poeta", "anios": "1402 - 1472", "linea": (1402, "Nace Nezahualcóyotl, el rey poeta"),
  "bio": "Nezahualcóyotl nació en 1402 en Texcoco, una gran ciudad junto a un lago. Su nombre en náhuatl quiere decir «coyote que ayuna». De joven tuvo que esconderse de sus enemigos, pero nunca se rindió. Cuando fue rey, construyó obras para llevar agua a su pueblo y un gran dique para proteger la ciudad de las inundaciones. Le encantaba la naturaleza y escribía poemas sobre las flores, los cantos y la amistad. Por eso lo recordamos como el rey poeta.",
  "dato": "El náhuatl, la lengua de Nezahualcóyotl, todavía se habla en México. Palabras como chocolate, tomate y aguacate vienen del náhuatl.",
  "preguntas": [("¿Qué quiere decir su nombre?", ["Águila que vuela", "Coyote que ayuna", "Sol que brilla"], 1),
                ("¿Sobre qué escribía sus poemas?", ["Las flores, los cantos y la amistad", "Los coches", "Los dinosaurios"], 0),
                ("¿Por qué construyó un gran dique?", None, "Para proteger la ciudad de las inundaciones."),
                ("¿Por qué crees que no se rindió?", None, "Respuesta libre.")],
  "escritura": "Escribe tres palabras que vengan del náhuatl: ______________________",
  "escritura_resp": "Por ejemplo: chocolate, tomate, aguacate.",
  "mates": [("Nezahualcóyotl nació en 1402 y murió en 1472. ¿Cuántos años vivió?", "1472 − 1402 = 70 años"),
            ("Si escribió 6 poemas y cada uno tiene 4 versos, ¿cuántos versos son en total?", "6 × 4 = 24 versos"),
            ("¿Cuántos años han pasado desde que nació hasta 2026?", "2026 − 1402 = 624 años")]},
 {"slug": "sor-juana", "nombre": "Sor Juana Inés de la Cruz", "apodo": "La gran escritora", "anios": "1648 (o 1651) - 1695", "linea": (1695, "Muere Sor Juana, gran escritora"),
  "bio": "Juana Inés nació en San Miguel Nepantla, en el Estado de México. Ella misma contó que aprendió a leer a los tres años. Quería tanto estudiar que pidió ir a la universidad vestida de hombre, porque en esa época las mujeres no podían entrar. Más tarde se hizo monja y su celda se llenó de libros. Escribió poemas, canciones y obras de teatro que todavía se leen. Murió en 1695 por cuidar a otras monjas enfermas durante una epidemia.",
  "dato": "Sor Juana también estudiaba música, matemáticas y astronomía. ¡Le gustaba aprender de todo!",
  "preguntas": [("¿A qué edad aprendió a leer?", ["A los tres años", "A los diez años", "A los veinte años"], 0),
                ("¿Por qué quería ir vestida de hombre a la universidad?", ["Para jugar", "Porque las mujeres no podían entrar", "Porque hacía frío"], 1),
                ("¿Qué cosas escribió?", None, "Poemas, canciones y obras de teatro."),
                ("¿Qué te gustaría aprender a ti como Sor Juana?", None, "Respuesta libre.")],
  "escritura": "Copia en tu mejor letra: «Aprender es la mejor aventura».",
  "escritura_resp": "Copia con buena letra.",
  "mates": [("Sor Juana murió en 1695. ¿Cuántos años han pasado hasta 2026?", "2026 − 1695 = 331 años"),
            ("Si leía 2 libros cada semana, ¿cuántos libros leía en 4 semanas?", "2 × 4 = 8 libros"),
            ("En un estante hay 45 libros y en otro 38. ¿Cuántos libros hay en total?", "45 + 38 = 83 libros")]},
 {"slug": "hidalgo", "nombre": "Miguel Hidalgo y Costilla", "apodo": "El Padre de la Patria", "anios": "1753 - 1811", "linea": (1810, "Grito de Dolores: inicia la Independencia"),
  "bio": "Miguel Hidalgo era el cura del pueblo de Dolores, en Guanajuato. Enseñaba a la gente a hacer trabajos de alfarería, a cuidar abejas y a criar gusanos de seda para que pudieran ganarse la vida. En la madrugada del 16 de septiembre de 1810 tocó la campana de la iglesia y llamó al pueblo a luchar para que México fuera libre. Así comenzó la Guerra de Independencia. Por eso lo llamamos el Padre de la Patria.",
  "dato": "Cada 15 de septiembre por la noche recordamos el Grito de Dolores con el grito de «¡Viva México!».",
  "preguntas": [("¿En qué pueblo era cura?", ["Dolores", "Texcoco", "Oaxaca"], 0),
                ("¿Qué día comenzó la Independencia?", ["20 de noviembre de 1910", "16 de septiembre de 1810", "21 de marzo de 1806"], 1),
                ("¿Qué oficios enseñaba Hidalgo?", None, "Alfarería, cuidar abejas y criar gusanos de seda."),
                ("¿Por qué crees que tocó la campana?", None, "Para reunir al pueblo y llamarlo a luchar por la libertad.")],
  "escritura": "Ordena las palabras y escribe la oración: libre — México — quería — Hidalgo — fuera — que",
  "escritura_resp": "Hidalgo quería que México fuera libre.",
  "mates": [("Hidalgo nació en 1753. ¿Cuántos años tenía en 1810?", "1810 − 1753 = 57 años"),
            ("¿Cuántos años han pasado desde 1810 hasta 2026?", "2026 − 1810 = 216 años"),
            ("Si la campana sonó 3 veces cada minuto durante 5 minutos, ¿cuántas veces sonó?", "3 × 5 = 15 veces")]},
 {"slug": "josefa", "nombre": "Josefa Ortiz de Domínguez", "apodo": "La Corregidora", "anios": "(1768) - 1829", "linea": (1810, "Josefa avisa a los insurgentes"),
  "bio": "Josefa Ortiz vivía en Querétaro y estaba casada con el corregidor, una autoridad de la ciudad. En su casa se hacían reuniones secretas para planear la lucha por la independencia. En septiembre de 1810 las autoridades descubrieron el plan y la encerraron en su casa. Aun así, Josefa encontró la manera de enviar un aviso a los insurgentes para que se adelantaran. Gracias a su valentía, la lucha comenzó a tiempo.",
  "dato": "A Josefa Ortiz se le conoce como «La Corregidora» por el cargo de su esposo.",
  "preguntas": [("¿En qué ciudad vivía Josefa?", ["Querétaro", "Monterrey", "Mérida"], 0),
                ("¿Qué hizo cuando la encerraron?", ["Se durmió", "Envió un aviso a los insurgentes", "Se fue de viaje"], 1),
                ("¿Para qué eran las reuniones secretas?", None, "Para planear la lucha por la independencia."),
                ("¿Qué significa ser valiente? Da un ejemplo.", None, "Respuesta libre.")],
  "escritura": "Escribe un mensaje secreto corto, como el que Josefa envió: ______________________",
  "escritura_resp": "Respuesta libre.",
  "mates": [("La Independencia empezó en 1810 y terminó en 1821. ¿Cuántos años duró?", "1821 − 1810 = 11 años"),
            ("Josefa murió en 1829. ¿Cuántos años después del inicio de la Independencia fue?", "1829 − 1810 = 19 años"),
            ("En una reunión había 12 personas y llegaron 9 más. ¿Cuántas personas había?", "12 + 9 = 21 personas")]},
 {"slug": "morelos", "nombre": "José María Morelos y Pavón", "apodo": "El Siervo de la Nación", "anios": "1765 - 1815", "linea": (1813, "Morelos escribe Sentimientos de la Nación"),
  "bio": "José María Morelos nació en Valladolid, una ciudad que hoy se llama Morelia en su honor. De joven trabajó como arriero, llevando mercancías con mulas por los caminos. Después estudió y fue sacerdote. Cuando empezó la Independencia se unió a Hidalgo y luego dirigió la lucha. En 1813 escribió Sentimientos de la Nación, donde pidió que todas las personas fueran iguales. Siempre usaba un pañuelo amarrado en la cabeza.",
  "dato": "La ciudad de Morelia, en Michoacán, lleva ese nombre para recordar a Morelos.",
  "preguntas": [("¿Cómo se llama hoy la ciudad donde nació?", ["Morelia", "Puebla", "Toluca"], 0),
                ("¿Qué pidió en Sentimientos de la Nación?", ["Más fiestas", "Que todas las personas fueran iguales", "Más caminos"], 1),
                ("¿En qué trabajaba de joven?", None, "Era arriero: llevaba mercancías con mulas."),
                ("¿Por qué es importante que todos seamos iguales?", None, "Respuesta libre.")],
  "escritura": "Completa: Morelos usaba un __________ amarrado en la __________.",
  "escritura_resp": "pañuelo / cabeza",
  "mates": [("Morelos nació en 1765. ¿Cuántos años tenía en 1813?", "1813 − 1765 = 48 años"),
            ("Si un arriero llevaba 4 mulas y cada mula cargaba 3 costales, ¿cuántos costales eran?", "4 × 3 = 12 costales"),
            ("Morelos vivió de 1765 a 1815. ¿Cuántos años vivió?", "1815 − 1765 = 50 años")]},
 {"slug": "leona", "nombre": "Leona Vicario", "apodo": "Madre de la Patria", "anios": "1789 - 1842", "linea": (1789, "Nace Leona Vicario"),
  "bio": "Leona Vicario nació en la Ciudad de México en 1789. Le encantaba leer y estudiar. Durante la Guerra de Independencia usó su propio dinero para ayudar a los insurgentes y les enviaba mensajes secretos escritos en clave. Un día la descubrieron y la encerraron, pero logró escapar y siguió ayudando. También escribía en periódicos para defender sus ideas, por eso se le considera una de las primeras periodistas de México.",
  "dato": "Un mensaje en clave es un mensaje escrito de una forma especial para que solo lo entienda quien conoce el secreto.",
  "preguntas": [("¿En qué ciudad nació Leona?", ["Ciudad de México", "Tijuana", "Cancún"], 0),
                ("¿Cómo ayudaba a los insurgentes?", ["Con dinero y mensajes secretos", "Cantando", "Pintando casas"], 0),
                ("¿Qué pasó cuando la descubrieron?", None, "La encerraron, pero logró escapar."),
                ("¿Por qué se le considera periodista?", None, "Porque escribía en periódicos para defender sus ideas.")],
  "escritura": "Descifra la clave (cada número es una letra: 1=A, 2=E, 3=I, 4=O, 5=U): L2 4 N 1",
  "escritura_resp": "LEONA",
  "mates": [("Leona vivió de 1789 a 1842. ¿Cuántos años vivió?", "1842 − 1789 = 53 años"),
            ("Si escribió 5 mensajes cada semana, ¿cuántos escribió en 6 semanas?", "5 × 6 = 30 mensajes"),
            ("Tenía 100 monedas y dio 64 a los insurgentes. ¿Cuántas le quedaron?", "100 − 64 = 36 monedas")]},
 {"slug": "juarez", "nombre": "Benito Juárez", "apodo": "El Benemérito de las Américas", "anios": "1806 - 1872", "linea": (1806, "Nace Benito Juárez en Oaxaca"),
  "bio": "Benito Juárez nació el 21 de marzo de 1806 en San Pablo Guelatao, Oaxaca. Era zapoteco y de niño hablaba zapoteco. Quedó huérfano muy pequeño y cuidaba ovejas en el campo. A los doce años se fue caminando a la ciudad de Oaxaca para estudiar. Allí aprendió español, estudió mucho y llegó a ser abogado, gobernador y presidente de México. Defendió las leyes y la igualdad de todas las personas.",
  "dato": "Juárez dijo: «Entre los individuos, como entre las naciones, el respeto al derecho ajeno es la paz».",
  "preguntas": [("¿Qué lengua hablaba Benito de niño?", ["Inglés", "Zapoteco", "Francés"], 1),
                ("¿Qué hacía en el campo cuando era niño?", ["Cuidaba ovejas", "Manejaba un tractor", "Vendía helados"], 0),
                ("¿A qué edad se fue a la ciudad para estudiar?", None, "A los doce años."),
                ("¿Qué significa para ti «respetar el derecho ajeno»?", None, "Respuesta libre.")],
  "escritura": "Escribe dos oraciones sobre lo que tú quieres lograr cuando seas grande.",
  "escritura_resp": "Respuesta libre.",
  "mates": [("Juárez vivió de 1806 a 1872. ¿Cuántos años vivió?", "1872 − 1806 = 66 años"),
            ("Imagina que cuidaba 18 ovejas y nacieron 7 más. ¿Cuántas ovejas eran?", "18 + 7 = 25 ovejas"),
            ("Imagina que caminaba 15 kilómetros cada día. ¿Cuántos kilómetros caminaba en 4 días?", "15 × 4 = 60 kilómetros")]},
 {"slug": "matilde", "nombre": "Matilde Montoya", "apodo": "La primera médica de México", "anios": "1859 - 1938", "linea": (1887, "Matilde Montoya, primera médica de México"),
  "bio": "Matilde Montoya nació en la Ciudad de México en 1859. Desde niña le gustaba mucho estudiar. Quería ser doctora, pero en esa época casi nadie aceptaba que una mujer estudiara medicina. Algunas personas se burlaban de ella y le pusieron muchos obstáculos, pero Matilde siguió adelante. En 1887 presentó su examen y se convirtió en la primera mujer médica de México. Abrió el camino para que muchas niñas pudieran estudiar lo que soñaban.",
  "dato": "Hoy, en México, hay miles de mujeres médicas gracias a pioneras como Matilde.",
  "preguntas": [("¿Qué quería ser Matilde?", ["Doctora", "Piloto", "Cocinera"], 0),
                ("¿En qué año se convirtió en médica?", ["1810", "1887", "1910"], 1),
                ("¿Qué hacían algunas personas para desanimarla?", None, "Se burlaban de ella y le ponían obstáculos."),
                ("¿Qué harías tú si alguien se burlara de tus sueños?", None, "Respuesta libre.")],
  "escritura": "Escribe tres palabras relacionadas con la medicina: ______________________",
  "escritura_resp": "Por ejemplo: doctora, hospital, medicina.",
  "mates": [("Matilde nació en 1859 y se tituló en 1887. ¿Cuántos años tenía?", "1887 − 1859 = 28 años"),
            ("Si atendía a 8 pacientes al día, ¿cuántos atendía en 5 días?", "8 × 5 = 40 pacientes"),
            ("Un frasco tenía 50 pastillas y usó 18. ¿Cuántas quedaron?", "50 − 18 = 32 pastillas")]},
 {"slug": "zapata", "nombre": "Emiliano Zapata", "apodo": "El Caudillo del Sur", "anios": "1879 - 1919", "linea": (1910, "Comienza la Revolución Mexicana"),
  "bio": "Emiliano Zapata nació en 1879 en Anenecuilco, Morelos. Era campesino y un gran jinete. Vio que muchos campesinos trabajaban la tierra, pero no eran dueños de ella. Por eso, cuando comenzó la Revolución Mexicana el 20 de noviembre de 1910, se unió a la lucha. En 1911 presentó el Plan de Ayala para que los campesinos recuperaran sus tierras. Su lema era «Tierra y libertad».",
  "dato": "Cada 20 de noviembre recordamos el inicio de la Revolución Mexicana con desfiles.",
  "preguntas": [("¿En qué estado nació Zapata?", ["Morelos", "Sonora", "Yucatán"], 0),
                ("¿Cuándo comenzó la Revolución Mexicana?", ["16 de septiembre de 1810", "20 de noviembre de 1910", "5 de mayo de 1862"], 1),
                ("¿Qué pedía el Plan de Ayala?", None, "Que los campesinos recuperaran sus tierras."),
                ("¿Por qué crees que la tierra era tan importante para los campesinos?", None, "Respuesta libre.")],
  "escritura": "Escribe el lema de Zapata con letra grande y bonita: ______________________",
  "escritura_resp": "Tierra y libertad.",
  "mates": [("¿Cuántos años han pasado desde 1910 hasta 2026?", "2026 − 1910 = 116 años"),
            ("Zapata nació en 1879. ¿Cuántos años tenía en 1910?", "1910 − 1879 = 31 años"),
            ("Si un campesino sembró 9 surcos con 6 plantas de maíz cada uno, ¿cuántas plantas sembró?", "9 × 6 = 54 plantas")]},
 {"slug": "camarena", "nombre": "Guillermo González Camarena", "apodo": "El inventor de la televisión a color", "anios": "1917 - 1965", "linea": (1940, "González Camarena patenta su televisión a color"),
  "bio": "Guillermo González Camarena nació en Guadalajara, Jalisco, en 1917. Desde niño desarmaba aparatos para ver cómo funcionaban y construía juguetes eléctricos. Muy joven armó su propia cámara de televisión con piezas que conseguía. Después inventó un sistema para ver la televisión a color y lo patentó en 1940. Su invento fue reconocido en otros países. Nos enseña que la curiosidad y la paciencia pueden cambiar el mundo.",
  "dato": "Patentar un invento quiere decir registrarlo para que todos sepan quién lo creó.",
  "preguntas": [("¿En qué ciudad nació Guillermo?", ["Guadalajara", "Puebla", "Oaxaca"], 0),
                ("¿Qué inventó?", ["El teléfono", "Un sistema de televisión a color", "La bicicleta"], 1),
                ("¿Qué hacía cuando era niño?", None, "Desarmaba aparatos y construía juguetes eléctricos."),
                ("Si fueras inventor o inventora, ¿qué inventarías?", None, "Respuesta libre.")],
  "escritura": "Dibuja tu invento en una hoja y escribe aquí cómo se llama y para qué sirve: ______________",
  "escritura_resp": "Respuesta libre.",
  "mates": [("Guillermo nació en 1917 y patentó su invento en 1940. ¿Cuántos años tenía?", "1940 − 1917 = 23 años"),
            ("Si usó 7 tornillos en cada aparato y armó 6 aparatos, ¿cuántos tornillos usó?", "7 × 6 = 42 tornillos"),
            ("Tenía 90 piezas y usó 47. ¿Cuántas le quedaron?", "90 − 47 = 43 piezas")]},
]

IMG = "https://pnjglzuxsyahxcbgjwvq.supabase.co/storage/v1/object/public/archivos/libros/heroes-mexico/"
GF = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
for f, u in [("Poppins-Regular.ttf", GF + "poppins/Poppins-Regular.ttf"), ("Poppins-Bold.ttf", GF + "poppins/Poppins-Bold.ttf"),
             ("Fredoka.ttf", GF + "fredokaone/FredokaOne-Regular.ttf"), ("PatrickHand.ttf", GF + "patrickhand/PatrickHand-Regular.ttf")]:
    try: urllib.request.urlretrieve(u, f)
    except Exception as e: print("fuente", f, e)
def reg(n, f, alt="Helvetica"):
    try: pdfmetrics.registerFont(TTFont(n, f)); return n
    except Exception: return alt
R = reg("Pop", "Poppins-Regular.ttf"); B = reg("PopB", "Poppins-Bold.ttf", "Helvetica-Bold")
T = reg("Fred", "Fredoka.ttf", B); M = reg("Hand", "PatrickHand.ttf", R)
imgs = {}
for p in P + [{"slug": "portada"}]:
    try: imgs[p["slug"]] = ImageReader(io.BytesIO(urllib.request.urlopen(IMG + p["slug"] + ".jpg", timeout=60).read()))
    except Exception as e: print("img", p["slug"], e)

W, H = letter
TINTA = HexColor("#3b2a1a"); ROJO = HexColor("#d62828"); VERDE = HexColor("#1b7a3e"); CREMA = HexColor("#fff8e7")
COLORES = ["#e76f51", "#2a9d8f", "#e9c46a", "#8e44ad", "#1d7874", "#d62828", "#3a86ff", "#ff006e", "#6a994e", "#f77f00"]
st_bio = ParagraphStyle("bio", fontName=R, fontSize=12.5, leading=18.5, textColor=TINTA)
st_peq = ParagraphStyle("peq", fontName=R, fontSize=11, leading=15, textColor=TINTA)
c = canvas.Canvas("heroes-de-mexico.pdf", pagesize=letter)
c.setTitle("Héroes de México: lee, escribe y cuenta"); c.setAuthor("Ediciones Guizar")
pag = [0]

def pie():
    pag[0] += 1
    c.setFont(R, 9); c.setFillColor(HexColor("#9a7b55"))
    c.drawString(40, 24, "Héroes de México · Ediciones Guizar"); c.drawRightString(W - 40, 24, str(pag[0]))

def banda(texto, color, sub=None):
    c.setFillColor(HexColor(color)); c.roundRect(30, H - 92, W - 60, 62, 18, fill=1, stroke=0)
    c.setFillColor(white); c.setFont(T, 26); c.drawString(50, H - 62, texto)
    if sub: c.setFont(R, 12); c.drawString(50, H - 82, sub)

def renglones(x, y, ancho, n, sep=34):
    for k in range(n):
        yy = y - k * sep
        c.setStrokeColor(HexColor("#7d6a55")); c.setLineWidth(0.9); c.line(x, yy, x + ancho, yy)
        c.setStrokeColor(HexColor("#c9b89f")); c.setDash(2, 3); c.line(x, yy + 11, x + ancho, yy + 11); c.setDash()
    return y - n * sep

def parrafo(texto, x, y, ancho, alto, st=st_bio):
    f = Frame(x, y - alto, ancho, alto, showBoundary=0, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    f.addFromList([Paragraph(texto, st)], c)

def texto_envuelto(t, x, y, ancho, fuente, tam, lead):
    palabras, linea = t.split(), ""
    for w in palabras:
        if pdfmetrics.stringWidth((linea + " " + w).strip(), fuente, tam) > ancho:
            c.drawString(x, y, linea); y -= lead; linea = w
        else: linea = (linea + " " + w).strip()
    if linea: c.drawString(x, y, linea); y -= lead
    return y

# ---------- PORTADA ----------
c.setFillColor(CREMA); c.rect(0, 0, W, H, fill=1, stroke=0)
c.setFillColor(HexColor("#006847")); c.rect(0, H - 30, W / 3, 30, fill=1, stroke=0)
c.setFillColor(white); c.rect(W / 3, H - 30, W / 3, 30, fill=1, stroke=0)
c.setFillColor(HexColor("#ce1126")); c.rect(2 * W / 3, H - 30, W / 3, 30, fill=1, stroke=0)
c.setFillColor(ROJO); c.setFont(T, 54); c.drawCentredString(W / 2, H - 110, "Héroes de México")
c.setFillColor(TINTA); c.setFont(B, 20); c.drawCentredString(W / 2, H - 145, "Lee, escribe y cuenta con 10 grandes personajes")
if "portada" in imgs: c.drawImage(imgs["portada"], (W - 420) / 2, 215, 420, 420, mask="auto")
c.setFillColor(HexColor("#2a9d8f")); c.roundRect(W / 2 - 235, 150, 470, 44, 22, fill=1, stroke=0)
c.setFillColor(white); c.setFont(B, 15); c.drawCentredString(W / 2, 166, "Biografías · Lectura · Escritura · Matemáticas")
c.setFillColor(TINTA); c.setFont(R, 14); c.drawCentredString(W / 2, 115, "Para niñas y niños de 2.º a 4.º de primaria")
c.setFont(B, 13); c.setFillColor(HexColor("#9a7b55")); c.drawCentredString(W / 2, 60, "Ediciones Guizar")
c.showPage(); pag[0] += 1

# ---------- PRESENTACIÓN ----------
banda("¡Bienvenidos, pequeños historiadores!", "#2a9d8f")
pres = ("En este libro conocerás a <b>10 personajes</b> que ayudaron a construir México: poetas, maestras, inventores, "
        "luchadores por la libertad y pioneras que no se rindieron. Con cada uno vas a <b>leer</b> su historia, <b>colorear</b> "
        "su dibujo, <b>responder</b> preguntas, <b>escribir</b> y resolver <b>problemas de matemáticas</b> con fechas y datos reales.")
parrafo(pres, 50, H - 120, W - 100, 120)
c.setFillColor(TINTA); c.setFont(B, 15); c.drawString(50, H - 255, "Cómo usar este libro")
pasos = ["1. Lee la historia del personaje (puedes leerla en voz alta con un adulto).",
         "2. Colorea su dibujo como más te guste.",
         "3. Responde las preguntas de «Lee y responde».",
         "4. Practica tu escritura en los renglones.",
         "5. Resuelve los problemas de «Cuenta con…».",
         "6. Recorta el año del personaje y pégalo en tu línea del tiempo."]
y = H - 280; c.setFont(R, 12.5)
for s in pasos: c.drawString(60, y, s); y -= 22
c.setFont(B, 15); c.drawString(50, y - 14, "Personajes"); y -= 40
for i, p in enumerate(P):
    c.setFillColor(HexColor(COLORES[i])); c.circle(64, y + 4, 9, fill=1, stroke=0)
    c.setFillColor(white); c.setFont(B, 10); c.drawCentredString(64, y + 0.5, str(i + 1))
    c.setFillColor(TINTA); c.setFont(B, 12); c.drawString(82, y, p["nombre"])
    c.setFont(R, 11); c.drawString(300, y, p["apodo"]); y -= 21
c.setFont(R, 10); c.setFillColor(HexColor("#7d6a55"))
c.drawString(50, 50, "Para papás y maestros: las respuestas están al final del libro. Ideal para tareas, efemérides y vacaciones.")
pie(); c.showPage()

# ---------- PERSONAJES ----------
for i, p in enumerate(P):
    col = COLORES[i]
    # A) Conoce
    banda(f"{i + 1}. {p['nombre']}", col, f"{p['apodo']}  ·  {p['anios']}")
    if p["slug"] in imgs: c.drawImage(imgs[p["slug"]], (W - 300) / 2, H - 420, 300, 300, mask="auto")
    c.setFillColor(HexColor("#9a7b55")); c.setFont(M, 13); c.drawCentredString(W / 2, H - 433, "¡Colorea el dibujo!")
    c.setFillColor(CREMA); c.setStrokeColor(HexColor(col)); c.setLineWidth(2); c.roundRect(40, 120, W - 80, 220, 16, fill=1, stroke=1)
    parrafo(p["bio"], 56, 328, W - 112, 200)
    c.setFillColor(HexColor(col)); c.roundRect(40, 50, W - 80, 58, 12, fill=1, stroke=0)
    c.setFillColor(white); c.setFont(B, 11); c.drawString(54, 90, "¿Sabías que…?")
    st_dato = ParagraphStyle("dato", fontName=R, fontSize=10.5, leading=13.5, textColor=white)
    parrafo(p["dato"], 54, 84, W - 108, 34, st_dato)
    pie(); c.showPage()
    # B) Lee y responde + escribe
    banda("Lee y responde", col, p["nombre"])
    y = H - 125
    for k, (q, ops, _) in enumerate(p["preguntas"]):
        c.setFillColor(TINTA); c.setFont(B, 12.5); y = texto_envuelto(f"{k + 1}. {q}", 50, y, W - 100, B, 12.5, 17)
        if ops:
            for o in ops:
                c.setStrokeColor(TINTA); c.setLineWidth(1.2); c.circle(70, y + 4, 6, fill=0, stroke=1)
                c.setFont(R, 12); c.drawString(84, y, o); y -= 20
            y -= 6
        else:
            y = renglones(60, y - 8, W - 120, 2, 30) - 4
    c.setFillColor(HexColor(col)); c.roundRect(40, y - 18, 150, 26, 13, fill=1, stroke=0)
    c.setFillColor(white); c.setFont(B, 13); c.drawString(54, y - 10, "Escribe")
    c.setFillColor(TINTA); c.setFont(R, 12); y = texto_envuelto(p["escritura"], 50, y - 42, W - 100, R, 12, 16)
    renglones(60, y - 12, W - 120, max(2, int((y - 80) / 36)), 36)
    pie(); c.showPage()
    # C) Cuenta
    banda(f"Cuenta con {p['nombre'].split()[0] if i not in (1,) else 'Sor Juana'}", col, "Resuelve y escribe tu operación")
    y = H - 125
    for k, (q, _) in enumerate(p["mates"]):
        c.setFillColor(TINTA); c.setFont(B, 12.5); y = texto_envuelto(f"{k + 1}. {q}", 50, y, W - 100, B, 12.5, 17)
        c.setStrokeColor(HexColor("#c9b89f")); c.setLineWidth(1); c.roundRect(60, y - 92, 260, 92, 10, fill=0, stroke=1)
        c.setFont(R, 9.5); c.setFillColor(HexColor("#9a7b55")); c.drawString(70, y - 14, "Mi operación")
        c.setFillColor(TINTA); c.setFont(B, 12); c.drawString(340, y - 50, "Resultado:"); c.line(415, y - 52, W - 60, y - 52)
        y -= 120
    # recortable de línea del tiempo
    anio, ev = p["linea"]
    c.setDash(4, 3); c.setStrokeColor(TINTA); c.roundRect(W / 2 - 150, 52, 300, 64, 10, fill=0, stroke=1); c.setDash()
    c.setFont(R, 9); c.setFillColor(HexColor("#9a7b55")); c.drawCentredString(W / 2, 122, "Recorta y pega en tu línea del tiempo")
    c.setFillColor(HexColor(col)); c.setFont(T, 22); c.drawCentredString(W / 2, 88, str(anio))
    c.setFillColor(TINTA); c.setFont(R, 10.5); c.drawCentredString(W / 2, 66, ev)
    pie(); c.showPage()

# ---------- LÍNEA DEL TIEMPO ----------
banda("Mi línea del tiempo de México", "#3a86ff", "Pega aquí los recortes en orden, del más antiguo al más reciente")
x0, x1, yl = 60, W - 60, H / 2 + 40
c.setStrokeColor(TINTA); c.setLineWidth(3); c.line(x0, yl, x1, yl)
for k in range(10):
    x = x0 + (x1 - x0) * k / 9
    c.setFillColor(HexColor(COLORES[k])); c.circle(x, yl, 7, fill=1, stroke=0)
    yb = yl + 30 if k % 2 == 0 else yl - 110
    c.setDash(3, 3); c.setStrokeColor(HexColor("#9a7b55")); c.setLineWidth(1); c.rect(x - 34, yb, 68, 80, fill=0, stroke=1); c.setDash()
c.setFont(R, 12); c.setFillColor(TINTA)
c.drawCentredString(W / 2, 150, "Pista: empieza con el año más pequeño (1402) y termina con el más grande (1940).")
pie(); c.showPage()

# ---------- SOPA DE LETRAS ----------
banda("Sopa de letras de los héroes", "#ff006e", "Encuentra las 10 palabras")
pal = ["JUAREZ", "HIDALGO", "MORELOS", "ZAPATA", "LEONA", "JOSEFA", "MATILDE", "JUANA", "CAMARENA", "TEXCOCO"]
N = 14; g = [[None] * N for _ in range(N)]; rnd = random.Random(7)
for w in pal:
    for _ in range(500):
        d = rnd.choice([(0, 1), (1, 0), (1, 1)]); r0 = rnd.randrange(N - d[0] * (len(w) - 1)); c0 = rnd.randrange(N - d[1] * (len(w) - 1))
        if all(g[r0 + d[0] * k][c0 + d[1] * k] in (None, w[k]) for k in range(len(w))):
            for k in range(len(w)): g[r0 + d[0] * k][c0 + d[1] * k] = w[k]
            break
ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
cel = 30; gx = (W - N * cel) / 2; gy = H - 130
c.setFont(B, 15); c.setFillColor(TINTA)
for r in range(N):
    for q in range(N):
        ch = g[r][q] or rnd.choice(ABC); c.drawCentredString(gx + q * cel + cel / 2, gy - r * cel - 20, ch)
c.setStrokeColor(HexColor("#c9b89f")); c.roundRect(gx - 8, gy - N * cel - 8, N * cel + 16, N * cel + 16, 10, fill=0, stroke=1)
y = gy - N * cel - 40; c.setFont(R, 12)
for k, w in enumerate(pal):
    xx = 80 + (k % 5) * 95; yy = y - (k // 5) * 22
    c.rect(xx, yy - 1, 9, 9, fill=0, stroke=1); c.drawString(xx + 14, yy, w.capitalize())
pie(); c.showPage()

# ---------- DIPLOMA ----------
c.setStrokeColor(HexColor("#e9c46a")); c.setLineWidth(10); c.roundRect(30, 30, W - 60, H - 60, 24, fill=0, stroke=1)
c.setFillColor(ROJO); c.setFont(T, 40); c.drawCentredString(W / 2, H - 150, "Diploma")
c.setFillColor(TINTA); c.setFont(B, 18); c.drawCentredString(W / 2, H - 190, "de Pequeño Historiador")
c.setFont(R, 14); c.drawCentredString(W / 2, H - 260, "Se otorga a:")
c.setLineWidth(1.2); c.setStrokeColor(TINTA)
c.line(120, H - 310, W - 120, H - 310)
parrafo("Por conocer la historia de 10 héroes de México, leer, escribir y resolver problemas con mucho esfuerzo. ¡Felicidades!",
        110, H - 350, W - 220, 80, ParagraphStyle("d", fontName=R, fontSize=14, leading=20, alignment=1, textColor=TINTA))
c.line(120, 200, 270, 200); c.line(W - 270, 200, W - 120, 200)
c.setFont(R, 11); c.drawCentredString(195, 182, "Fecha"); c.drawCentredString(W - 195, 182, "Firma")
c.setFont(B, 12); c.setFillColor(HexColor("#9a7b55")); c.drawCentredString(W / 2, 90, "Ediciones Guizar")
c.showPage(); pag[0] += 1

# ---------- RESPUESTAS ----------
banda("Respuestas (para papás y maestros)", "#6a994e")
y = H - 120
for i, p in enumerate(P):
    if y < 120:
        pie(); c.showPage(); banda("Respuestas (continuación)", "#6a994e"); y = H - 120
    c.setFillColor(HexColor(COLORES[i])); c.setFont(B, 12); c.drawString(45, y, f"{i + 1}. {p['nombre']}"); y -= 16
    c.setFillColor(TINTA); c.setFont(R, 9.5)
    for k, (q, ops, ans) in enumerate(p["preguntas"]):
        t = ops[ans] if ops else ans
        y = texto_envuelto(f"P{k + 1}: {t}", 55, y, W - 110, R, 9.5, 12)
    y = texto_envuelto("Escribe: " + p["escritura_resp"], 55, y, W - 110, R, 9.5, 12)
    for k, (_, r) in enumerate(p["mates"]):
        y = texto_envuelto(f"M{k + 1}: {r}", 55, y, W - 110, R, 9.5, 12)
    y -= 8
c.setFont(R, 9.5); c.drawString(45, max(y - 6, 60), "Línea del tiempo: 1402, 1695, 1789, 1806, 1810, 1810, 1813, 1887, 1910, 1940.")
pie(); c.showPage()
c.save()

# ---------- muestra + hoja de revisión ----------
import fitz
doc = fitz.open("heroes-de-mexico.pdf"); print("paginas", doc.page_count)
m = fitz.open(); m.insert_pdf(doc, from_page=0, to_page=4); m.save("heroes-de-mexico-muestra.pdf")
from PIL import Image
sel = [0, 1, 2, 3, 4, doc.page_count - 4, doc.page_count - 3, doc.page_count - 1]
ims = []
for k in sel:
    pix = doc[k].get_pixmap(dpi=40); ims.append(Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB"))
w0, h0 = ims[0].size; hoja = Image.new("RGB", (w0 * 4, h0 * 2), "white")
for k, im in enumerate(ims): hoja.paste(im.resize((w0, h0)), ((k % 4) * w0, (k // 4) * h0))
hoja.save("hoja.jpg", quality=60)
open("hoja.txt", "w").write(f"paginas {doc.page_count}\n" + base64.b64encode(open("hoja.jpg", "rb").read()).decode())
for k in [2, 3, 4]:
    doc[k].get_pixmap(dpi=70).save(f"pag{k}.png")
open("pags.txt", "w").write("\n".join(base64.b64encode(open(f"pag{k}.png", "rb").read()).decode() for k in [2, 3, 4]))
