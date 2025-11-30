-- ============================================================================
-- MIGRACIÓN 002: Extender pine_exercise_sessions (ROBLE - TIPOS CORRECTOS)
-- ============================================================================

ALTER TABLE pine_exercise_sessions
  ADD COLUMN pp_ganados int4 DEFAULT 0;

ALTER TABLE pine_exercise_sessions
  ADD COLUMN pd_ganados int4 DEFAULT 0;

ALTER TABLE pine_exercise_sessions
  ADD COLUMN xp_ganados int4 DEFAULT 0;

ALTER TABLE pine_exercise_sessions
  ADD COLUMN bonus_batch_pd int4 DEFAULT 0;

ALTER TABLE pine_exercise_sessions
  ADD COLUMN bonus_racha_pd int4 DEFAULT 0;

ALTER TABLE pine_exercise_sessions
  ADD COLUMN bonus_levelup_pd int4 DEFAULT 0;

ALTER TABLE pine_exercise_sessions
  ADD COLUMN session_type TEXT DEFAULT 'normal';

ALTER TABLE pine_exercise_sessions
  ADD COLUMN total_items int4 DEFAULT 10;

ALTER TABLE pine_exercise_sessions
  ADD COLUMN items_correctos_primer_intento int4 DEFAULT 0;

ALTER TABLE pine_exercise_sessions
  ADD COLUMN items_correctos_reintento int4 DEFAULT 0;

ALTER TABLE pine_exercise_sessions
  ADD COLUMN items_fallados int4 DEFAULT 0;

ALTER TABLE pine_exercise_sessions
  ADD COLUMN tiempo_promedio_segundos float4;

ALTER TABLE pine_exercise_sessions
  ADD COLUMN miniboss_exito bool DEFAULT FALSE;

ALTER TABLE pine_exercise_sessions
  ADD COLUMN miniboss_tiempo_total float4;

ALTER TABLE pine_exercise_sessions
  ADD COLUMN miniboss_aciertos int4;

ALTER TABLE pine_exercise_sessions
  ADD COLUMN miniboss_reintentos int4;

-- Índices
CREATE INDEX IF NOT EXISTS idx_exercise_sessions_user_type 
  ON pine_exercise_sessions(user_ref, session_type);

CREATE INDEX IF NOT EXISTS idx_exercise_sessions_date 
  ON pine_exercise_sessions(user_ref, created_at DESC);
