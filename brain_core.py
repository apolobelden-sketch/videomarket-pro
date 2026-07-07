Brain Core AI - Orquestador Principal
Este script analiza la intención del usuario y delega la tarea.
def router_ia(user_input):
print(f"Analizando solicitud: {user_input}")
if "imagen" in user_input.lower():
return "Ejecutando modulo de diseño (Canva/Imagen)..."
elif "correo" in user_input.lower():
return "Ejecutando modulo de comunicacion (Gmail)..."
else:
return "Solicitud general: Usando LLM central..."
Ejemplo de prueba
print(router_ia("Quiero crear una imagen para mi campana"))
