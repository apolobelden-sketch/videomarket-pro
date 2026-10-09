import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.39.0/+esm'

const SUPABASE_URL = 'https://pnjglzuxsyahxcbgjwvq.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBuamdsenV4c3lhaHhjYmdqd3ZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE1NjI0ODcsImV4cCI6MjA5NzEzODQ4N30.iD-yLgcC5GiGWQseAykLnONTCr1qA7kXSWgqVQ3-gfM'

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Lectura: solo tablas con politica publica. El orden es opcional.
export async function consultarTabla(tabla, { columnas = '*', orden = null, ascendente = false, limite = 100 } = {}) {
  try {
    let q = supabase.from(tabla).select(columnas).limit(Math.min(limite, 500))
    if (orden) q = q.order(orden, { ascending: ascendente })
    const { data, error } = await q
    if (error) throw error
    return { exito: true, data }
  } catch (err) {
    console.error(`[Ecosistema] Consulta a ${tabla}:`, err.message)
    return { exito: false, error: err.message }
  }
}

// Solo funciones pensadas para el publico.
const FUNCIONES_PUBLICAS = ['profe', 'cerebro']
export async function llamarFuncionBorde(nombre, payload = {}) {
  if (!FUNCIONES_PUBLICAS.includes(nombre)) {
    return { exito: false, error: 'Funcion no permitida desde el navegador.' }
  }
  try {
    const { data, error } = await supabase.functions.invoke(nombre, { body: payload })
    if (error) throw error
    return { exito: true, respuesta: data }
  } catch (err) {
    console.error(`[Ecosistema] Funcion ${nombre}:`, err.message)
    return { exito: false, error: err.message }
  }
}

// Subida desactivada a proposito: abrirla al publico permitiria que cualquiera llene el almacenamiento.
export async function subirArchivoStorage() {
  return { exito: false, error: 'Subida desactivada por seguridad. Requiere inicio de sesion.' }
}
