/**
 * ATTAPOLL INTELLIGENT EARNINGS PRO
 * Supabase Edge Function: groq-assistant
 * Entregables 4 y 5: Edge Function necesaria + configuración del asistente.
 *
 * QUÉ HACE
 * Recibe { question, stats } desde el panel, donde stats son SOLO cifras
 * agregadas ya calculadas por el panel (hoy, semana, mes, ganancia por
 * hora, saldo pendiente, retirado, tiempo perdido, mejor plataforma).
 * Llama a Groq desde el servidor y devuelve { answer } en español.
 * Nunca recibe ni envía preguntas o respuestas de encuestas.
 * Nunca pide, recibe ni guarda contraseñas, códigos ni datos bancarios.
 * Nunca mueve dinero ni ejecuta retiros.
 *
 * DESPLIEGUE DESDE TERMUX / ANDROID
 * 1. Instala la CLI en Termux y entra a la carpeta de tu proyecto:
 *      pkg update && pkg install nodejs
 *      npm install -g supabase
 *      cd <tu-proyecto>            # carpeta que contiene supabase/
 * 2. Coloca este archivo como:
 *      supabase/functions/groq-assistant/index.ts
 * 3. Inicia sesión y enlaza TU proyecto (usa tu propio project-ref):
 *      supabase login
 *      supabase link --project-ref <TU_REF>
 * 4. Guarda la clave de Groq como SECRETO de Supabase (nunca en el código,
 *    nunca en GitHub, nunca en el panel):
 *      supabase secrets set GROQ_API_KEY=<tu clave>
 * 5. Despliega la función:
 *      supabase functions deploy groq-assistant --no-verify-jwt
 *    Alternativa con verificación: si el panel envía el token de sesión
 *    del usuario en el header Authorization, despliega con:
 *      supabase functions deploy groq-assistant --verify-jwt
 * 6. Prueba con curl (reemplaza <TU_PROYECTO> y la URL de tu proyecto):
 *      curl -s -X POST \
 *        https://<TU_PROYECTO>.supabase.co/functions/v1/groq-assistant \
 *        -H "Content-Type: application/json" \
 *        -H "Authorization: Bearer <TU_ANON_KEY>" \
 *        -d '{"question":"¿Cuánto gané hoy?","stats":{"today":0,"week":0,"month":0,"perHour":null,"pending":0,"withdrawn":0,"lostMinutes":0,"bestPlatform":null}}'
 *    Respuesta esperada: {"answer":"..."}
 *
 * COSTO: $0. Usa el nivel gratuito de Supabase Edge Functions y de Groq.
 * No actives ningún servicio de pago.
 */

// ---------------------------------------------------------------------------
// 5. CONFIGURACIÓN DEL ASISTENTE
// ---------------------------------------------------------------------------

export const ASSISTANT_CONFIG = {
  name: "Asistente AttaPoll Intelligent Earnings Pro",
  language: "es-MX",
  model: "llama-3.3-70b-versatile",
  temperature: 0.2,
  maxQuestionLength: 500,
  timeoutMs: 25_000,
  groqUrl: "https://api.groq.com/openai/v1/chat/completions",
  systemPrompt: [
    "Eres un asistente de finanzas personales para ingresos de encuestas",
    "y actividades remuneradas legítimas, dentro de AttaPoll Intelligent",
    "Earnings Pro.",
    "Responde SOLO con las cifras que vienen en los datos (stats) que",
    "recibes en este mensaje. Si un dato no está en stats, di claramente",
    "que no tienes ese dato. Nunca inventes cifras, probabilidades,",
    "plataformas, fechas ni resultados.",
    "Responde en español de México, breve y directo.",
    "Distingue siempre: anunciado no es confirmado, y confirmado no es",
    "recibido. No prometas ganancias futuras: una proyección solo es",
    "válida si viene calculada en stats.",
    "Nunca contestes encuestas por el usuario, nunca pidas contraseñas,",
    "códigos, datos bancarios ni claves, y nunca muevas dinero.",
    "Si la pregunta pide algo fuera de sus cifras registradas, dilo y",
    "ofrece responder sobre los datos que sí tienes.",
  ].join(" "),
} as const;

/** Cifras agregadas que el panel ya calculó. Nada más que esto. */
export interface AssistantStats {
  today?: number | null;
  week?: number | null;
  month?: number | null;
  perHour?: number | null;
  pending?: number | null;
  withdrawn?: number | null;
  lostMinutes?: number | null;
  bestPlatform?: string | null;
  [key: string]: unknown;
}

export interface AssistantRequest {
  question: string;
  stats: AssistantStats;
}

export interface AssistantResponse {
  answer: string;
}

// ---------------------------------------------------------------------------
// Utilidades HTTP / CORS
// ---------------------------------------------------------------------------

const CORS_HEADERS: Record<string, string> = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

