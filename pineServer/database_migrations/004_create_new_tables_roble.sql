-- ============================================================================
-- MIGRACIÓN 004: Crear tablas nuevas (ROBLE - TIPOS CORRECTOS)
-- ============================================================================

-- ===========================================
-- TABLA: pine_pending_items (NORMALIZADO)
-- ===========================================

CREATE TABLE IF NOT EXISTS pine_pending_items (
  id SERIAL PRIMARY KEY,
  user_ref TEXT NOT NULL,
  exercise_ref TEXT NOT NULL,  -- FK a pine_exercises (como TEXT/VARCHAR)
  
  -- Cache para queries rápidas
  operacion TEXT,  -- TEXT es mejor que VARCHAR para strings pequeños
  dificultad float4,
  
  -- Metadatos del fallo
  intentos_fallidos int4 DEFAULT 1,
  fecha_primer_fallo timestamptz,
  fecha_ultimo_fallo timestamptz,
  
  -- Estado
  mostrado_nuevamente bool DEFAULT FALSE NOT NULL,
  completado bool DEFAULT FALSE NOT NULL,
  fecha_completado timestamptz,
  
  created_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
  
  UNIQUE(user_ref, exercise_ref)
);

CREATE INDEX IF NOT EXISTS idx_pending_items_user 
  ON pine_pending_items(user_ref, completado);

CREATE INDEX IF NOT EXISTS idx_pending_items_operacion 
  ON pine_pending_items(user_ref, operacion, completado);

CREATE INDEX IF NOT EXISTS idx_pending_items_exercise
  ON pine_pending_items(exercise_ref);

-- ===========================================
-- TABLA: pine_weekly_leaderboard
-- ===========================================

CREATE TABLE IF NOT EXISTS pine_weekly_leaderboard (
  id SERIAL PRIMARY KEY,
  user_ref TEXT NOT NULL,
  
  semana_id TEXT NOT NULL,  -- '2024-W48'
  
  pp_semana int4 DEFAULT 0,
  pd_semana int4 DEFAULT 0,
  score_semanal float4 DEFAULT 0,
  
  ranking int4,
  
  fecha_inicio timestamptz,
  fecha_fin timestamptz,
  created_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
  
  UNIQUE(user_ref, semana_id)
);

CREATE INDEX IF NOT EXISTS idx_leaderboard_semana 
  ON pine_weekly_leaderboard(semana_id, score_semanal DESC);

CREATE INDEX IF NOT EXISTS idx_leaderboard_ranking 
  ON pine_weekly_leaderboard(semana_id, ranking);

CREATE INDEX IF NOT EXISTS idx_leaderboard_user 
  ON pine_weekly_leaderboard(user_ref, semana_id);

-- ===========================================
-- TABLA: pine_nivel_dominio_log
-- ===========================================

CREATE TABLE IF NOT EXISTS pine_nivel_dominio_log (
  id SERIAL PRIMARY KEY,
  user_ref TEXT NOT NULL,
  
  operacion TEXT NOT NULL,  -- TEXT es óptimo para strings cortos conocidos
  nivel_anterior int2 NOT NULL,
  nivel_nuevo int2 NOT NULL,
  pd_operacion int4 NOT NULL,
  
  fecha timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_dominio_log_user 
  ON pine_nivel_dominio_log(user_ref, operacion);

-- ===========================================
-- TABLA: pine_mini_jefes_intentos
-- ===========================================

CREATE TABLE IF NOT EXISTS pine_mini_jefes_intentos (
  id SERIAL PRIMARY KEY,
  user_ref TEXT NOT NULL,
  
  mini_jefe TEXT NOT NULL CHECK (mini_jefe IN ('suma', 'mult', 'div')),
  
  exito bool NOT NULL,
  
  total_items int4 NOT NULL,
  items_correctos int4 NOT NULL,
  porcentaje_acierto float4 NOT NULL,
  tiempo_total_segundos float4,
  reintentos_usados int4 DEFAULT 0,
  
  operacion_desbloqueada TEXT CHECK (operacion_desbloqueada IN ('resta', 'mult', 'div')),
  
  fecha timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_minijefes_user 
  ON pine_mini_jefes_intentos(user_ref, mini_jefe, exito);

CREATE INDEX IF NOT EXISTS idx_minijefes_fecha 
  ON pine_mini_jefes_intentos(user_ref, fecha DESC);
