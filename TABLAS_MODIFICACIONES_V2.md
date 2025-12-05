# Modificaciones de Tablas para Gamificación V2

**Fecha**: 2025-12-05  
**Estado**: Análisis de  tablas existentes vs. nuevas necesidades

---

## 📊 RESUMEN DE ANÁLISIS

### Tablas Existentes que SE REUTILIZAN:
✅ `pine_user_gamification` - Perfil general de gamificación  
✅ `pine_user_operations` - Progreso por operación  
✅ `pine_pending_items` - Ejercicios pendientes de repetición  
✅ `pine_weekly_leaderboard` - Tabla de clasificación semanal  
✅ `pine_nivel_dominio_log` - Historial de cambios de nivel  
✅ `pine_mini_jefes_intentos` - Intentos de mini-jefes  

### Tablas Existentes que NO CAMBIAN:
- `pine_users` - Usuarios base
- `pine_institutions` - Instituciones
- `pine_exercise_sessions` - Sesiones de ejercicios
- `pine_exercises` - Ejercicios individuales
- `pine_user_difficulty_profile` - Perfiles de dificultad (legacy)
- `pine_difficulty_adjustments` - Ajustes de dificultad (legacy)
- `pine_model_assignments` - Asignaciones de modelo A/B

---

## 🔧 MODIFICACIONES A TABLAS EXISTENTES

### 1. `pine_user_operations` - AGREGAR CAMPO

**Campo nuevo para nivel invisible:**

```sql
-- Agregar columna para nivel invisible (nivel real/interno)
ALTER TABLE pine_user_operations
ADD COLUMN nivel_invisible float4 DEFAULT 1.0 NOT NULL;

-- Crear índice para queries
CREATE INDEX idx_user_operations_nivel_invisible 
  ON pine_user_operations(user_ref, nivel_invisible);
```

**Nota**: 
- `nivel_dominio` (int2) = Nivel visible (1-5, nunca baja)
- `nivel_invisible` (float4) = Nivel real (1.0-6.0, sube/baja para ajustar dificultad)

---

### 2. `pine_user_operations` - AGREGAR CAMPOS DE CONTROL DE MINIBOSS

**Agregar tracking mejorado de miniboss:**

```sql
-- Agregar campos para controlar cuándo presentar miniboss
ALTER TABLE pine_user_operations
ADD COLUMN batches_desde_ultimo_miniboss int4 DEFAULT 0 NOT NULL;

ALTER TABLE pine_user_operations
ADD COLUMN miniboss_fallos_consecutivos int4 DEFAULT 0 NOT NULL;
```

**Lógica**:
- `batches_desde_ultimo_miniboss`: Cuenta batches desde último intento de miniboss
- `miniboss_fallos_consecutivos`: Si falla miniboss, debe completar 3+ batches antes del siguiente

---

### 3. `pine_user_gamification` - AGREGAR CAMPOS DE STREAK MEJORADO

```sql
-- Agregar racha máxima histórica
ALTER TABLE pine_user_gamification
ADD COLUMN racha_maxima int4 DEFAULT 0 NOT NULL;

-- Agregar contador de días con >= 4 aciertos (para validar streak)
ALTER TABLE pine_user_gamification
ADD COLUMN dias_validos_streak int4 DEFAULT 0 NOT NULL;
```

**Lógica**:
- `racha_maxima`: Registro histórico de mejor racha
- `dias_validos_streak`: Solo cuenta días con 4+ aciertos

---

## ➕ NUEVAS TABLAS NECESARIAS

### 4. `pine_batches_completados` - Historial detallado de batches

**Propósito**: Guardar historial completo de cada batch para análisis y progresión