function jsonResponse(body: unknown, status: number): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...CORS_HEADERS, "Content-Type": "application/json" },
  });
}

function errorResponse(message: string, status: number): Response {
  return jsonResponse({ error: message }, status);
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** Valida el cuerpo. Devuelve el pedido limpio o un mensaje de error. */
function validateBody(
  body: unknown,
): { ok: true; data: AssistantRequest } | { ok: false; error: string } {
  if (!isPlainObject(body)) {
    return { ok: false, error: "El cuerpo debe ser un objeto JSON." };
  }
  const { question, stats } = body as Record<string, unknown>;
  if (typeof question !== "string" || question.trim().length === 0) {
    return {
      ok: false,
      error: "Falta la pregunta: 'question' debe ser texto no vacío.",
    };
  }
  if (question.length > ASSISTANT_CONFIG.maxQuestionLength) {
    return {
      ok: false,
      error: `La pregunta es demasiado larga (máximo ${ASSISTANT_CONFIG.maxQuestionLength} caracteres).`,
    };
  }
  if (!isPlainObject(stats)) {
    return {
      ok: false,
      error: "Faltan los datos: 'stats' debe ser un objeto con tus cifras.",
    };
  }
  return {
    ok: true,
    data: { question: question.trim(), stats: stats as AssistantStats },
  };
}

// ---------------------------------------------------------------------------
// Llamada a Groq (solo desde el servidor; la clave nunca sale de aquí)
// ---------------------------------------------------------------------------

interface GroqChatResponse {
  choices?: Array<{ message?: { content?: string } }>;
}

async function askGroq(
  apiKey: string,
  question: string,
  stats: AssistantStats,
): Promise<string> {
  const controller = new AbortController();
  const timer = setTimeout(
    () => controller.abort(),
    ASSISTANT_CONFIG.timeoutMs,
  );
  try {
    const res = await fetch(ASSISTANT_CONFIG.groqUrl, {
      method: "POST",
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: ASSISTANT_CONFIG.model,
        temperature: ASSISTANT_CONFIG.temperature,
        messages: [
          { role: "system", content: ASSISTANT_CONFIG.systemPrompt },
          {
            role: "user",
            content:
              `Datos reales del usuario (stats, ya calculados por el panel):\n` +
              `${JSON.stringify(stats)}\n\n` +
              `Pregunta del usuario:\n${question}`,
          },
        ],
      }),
    });

    if (!res.ok) {
      // No se registra la clave ni el contenido de stats.
      console.error(`Groq respondió con estado ${res.status}.`);
      throw new Error("groq_upstream_error");
    }

    const data = (await res.json()) as GroqChatResponse;
    const answer = data.choices?.[0]?.message?.content?.trim();
    if (!answer) throw new Error("groq_empty_answer");
    return answer;
  } finally {
    clearTimeout(timer);
  }
}

// ---------------------------------------------------------------------------
// 4. EDGE FUNCTION: handler principal
// ---------------------------------------------------------------------------

export async function handler(req: Request): Promise<Response> {
  // Preflight CORS
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: CORS_HEADERS });
  }
  if (req.method !== "POST") {
    return errorResponse("Método no permitido. Usa POST.", 405);
  }

  // La clave vive SOLO como secreto de Supabase.
  const apiKey = Deno.env.get("GROQ_API_KEY");
  if (!apiKey) {
    console.error("Falta el secreto GROQ_API_KEY en Supabase.");
    return errorResponse(
      "Falta configurar GROQ_API_KEY en los secretos de Supabase. " +
        "Configúrala con: supabase secrets set GROQ_API_KEY=<tu clave>",
      500,
    );
  }

  let rawBody: unknown;
  try {
    rawBody = await req.json();
  } catch {
    return errorResponse("El cuerpo no es JSON válido.", 400);
  }

  const validated = validateBody(rawBody);
  if (!validated.ok) return errorResponse(validated.error, 400);

  try {
    const answer = await askGroq(
      apiKey,
      validated.data.question,
      validated.data.stats,
    );
    const body: AssistantResponse = { answer };
    return jsonResponse(body, 200);
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      return errorResponse(
        "Groq tardó demasiado en responder (más de 25 segundos). Intenta de nuevo.",
        504,
      );
    }
    return errorResponse(
      "No se pudo obtener respuesta del asistente. Intenta de nuevo en un momento.",
      502,
    );
  }
}

// Supabase Edge Functions: punto de entrada en tiempo de ejecución Deno.
// La guarda permite importar este archivo en pruebas sin abrir un servidor.
if (typeof Deno !== "undefined" && typeof Deno.serve === "function") {
  // Solo auto-registra cuando se ejecuta como función desplegada.
  // En un import de prueba, el entorno puede definir NO_SERVE=1.
  if (Deno.env.get("GROQ_ASSISTANT_NO_SERVE") !== "1") {
    Deno.serve(handler);
  }
}
