CREATE TABLE IF NOT EXISTS pine_pending_items (
  id SERIAL PRIMARY KEY,
  user_ref TEXT NOT NULL,
  operacion TEXT NOT NULL,
  ejercicio_data JSONB NOT NULL,
  dificultad float4 NOT NULL,
  estado TEXT DEFAULT 'pendiente',
  prioridad float4 DEFAULT 1.0,
  created_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pending_user_op ON pine_pending_items(user_ref, operacion, estado);
