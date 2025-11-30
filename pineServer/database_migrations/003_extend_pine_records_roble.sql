-- ============================================================================
-- MIGRACIÓN 003: Extender pine_exercises (ROBLE - TIPOS CORRECTOS)
-- ============================================================================

ALTER TABLE pine_exercises
  ADD COLUMN fue_primer_intento bool DEFAULT TRUE;

ALTER TABLE pine_exercises
  ADD COLUMN requirio_reintento bool DEFAULT FALSE;

ALTER TABLE pine_exercises
  ADD COLUMN reintento_exitoso bool;

ALTER TABLE pine_exercises
  ADD COLUMN pp_ganados int4 DEFAULT 0;

ALTER TABLE pine_exercises
  ADD COLUMN pd_ganados int4 DEFAULT 0;

ALTER TABLE pine_exercises
  ADD COLUMN operacion TEXT;

ALTER TABLE pine_exercises
  ADD COLUMN debe_repetirse bool DEFAULT FALSE;

ALTER TABLE pine_exercises
  ADD COLUMN repeticion_programada bool DEFAULT FALSE;

-- Índices
CREATE INDEX IF NOT EXISTS idx_exercises_repeticion 
  ON pine_exercises(user_ref, debe_repetirse) WHERE debe_repetirse = TRUE;

CREATE INDEX IF NOT EXISTS idx_exercises_operacion 
  ON pine_exercises(user_ref, operacion);

CREATE INDEX IF NOT EXISTS idx_exercises_session_stats 
  ON pine_exercises(session_id, fue_primer_intento, requirio_reintento);
