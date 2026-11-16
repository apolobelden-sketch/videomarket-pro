-- ============================================================================
-- ATTAPOLL INTELLIGENT EARNINGS PRO — Esquema PostgreSQL para Supabase
-- ============================================================================
-- Cómo usarlo (desde Android, sin computadora):
--   1. Entra a tu proyecto en https://supabase.com/dashboard
--   2. Abre "SQL Editor" > "New query"
--   3. Pega todo este archivo y pulsa "Run"
--   4. No pegues aquí ninguna clave privada. Este archivo NO contiene secretos.
--
-- Moneda: los montos se guardan en la moneda original (USD o MXN) y el
-- panel convierte a MXN con el tipo de cambio guardado en settings.
-- Nada de este esquema responde encuestas, guarda respuestas de encuestas
-- ni automatiza interacciones con AttaPoll u otras plataformas.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- profiles: un registro por usuario (dueño de sus datos)
-- ----------------------------------------------------------------------------
create table if not exists public.profiles (
  id            uuid primary key references auth.users (id) on delete cascade,
  display_name  text,
  currency      text not null default 'MXN' check (currency in ('MXN','USD')),
  usd_to_mxn    numeric(10,4) not null default 18.00,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

-- ----------------------------------------------------------------------------
-- platforms: AttaPoll y cualquier otra plataforma legítima de actividades
-- ----------------------------------------------------------------------------
create table if not exists public.platforms (
  id              uuid primary key default gen_random_uuid(),
  user_id         uuid not null references public.profiles (id) on delete cascade,
  name            text not null,                       -- ej. AttaPoll
  kind            text not null default 'survey'
                  check (kind in ('survey','task','cashback','referral','other')),
  payout_method   text not null default 'PayPal',     -- PayPal, transferencia, etc.
  min_payout      numeric(10,2),                      -- mínimo para retirar
  currency        text not null default 'USD' check (currency in ('MXN','USD')),
  active          boolean not null default true,
  created_at      timestamptz not null default now(),
  unique (user_id, name)
);

-- ----------------------------------------------------------------------------
-- activities: cada actividad remunerada (encuesta, tarea, etc.)
-- Solo datos generales: NUNCA preguntas ni respuestas de encuestas.
-- ----------------------------------------------------------------------------
create table if not exists public.activities (
  id                    uuid primary key default gen_random_uuid(),
  user_id               uuid not null references public.profiles (id) on delete cascade,
  platform_id           uuid not null references public.platforms (id) on delete restrict,
  activity_type         text not null,                 -- encuesta, tarea, video, etc.
  title                 text,                          -- nombre general, ej. "Encuesta de consumo"
  reward_announced      numeric(10,2) not null default 0 check (reward_announced >= 0),
  reward_confirmed      numeric(10,2) not null default 0 check (reward_confirmed >= 0),
  currency              text not null default 'USD' check (currency in ('MXN','USD')),
  duration_estimated_min integer check (duration_estimated_min >= 0),
  duration_actual_min   integer check (duration_actual_min >= 0),
  status                text not null default 'pending'
                        check (status in ('pending','completed','disqualified','abandoned')),
  activity_date         date not null default current_date,
  notes                 text,
  created_at            timestamptz not null default now(),
  updated_at            timestamptz not null default now(),
  -- Una actividad completada o descalificada debe tener tiempo real registrado
  constraint completed_needs_time
    check (status not in ('completed','disqualified') or duration_actual_min is not null)
);

-- ----------------------------------------------------------------------------
-- earnings: dinero ganado (anunciado -> confirmado -> recibido)
-- ----------------------------------------------------------------------------
create table if not exists public.earnings (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references public.profiles (id) on delete cascade,
  activity_id   uuid references public.activities (id) on delete set null,
  platform_id   uuid references public.platforms (id) on delete set null,
  amount        numeric(10,2) not null check (amount >= 0),
  currency      text not null default 'USD' check (currency in ('MXN','USD')),
  source        text not null default 'activity'
                check (source in ('activity','bonus','referral','adjustment')),
  status        text not null default 'announced'
                check (status in ('announced','confirmed','received')),
  received_at   timestamptz,
  created_at    timestamptz not null default now()
);

-- ----------------------------------------------------------------------------
-- withdrawals: retiros de PayPal (solo registro; aquí NADA mueve dinero)
-- paypal_identifier: identificador NO sensible (ej. tu correo de PayPal).
-- NUNCA guardes contraseñas ni códigos.
-- ----------------------------------------------------------------------------
create table if not exists public.withdrawals (
  id                  uuid primary key default gen_random_uuid(),
  user_id             uuid not null references public.profiles (id) on delete cascade,
  platform_id         uuid references public.platforms (id) on delete set null,
  paypal_identifier   text,
  amount              numeric(10,2) not null check (amount > 0),
  fee                 numeric(10,2) not null default 0 check (fee >= 0),
  currency            text not null default 'USD' check (currency in ('MXN','USD')),
  status              text not null default 'requested'
                      check (status in ('requested','received','failed')),
  requested_at        timestamptz not null default now(),
  received_at         timestamptz,
  created_at          timestamptz not null default now()
);

-- ----------------------------------------------------------------------------
-- expenses: costos asociados (ej. comisiones, datos móviles si los cuentas)
-- ----------------------------------------------------------------------------
create table if not exists public.expenses (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references public.profiles (id) on delete cascade,
  concept     text not null,
  amount      numeric(10,2) not null check (amount >= 0),
  currency    text not null default 'MXN' check (currency in ('MXN','USD')),
  expense_date date not null default current_date,
  created_at  timestamptz not null default now()
);

-- ----------------------------------------------------------------------------
-- daily_reports: resumen diario calculado (para informes rápidos)
-- ----------------------------------------------------------------------------
create table if not exists public.daily_reports (
  id                    uuid primary key default gen_random_uuid(),
  user_id               uuid not null references public.profiles (id) on delete cascade,
  report_date           date not null,
  total_earned          numeric(10,2) not null default 0,
  total_received        numeric(10,2) not null default 0,
  minutes_invested      integer not null default 0,
  activities_completed  integer not null default 0,
  activities_disqualified integer not null default 0,
  avg_per_hour          numeric(10,2),
  created_at            timestamptz not null default now(),
  unique (user_id, report_date)
);

-- ----------------------------------------------------------------------------
-- settings: preferencias del usuario (clave/valor)
-- ----------------------------------------------------------------------------
create table if not exists public.settings (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references public.profiles (id) on delete cascade,
  key         text not null,
  value       jsonb not null default '{}'::jsonb,
  updated_at  timestamptz not null default now(),
  unique (user_id, key)
);

-- ----------------------------------------------------------------------------
-- audit_logs: registro de operaciones importantes (quién hizo qué y cuándo)
-- ----------------------------------------------------------------------------
create table if not exists public.audit_logs (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references public.profiles (id) on delete cascade,
  action      text not null,                 -- create, update, delete, export, login
  entity      text not null,                 -- activities, withdrawals, etc.
  entity_id   uuid,
  details     jsonb not null default '{}'::jsonb,
  created_at  timestamptz not null default now()
);

-- ============================================================================
-- VISTAS DE RENTABILIDAD (solo lectura; los cálculos viven también en el panel)
-- ============================================================================

-- Ganancia por hora por actividad completada con recompensa confirmada
create or replace view public.v_activity_profitability as
select
  a.id,
  a.user_id,
  a.platform_id,
  a.activity_date,
  a.status,
  a.reward_confirmed,
  a.currency,
  a.duration_actual_min,
  case
    when a.duration_actual_min > 0
      then round(a.reward_confirmed / (a.duration_actual_min::numeric / 60), 2)
    else null
  end as per_hour
from public.activities a
where a.status = 'completed';

-- Resumen por plataforma
create or replace view public.v_platform_summary as
select
  p.id as platform_id,
  p.user_id,
  p.name,
  count(a.id) filter (where a.status = 'completed')     as completed,
  count(a.id) filter (where a.status = 'disqualified')  as disqualified,
  coalesce(sum(a.reward_confirmed) filter (where a.status = 'completed'), 0) as total_confirmed,
  coalesce(sum(a.duration_actual_min), 0)               as total_minutes,
  case
    when coalesce(sum(a.duration_actual_min) filter (where a.status = 'completed'), 0) > 0
      then round(
        coalesce(sum(a.reward_confirmed) filter (where a.status = 'completed'), 0)
        / (sum(a.duration_actual_min) filter (where a.status = 'completed')::numeric / 60), 2)
    else null
  end as per_hour
from public.platforms p
left join public.activities a on a.platform_id = p.id
group by p.id, p.user_id, p.name;

-- ============================================================================
-- SEGURIDAD: Row Level Security — cada usuario solo ve y toca SUS registros
-- ============================================================================
alter table public.profiles       enable row level security;
alter table public.platforms      enable row level security;
alter table public.activities     enable row level security;
alter table public.earnings       enable row level security;
alter table public.withdrawals    enable row level security;
alter table public.expenses       enable row level security;
alter table public.daily_reports  enable row level security;
alter table public.settings       enable row level security;
alter table public.audit_logs     enable row level security;

-- profiles: el usuario solo accede a su propio perfil
create policy "profiles_owner" on public.profiles
  for all using (auth.uid() = id) with check (auth.uid() = id);

-- resto de tablas: el usuario solo accede a filas con su user_id
create policy "platforms_owner" on public.platforms
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "activities_owner" on public.activities
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "earnings_owner" on public.earnings
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "withdrawals_owner" on public.withdrawals
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "expenses_owner" on public.expenses
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "daily_reports_owner" on public.daily_reports
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "settings_owner" on public.settings
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "audit_logs_owner" on public.audit_logs
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ============================================================================
-- DATOS INICIALES (opcionales): plataformas comunes, SIN montos reales.
-- Ejecuta solo la parte que quieras; AttaPoll queda como plataforma inicial.
-- ============================================================================
-- insert into public.platforms (user_id, name, kind, payout_method, currency)
-- values (auth.uid(), 'AttaPoll', 'survey', 'PayPal', 'USD');