```sql
CREATE TABLE pine_batches_completados (
  id SERIAL PRIMARY KEY,
  user_ref TEXT NOT NULL,
  
  -- Identificación del batch
  batch_type TEXT NOT NULL,  -- 'regular', 'miniboss', 'endless'
  operacion TEXT NOT NULL,   -- 'suma', 'resta', 'mult', 'div'
  
  -- Nivel del batch
  nivel_central int2 NOT NULL,
  nivel_invisible_antes float4 NOT NULL,
  nivel_invisible_despues float4 NOT NULL,
  
  -- Estadísticas
  total_ejercicios int2 NOT NULL,
  ejercicios_correctos int2 NOT NULL,
  dificultad_promedio float4 NOT NULL,
  
  -- Puntuación
  score_ganado int4 NOT NULL,
  pp_ganados int4 NOT NULL,
  pd_ganados int4 DEFAULT 0,
  xp_ganada int4 DEFAULT 0,
  
  -- Detalles del batch (JSONB para flexibilidad)
  ejercicios_data JSONB,  -- Array de ejercicios con respuestas
  
  -- Caso especial: Miniboss
  miniboss_aprobado bool,  -- NULL si no es miniboss
  
  -- Caso especial: Endless
  endless_streak int4,  -- NULL si no es endless
  
  -- Timestamps
  completado_en timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
  duracion_segundos int4
);

-- Índices
CREATE INDEX idx_batches_user ON pine_batches_completados(user_ref);
CREATE INDEX idx_batches_user_fecha ON pine_batches_completados(user_ref, completado_en DESC);
CREATE INDEX idx_batches_operacion ON pine_batches_completados(operacion);
CREATE INDEX idx_batches_tipo ON pine_batches_completados(batch_type);
```

**Estructura de `ejercicios_data` (JSONB)**:
```json
[
  {
    "num": 1,
    "operand_1": 5,
    "operand_2": 3,
    "respuesta_correcta": 8,
    "respuesta_usuario": 8,
    "es_correcto": true,
    "dificultad": 1.5,
    "tiempo_segundos": 3.2,
    "fue_retry": false
  }
]
```

---

### 5. `pine_configuracion_dificultad` - Configuración de niveles

**Propósito**: Configuración dinámica de parámetros por nivel (para A/B testing)

```sql
CREATE TABLE pine_configuracion_dificultad (
  id SERIAL PRIMARY KEY,
  
  operacion TEXT NOT NULL,  -- 'suma', 'resta', 'mult', 'div'
  nivel int2 NOT NULL,      -- 1, 2, 3, 4, 5
  
  -- Rangos de operandos
  min_operando_1 int4 NOT NULL,
  max_operando_1 int4 NOT NULL,
  min_operando_2 int4 NOT NULL,
  max_operando_2 int4 NOT NULL,
  
  -- Límite de resultado
  max_resultado int4,
  
  -- Tipo de respuesta
  tipo_respuesta TEXT NOT NULL,  -- 'multiple_choice', 'abierta'
  num_opciones int2,  -- Para multiple choice
  
  -- Tiempo
  max_tiempo_segundos int4 NOT NULL,
  
  -- Puntuación interna de dificultad (para stats)
  dificultad_score float4 NOT NULL,
  
  -- Versión de configuración (para A/B testing)
  config_version int2 DEFAULT 1 NOT NULL,
  activa bool DEFAULT TRUE NOT NULL,
  
  created_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
  
  UNIQUE(operacion, nivel, config_version)
);

-- Índices
CREATE INDEX idx_config_dif_activa 
  ON pine_configuracion_dificultad(operacion, nivel, activa);
```

**Datos iniciales a insertar**: Ver script de población más abajo.

---

### 6. `pine_leaderboard_endless_mensual` - Ranking endless mensual

**Propósito**: Tabla de clasificación para modo endless (separada de weekly)

```sql
CREATE TABLE pine_leaderboard_endless_mensual (
  id SERIAL PRIMARY KEY,
  user_ref TEXT NOT NULL,
  
  mes_id TEXT NOT NULL,  -- '2025-12'
  
  mejor_streak int4 DEFAULT 0,
  total_intentos int4 DEFAULT 0,
  
  ranking int4,
  
  fecha_inicio date,
  fecha_fin date,
  created_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
  
  UNIQUE(user_ref, mes_id)
);

-- Índices
CREATE INDEX idx_endless_mes 
  ON pine_leaderboard_endless_mensual(mes_id, mejor_streak DESC);

CREATE INDEX idx_endless_ranking 
  ON pine_leaderboard_endless_mensual(mes_id, ranking);

CREATE INDEX idx_endless_user 
  ON pine_leaderboard_endless_mensual(user_ref, mes_id);
```

---

### 7. `pine_configuracion_sistema` - Parámetros del sistema

**Propósito**: Configuración centralizada del sistema (puntuación, streak, etc.)

```sql
CREATE TABLE pine_configuracion_sistema (
  config_key TEXT PRIMARY KEY,
  config_value JSONB NOT NULL,
  description TEXT,
  version int2 DEFAULT 1 NOT NULL,
  activa bool DEFAULT TRUE NOT NULL,
  created_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Índice
CREATE INDEX idx_config_sistema_activa 
  ON pine_configuracion_sistema(config_key, activa);
```

