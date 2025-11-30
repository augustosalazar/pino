-- ============================================================================
-- MIGRACIÓN 001: Crear tablas de gamificación (ROBLE - TIPOS CORRECTOS)
-- ============================================================================

-- ===========================================
-- TABLA 1: pine_user_gamification
-- ===========================================

CREATE TABLE IF NOT EXISTS pine_user_gamification (
  user_ref TEXT PRIMARY KEY,
  
  -- === PUNTOS DE PRÁCTICA (PP) ===
  pp_total int4 DEFAULT 0 NOT NULL,
  pp_dia int4 DEFAULT 0 NOT NULL,
  pp_semana int4 DEFAULT 0 NOT NULL,
  pp_dia_max int4 DEFAULT 30 NOT NULL,
  pp_ultima_fecha date,
  
  -- === PUNTOS DE DOMINIO GLOBALES ===
  pd_global int4 DEFAULT 0 NOT NULL,
  pd_semana int4 DEFAULT 0 NOT NULL,
  
  -- === EXPERIENCIA Y NIVEL DEL JUGADOR ===
  xp_total int4 DEFAULT 0 NOT NULL,
  nivel_jugador int4 DEFAULT 1 NOT NULL,
  
  -- === RACHA DIARIA ===
  racha_dias int4 DEFAULT 0 NOT NULL,
  racha_ultima_fecha date,
  
  -- === DESBLOQUEOS DE MODOS DE JUEGO ===
  unlocked_mix_suma_resta bool DEFAULT FALSE NOT NULL,
  unlocked_mix_mult_div bool DEFAULT FALSE NOT NULL,
  unlocked_speed bool DEFAULT FALSE NOT NULL,
  unlocked_bosses bool DEFAULT FALSE NOT NULL,
  unlocked_elite bool DEFAULT FALSE NOT NULL,
  unlocked_master bool DEFAULT FALSE NOT NULL,
  
  -- === TIMESTAMPS ===
  semana_inicio timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
  created_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_gamification_score 
  ON pine_user_gamification(pp_semana DESC, pd_semana DESC);

CREATE INDEX IF NOT EXISTS idx_gamification_xp 
  ON pine_user_gamification(xp_total DESC, nivel_jugador DESC);

CREATE INDEX IF NOT EXISTS idx_gamification_pd_global 
  ON pine_user_gamification(pd_global DESC);

CREATE INDEX IF NOT EXISTS idx_gamification_racha
  ON pine_user_gamification(racha_dias DESC);

-- ===========================================
-- TABLA 2: pine_user_operations
-- ===========================================

CREATE TABLE IF NOT EXISTS pine_user_operations (
  id SERIAL PRIMARY KEY,
  user_ref TEXT NOT NULL,
  operacion TEXT NOT NULL CHECK (operacion IN ('suma', 'resta', 'mult', 'div')),
  
  -- === PUNTOS DE DOMINIO POR OPERACIÓN ===
  pd_operacion int4 DEFAULT 0 NOT NULL,
  
  -- === NIVEL DE DOMINIO (0-5) ===
  nivel_dominio int2 DEFAULT 0 NOT NULL CHECK (nivel_dominio BETWEEN 0 AND 5),
  
  -- === DESBLOQUEO ===
  unlocked bool DEFAULT FALSE NOT NULL,
  
  -- === MINI-JEFE ===
  miniboss_completed bool DEFAULT FALSE NOT NULL,
  miniboss_attempts int4 DEFAULT 0 NOT NULL,
  miniboss_last_attempt timestamptz,
  
  -- === ESTADÍSTICAS ADICIONALES ===
  total_ejercicios int4 DEFAULT 0 NOT NULL,
  total_correctos int4 DEFAULT 0 NOT NULL,
  
  -- === TIMESTAMPS ===
  created_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
  
  UNIQUE(user_ref, operacion)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_user_operations_user 
  ON pine_user_operations(user_ref);

CREATE INDEX IF NOT EXISTS idx_user_operations_user_op 
  ON pine_user_operations(user_ref, operacion);

CREATE INDEX IF NOT EXISTS idx_user_operations_pd 
  ON pine_user_operations(pd_operacion DESC);

CREATE INDEX IF NOT EXISTS idx_user_operations_nivel 
  ON pine_user_operations(operacion, nivel_dominio);