**Datos iniciales a insertar**:

```sql
-- Configuración de puntuación
INSERT INTO pine_configuracion_sistema (config_key, config_value, description) VALUES
('scoring.base_multiplier', '{"value": 5, "type": "integer"}', 'Multiplicador base: C × (value + d̄)'),
('scoring.participation_bonus', '{"value": 10, "type": "integer"}', 'Bonus por completar batch'),
('scoring.error_penalty', '{"value": 2, "type": "integer"}', 'Penalización por error'),

-- Configuración de streak
('streak.min_correct', '{"value": 4, "type": "integer"}', 'Mínimo de aciertos para contar streak'),
('streak.base_score', '{"value": 5, "type": "integer"}', 'Puntos base de streak'),
('streak.daily_multiplier', '{"value": 3, "type": "integer"}', 'Multiplicador por día'),
('streak.max_days', '{"value": 30, "type": "integer"}', 'Días máximos de streak'),

-- Configuración de puntos de práctica
('practice_points.chest_interval', '{"value": 100, "type": "integer"}', 'PP para abrir cofre'),

-- Configuración de miniboss
('miniboss.min_batches_after_fail', '{"value": 3, "type": "integer"}', 'Batches mínimos tras fallo'),
('miniboss.min_correct_rate', '{"value": 0.8, "type": "float"}', 'Tasa de aciertos mínima (80%)'),
('miniboss.nivel_invisible_threshold', '{"value": 0.5, "type": "float"}', 'Diferencia mínima de nivel'),

-- Configuración de batch
('batch.size', '{"value": 10, "type": "integer"}', 'Ejercicios por batch'),
('batch.distribution_easy', '{"value": 2, "type": "integer"}', 'Ejercicios fáciles'),
('batch.distribution_central', '{"value": 6, "type": "integer"}', 'Ejercicios centrales'),
('batch.distribution_hard', '{"value": 2, "type": "integer"}', 'Ejercicios difíciles');
```

---

## 📝 SCRIPT COMPLETO DE MIGRACIÓN

### Archivo: `005_add_gamification_v2_fields.sql`

```sql
-- ============================================================================
-- MIGRACIÓN 005: Campos y tablas para Gamificación V2
-- ============================================================================

-- === MODIFICAR TABLAS EXISTENTES ===

-- 1. pine_user_operations: Agregar nivel invisible y control de miniboss
ALTER TABLE pine_user_operations
  ADD COLUMN IF NOT EXISTS nivel_invisible float4 DEFAULT 1.0 NOT NULL,
  ADD COLUMN IF NOT EXISTS batches_desde_ultimo_miniboss int4 DEFAULT 0 NOT NULL,
  ADD COLUMN IF NOT EXISTS miniboss_fallos_consecutivos int4 DEFAULT 0 NOT NULL;

CREATE INDEX IF NOT EXISTS idx_user_operations_nivel_invisible 
  ON pine_user_operations(user_ref, nivel_invisible);

-- 2. pine_user_gamification: Agregar tracking mejorado de streak
ALTER TABLE pine_user_gamification
  ADD COLUMN IF NOT EXISTS racha_maxima int4 DEFAULT 0 NOT NULL,
  ADD COLUMN IF NOT EXISTS dias_validos_streak int4 DEFAULT 0 NOT NULL;

-- === CREAR NUEVAS TABLAS ===

-- 3. pine_batches_completados
CREATE TABLE IF NOT EXISTS pine_batches_completados (
  id SERIAL PRIMARY KEY,
  user_ref TEXT NOT NULL,
  batch_type TEXT NOT NULL,
  operacion TEXT NOT NULL,
  nivel_central int2 NOT NULL,
  nivel_invisible_antes float4 NOT NULL,
  nivel_invisible_despues float4 NOT NULL,
  total_ejercicios int2 NOT NULL,
  ejercicios_correctos int2 NOT NULL,
  dificultad_promedio float4 NOT NULL,
  score_ganado int4 NOT NULL,
  pp_ganados int4 NOT NULL,
  pd_ganados int4 DEFAULT 0,
  xp_ganada int4 DEFAULT 0,
  ejercicios_data JSONB,
  miniboss_aprobado bool,
  endless_streak int4,
  completado_en timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
  duracion_segundos int4
);

CREATE INDEX IF NOT EXISTS idx_batches_user ON pine_batches_completados(user_ref);
CREATE INDEX IF NOT EXISTS idx_batches_user_fecha ON pine_batches_completados(user_ref, completado_en DESC);
CREATE INDEX IF NOT EXISTS idx_batches_operacion ON pine_batches_completados(operacion);
CREATE INDEX IF NOT EXISTS idx_batches_tipo ON pine_batches_completados(batch_type);

-- 4. pine_configuracion_dificultad
CREATE TABLE IF NOT EXISTS pine_configuracion_dificultad (
  id SERIAL PRIMARY KEY,
  operacion TEXT NOT NULL,
  nivel int2 NOT NULL,
  min_operando_1 int4 NOT NULL,
  max_operando_1 int4 NOT NULL,
  min_operando_2 int4 NOT NULL,
  max_operando_2 int4 NOT NULL,
  max_resultado int4,
  tipo_respuesta TEXT NOT NULL,
  num_opciones int2,
  max_tiempo_segundos int4 NOT NULL,
  dificultad_score float4 NOT NULL,
  config_version int2 DEFAULT 1 NOT NULL,
  activa bool DEFAULT TRUE NOT NULL,
  created_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
  UNIQUE(operacion, nivel, config_version)
);

CREATE INDEX IF NOT EXISTS idx_config_dif_activa 
  ON pine_configuracion_dificultad(operacion, nivel, activa);

-- 5. pine_leaderboard_endless_mensual
CREATE TABLE IF NOT EXISTS pine_leaderboard_endless_mensual (
  id SERIAL PRIMARY KEY,
  user_ref TEXT NOT NULL,
  mes_id TEXT NOT NULL,
  mejor_streak int4 DEFAULT 0,
  total_intentos int4 DEFAULT 0,
  ranking int4,
  fecha_inicio date,
  fecha_fin date,
  created_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
  UNIQUE(user_ref, mes_id)
);

CREATE INDEX IF NOT EXISTS idx_endless_mes 
  ON pine_leaderboard_endless_mensual(mes_id, mejor_streak DESC);
CREATE INDEX IF NOT EXISTS idx_endless_ranking 
  ON pine_leaderboard_endless_mensual(mes_id, ranking);
CREATE INDEX IF NOT EXISTS idx_endless_user 
  ON pine_leaderboard_endless_mensual(user_ref, mes_id);

-- 6. pine_configuracion_sistema
CREATE TABLE IF NOT EXISTS pine_configuracion_sistema (
  config_key TEXT PRIMARY KEY,
  config_value JSONB NOT NULL,
  description TEXT,
  version int2 DEFAULT 1 NOT NULL,
  activa bool DEFAULT TRUE NOT NULL,
  created_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_config_sistema_activa 
  ON pine_configuracion_sistema(config_key, activa);

-- === POBLAR DATOS INICIALES ===

-- Configuración del sistema
INSERT INTO pine_configuracion_sistema (config_key, config_value, description) VALUES
('scoring.base_multiplier', '{"value": 5, "type": "integer"}', 'Multiplicador base: C × (value + d̄)'),
('scoring.participation_bonus', '{"value": 10, "type": "integer"}', 'Bonus por completar batch'),
('scoring.error_penalty', '{"value": 2, "type": "integer"}', 'Penalización por error'),
('streak.min_correct', '{"value": 4, "type": "integer"}', 'Mínimo de aciertos para contar streak'),
('streak.base_score', '{"value": 5, "type": "integer"}', 'Puntos base de streak'),
('streak.daily_multiplier', '{"value": 3, "type": "integer"}', 'Multiplicador por día'),
('streak.max_days', '{"value": 30, "type": "integer"}', 'Días máximos de streak'),
('practice_points.chest_interval', '{"value": 100, "type": "integer"}', 'PP para abrir cofre'),
('miniboss.min_batches_after_fail', '{"value": 3, "type": "integer"}', 'Batches mínimos tras fallo'),
('miniboss.min_correct_rate', '{"value": 0.8, "type": "float"}', 'Tasa de aciertos mínima (80%)'),
('miniboss.nivel_invisible_threshold', '{"value": 0.5, "type": "float"}', 'Diferencia mínima de nivel'),
('batch.size', '{"value": 10, "type": "integer"}', 'Ejercicios por batch'),
('batch.distribution_easy', '{"value": 2, "type": "integer"}', 'Ejercicios fáciles'),
('batch.distribution_central', '{"value": 6, "type": "integer"}', 'Ejercicios centrales'),
('batch.distribution_hard', '{"value": 2, "type": "integer"}', 'Ejercicios difíciles')
ON CONFLICT (config_key) DO NOTHING;

-- Configuración de dificultad por nivel (SUMA - Nivel 1-5)
INSERT INTO pine_configuracion_dificultad (operacion, nivel, min_operando_1, max_operando_1, min_operando_2, max_operando_2, max_resultado, tipo_respuesta, num_opciones, max_tiempo_segundos, dificultad_score, config_version, activa) VALUES
-- SUMA
('suma', 1, 0, 10, 0, 10, 20, 'multiple_choice', 4, 30, 1.0, 1, TRUE),
('suma', 2, 10, 50, 10, 50, 100, 'multiple_choice', 4, 45, 2.0, 1, TRUE),
('suma', 3, 50, 200, 50, 200, 400, 'multiple_choice', 4, 60, 3.0, 1, TRUE),
('suma', 4, 100, 500, 100, 500, 1000, 'abierta', NULL, 75, 4.0, 1, TRUE),
('suma', 5, 500, 2000, 500, 2000, 4000, 'abierta', NULL, 90, 5.0, 1, TRUE),

-- RESTA
('resta', 1, 0, 10, 0, 10, 10, 'multiple_choice', 4, 30, 1.0, 1, TRUE),
('resta', 2, 10, 50, 10, 50, 50, 'multiple_choice', 4, 45, 2.0, 1, TRUE),
('resta', 3, 50, 200, 50, 200, 200, 'multiple_choice', 4, 60, 3.0, 1, TRUE),
('resta', 4, 100, 500, 100, 500, 500, 'abierta', NULL, 75, 4.0, 1, TRUE),
('resta', 5, 500, 2000, 500, 2000, 2000, 'abierta', NULL, 90, 5.0, 1, TRUE),

-- MULTIPLICACIÓN
('mult', 1, 0, 10, 0, 10, 100, 'multiple_choice', 4, 30, 1.0, 1, TRUE),
('mult', 2, 2, 12, 2, 12, 144, 'multiple_choice', 4, 45, 2.0, 1, TRUE),
('mult', 3, 10, 20, 10, 20, 400, 'multiple_choice', 4, 60, 3.0, 1, TRUE),
('mult', 4, 10, 50, 10, 50, 2500, 'abierta', NULL, 75, 4.0, 1, TRUE),
('mult', 5, 50, 100, 50, 100, 10000, 'abierta', NULL, 90, 5.0, 1, TRUE),

-- DIVISIÓN
('div', 1, 2, 20, 2, 10, 10, 'multiple_choice', 4, 30, 1.0, 1, TRUE),
('div', 2, 10, 100, 2, 12, 50, 'multiple_choice', 4, 45, 2.0, 1, TRUE),
('div', 3, 50, 500, 5, 25, 100, 'multiple_choice', 4, 60, 3.0, 1, TRUE),
('div', 4, 100, 1000, 10, 50, 100, 'abierta', NULL, 75, 4.0, 1, TRUE),
('div', 5, 500, 5000, 10, 100, 500, 'abierta', NULL, 90, 5.0, 1, TRUE)
ON CONFLICT (operacion, nivel, config_version) DO NOTHING;
```

---

## 📊 RESUMEN DE CAMBIOS

### Modificaciones (3):
1. ✏️ `pine_user_operations` +3 campos
2. ✏️ `pine_user_gamification` +2 campos

### Nuevas tablas (4):
1. ➕ `pine_batches_completados` - Historial de batches
2. ➕ `pine_configuracion_dificultad` - Configuración de niveles
3. ➕ `pine_leaderboard_endless_mensual` - Ranking endless
4. ➕ `pine_configuracion_sistema` - Parámetros del sistema

### Total: 
- **2 tablas modificadas**
- **4 tablas nuevas**
- **Tablas existentes reutilizadas: 6**

---

## ✅ NEXT STEPS

1. **Ejecutar migración**: Correr el script `005_add_gamification_v2_fields.sql` en Roble
2. **Verificar tablas**: Confirmar que todas las tablas y columnas se crearon correctamente
3. **Inicializar datos**: Los usuarios existentes tendrán `nivel_invisible = 1.0` por default
4. **Actualizar plan**: Modificar `PLAN_GAMIFICATION_V2.md` con estas tablas exactas

---

**Última actualización**: 2025-12-05
