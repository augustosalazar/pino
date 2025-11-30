# 📊 Esquema de Base de Datos - Sistema de Gamificación (v3.0 - NORMALIZADO)

## 🎯 Decisión de Diseño: Normalización Completa

**Estructura de 3 tablas separadas:**

1. **`pine_user_gamification`** - Estado global del jugador (PP, PD global, XP, nivel, racha)
2. **`pine_user_operations`** - Progreso por operación (suma, resta, mult, div)
3. **Tablas auxiliares** - Sessions, records, pending_items, leaderboard, etc.

### Ventajas vs. Diseño Anterior

| Aspecto | v2.0 (Campos por operación) | v3.0 (Tabla normalizada) |
|---------|----------------------------|--------------------------|
| **Normalización** | ❌ Campos repetidos (pd_suma, pd_resta...) | ✅ Tabla normalizada |
| **Escalabilidad** | ❌ ALTER TABLE para nueva operación | ✅ Simple INSERT |
| **Queries** | ❌ 4 campos separados | ✅ WHERE operacion = ? |
| **Estadísticas** | ❌ Queries complejas | ✅ GROUP BY operacion |
| **Mantenibilidad** | ⚠️ Mediana | ✅ Excelente |

---

## 1. Tabla: `pine_user_gamification`

Contiene el **estado global** del jugador (sin datos específicos de operaciones):

```sql
CREATE TABLE pine_user_gamification (
  user_ref TEXT PRIMARY KEY REFERENCES pine_users(user_ref) ON DELETE CASCADE,
  
  -- === PUNTOS DE PRÁCTICA (PP) ===
  pp_total INTEGER DEFAULT 0 NOT NULL,
  pp_dia INTEGER DEFAULT 0 NOT NULL,
  pp_semana INTEGER DEFAULT 0 NOT NULL,
  pp_dia_max INTEGER DEFAULT 30 NOT NULL,
  pp_ultima_fecha DATE,
  
  -- === PUNTOS DE DOMINIO GLOBALES ===
  pd_global INTEGER DEFAULT 0 NOT NULL,
  pd_semana INTEGER DEFAULT 0 NOT NULL,
  
  -- === EXPERIENCIA Y NIVEL DEL JUGADOR ===
  xp_total INTEGER DEFAULT 0 NOT NULL,
  nivel_jugador INTEGER DEFAULT 1 NOT NULL,
  
  -- === RACHA DIARIA ===
  racha_dias INTEGER DEFAULT 0 NOT NULL,
  racha_ultima_fecha DATE,
  
  -- === DESBLOQUEOS DE MODOS DE JUEGO ===
  -- (Modos que requieren múltiples operaciones)
  unlocked_mix_suma_resta BOOLEAN DEFAULT FALSE NOT NULL,
  unlocked_mix_mult_div BOOLEAN DEFAULT FALSE NOT NULL,
  unlocked_speed BOOLEAN DEFAULT FALSE NOT NULL,
  unlocked_bosses BOOLEAN DEFAULT FALSE NOT NULL,
  unlocked_elite BOOLEAN DEFAULT FALSE NOT NULL,
  unlocked_master BOOLEAN DEFAULT FALSE NOT NULL,
  
  -- === TIMESTAMPS ===
  semana_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```

---

## 2. Tabla: `pine_user_operations` (NUEVA - CLAVE)

Contiene el **progreso por operación** (normalizado):

```sql
CREATE TABLE pine_user_operations (
  id SERIAL PRIMARY KEY,
  user_ref TEXT NOT NULL REFERENCES pine_users(user_ref) ON DELETE CASCADE,
  operacion TEXT NOT NULL CHECK (operacion IN ('suma', 'resta', 'mult', 'div')),
  
  -- === PUNTOS DE DOMINIO POR OPERACIÓN ===
  pd_operacion INTEGER DEFAULT 0 NOT NULL,
  
  -- === NIVEL DE DOMINIO (calculado desde pd_operacion) ===
  -- Nivel 1-5 según rangos de PD
  nivel_dominio INTEGER DEFAULT 1 NOT NULL,
  
  -- === DESBLOQUEO ===
  unlocked BOOLEAN DEFAULT FALSE NOT NULL,
  
  -- === MINI-JEFE ===
  miniboss_completed BOOLEAN DEFAULT FALSE NOT NULL,
  miniboss_attempts INTEGER DEFAULT 0 NOT NULL,
  miniboss_last_attempt TIMESTAMP,
  
  -- === ESTADÍSTICAS ADICIONALES ===
  total_ejercicios INTEGER DEFAULT 0 NOT NULL,
  total_correctos INTEGER DEFAULT 0 NOT NULL,
  
  -- === TIMESTAMPS ===
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  
  -- Constraint: un registro por usuario-operación
  UNIQUE(user_ref, operacion)
);

-- Índices
CREATE INDEX idx_user_operations_user ON pine_user_operations(user_ref);
CREATE INDEX idx_user_operations_operacion ON pine_user_operations(user_ref, operacion);
CREATE INDEX idx_user_operations_unlocked ON pine_user_operations(unlocked);
CREATE INDEX idx_user_operations_pd ON pine_user_operations(pd_operacion DESC);
```

### Inicialización Automática

Al crear un perfil de gamificación, se crean automáticamente las 4 operaciones:

```sql
CREATE OR REPLACE FUNCTION crear_operaciones_iniciales()
RETURNS TRIGGER AS $$
BEGIN
  -- Crear las 4 operaciones base
  INSERT INTO pine_user_operations (user_ref, operacion, unlocked)
  VALUES 
    (NEW.user_ref, 'suma', TRUE),   -- SUMA siempre desbloqueada
    (NEW.user_ref, 'resta', FALSE),
    (NEW.user_ref, 'mult', FALSE),
    (NEW.user_ref, 'div', FALSE)
  ON CONFLICT (user_ref, operacion) DO NOTHING;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_crear_operaciones
AFTER INSERT ON pine_user_gamification
FOR EACH ROW
EXECUTE FUNCTION crear_operaciones_iniciales();
```

---

## 3. Consultas Comunes

### Obtener nivel de una operación

```sql
SELECT nivel_dominio, pd_operacion, unlocked
FROM pine_user_operations
WHERE user_ref = 'user123' AND operacion = 'suma';
```

### Obtener todas las operaciones de un usuario

```sql
SELECT 
  operacion,
  pd_operacion,
  nivel_dominio,
  unlocked,
  miniboss_completed
FROM pine_user_operations
WHERE user_ref = 'user123'
ORDER BY operacion;
```

### Actualizar PD de una operación

```sql
UPDATE pine_user_operations
SET 
  pd_operacion = pd_operacion + 10,
  total_ejercicios = total_ejercicios + 1,
  total_correctos = total_correctos + 1,
  updated_at = CURRENT_TIMESTAMP
WHERE user_ref = 'user123' AND operacion = 'suma';
```

### Desbloquear operación

```sql
UPDATE pine_user_operations
SET 
  unlocked = TRUE,
  updated_at = CURRENT_TIMESTAMP
WHERE user_ref = 'user123' AND operacion = 'resta';
```

---

## 4. Vista: `pine_user_complete_profile` (ACTUALIZADA)

```sql
CREATE OR REPLACE VIEW pine_user_complete_profile AS
SELECT 
  -- Datos básicos
  u.user_ref,
  u.email,
  u.username,
  u.age,
  u.grade,
  u.institution_name,
  
  -- Gamificación global
  g.pp_total,
  g.pp_dia,
  g.pp_semana,
  g.pd_global,
  g.pd_semana,
  g.xp_total,
  g.nivel_jugador,
  g.racha_dias,
  
  -- Operaciones (como JSON o campos individuales)
  (SELECT json_agg(
    json_build_object(
      'operacion', operacion,
      'pd', pd_operacion,
      'nivel', nivel_dominio,
      'unlocked', unlocked,
      'miniboss_completed', miniboss_completed
    )
  ) FROM pine_user_operations WHERE user_ref = u.user_ref) as operaciones,
  
  -- O campos individuales (para compatibilidad)
  (SELECT pd_operacion FROM pine_user_operations WHERE user_ref = u.user_ref AND operacion = 'suma') as pd_suma,
  (SELECT pd_operacion FROM pine_user_operations WHERE user_ref = u.user_ref AND operacion = 'resta') as pd_resta,
  (SELECT pd_operacion FROM pine_user_operations WHERE user_ref = u.user_ref AND operacion = 'mult') as pd_mult,
  (SELECT pd_operacion FROM pine_user_operations WHERE user_ref = u.user_ref AND operacion = 'div') as pd_div,
  
  (SELECT nivel_dominio FROM pine_user_operations WHERE user_ref = u.user_ref AND operacion = 'suma') as nivel_suma,
  (SELECT nivel_dominio FROM pine_user_operations WHERE user_ref = u.user_ref AND operacion = 'resta') as nivel_resta,
  (SELECT nivel_dominio FROM pine_user_operations WHERE user_ref = u.user_ref AND operacion = 'mult') as nivel_mult,
  (SELECT nivel_dominio FROM pine_user_operations WHERE user_ref = u.user_ref AND operacion = 'div') as nivel_div,
  
  -- Modos
  g.unlocked_mix_suma_resta,
  g.unlocked_mix_mult_div,
  g.unlocked_speed,
  g.unlocked_bosses,
  g.unlocked_elite,
  g.unlocked_master
  
FROM pine_users u
LEFT JOIN pine_user_gamification g ON u.user_ref = g.user_ref;
```

---

## 5. Trigger: Actualizar Nivel de Dominio Automáticamente

```sql
CREATE OR REPLACE FUNCTION trigger_actualizar_nivel_dominio()
RETURNS TRIGGER AS $$
DECLARE
  nivel_anterior INTEGER;
  nivel_nuevo INTEGER;
BEGIN
  -- Calcular nivel desde PD
  nivel_nuevo := obtener_nivel_dominio(NEW.pd_operacion);
  nivel_anterior := OLD.nivel_dominio;
  
  -- Actualizar nivel
  NEW.nivel_dominio := nivel_nuevo;
  NEW.updated_at := CURRENT_TIMESTAMP;
  
  -- Si cambió de nivel, registrar en log
  IF nivel_nuevo != nivel_anterior THEN
    INSERT INTO pine_nivel_dominio_log (
      user_ref, 
      operacion, 
      nivel_anterior, 
      nivel_nuevo, 
      pd_operacion
    )
    VALUES (NEW.user_ref, NEW.operacion, nivel_anterior, nivel_nuevo, NEW.pd_operacion);
    
    RAISE NOTICE 'Usuario %: % nivel % → %', 
                  NEW.user_ref, NEW.operacion, nivel_anterior, nivel_nuevo;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER actualizar_nivel_dominio
BEFORE UPDATE OF pd_operacion ON pine_user_operations
FOR EACH ROW
EXECUTE FUNCTION trigger_actualizar_nivel_dominio();
```

---

## 6. Comparación de Estructuras

### Antes (v2.0 - Campos separados)
```sql
pine_user_gamification (
  pd_suma,
  pd_resta,
  pd_mult,
  pd_div,
  unlocked_suma,
  unlocked_resta,
  unlocked_mult,
  unlocked_div,
  miniboss_suma_completed,
  miniboss_mult_completed,
  miniboss_div_completed
  -- 11 campos solo para operaciones
)
```

### Ahora (v3.0 - Normalizado)
```sql
pine_user_gamification (
  -- Solo datos globales (PP, PD global, XP, nivel, racha)
  -- NO incluye datos por operación
  -- 15 campos total
)

pine_user_operations (
  user_ref,
  operacion,  -- 'suma', 'resta', 'mult', 'div'
  pd_operacion,
  nivel_dominio,
  unlocked,
  miniboss_completed,
  total_ejercicios,
  total_correctos
  -- 4 registros por usuario (uno por operación)
)
```

---

## 7. Ventajas del Nuevo Diseño

### ✅ Escalabilidad
```sql
-- Agregar nueva operación: solo INSERT
INSERT INTO pine_user_operations (user_ref, operacion, unlocked)
SELECT user_ref, 'potencias', FALSE FROM pine_users;

-- vs. Antes: ALTER TABLE con nuevos campos
ALTER TABLE pine_user_gamification
  ADD COLUMN pd_potencias INTEGER DEFAULT 0,
  ADD COLUMN unlocked_potencias BOOLEAN DEFAULT FALSE,
  ADD COLUMN miniboss_potencias_completed BOOLEAN DEFAULT FALSE;
```

### ✅ Queries más Simples
```sql
-- Top operación más practicada
SELECT operacion, SUM(pd_operacion) as total_pd
FROM pine_user_operations
GROUP BY operacion
ORDER BY total_pd DESC;

-- Usuarios que dominan una operación específica
SELECT u.username, o.pd_operacion
FROM pine_user_operations o
JOIN pine_users u ON o.user_ref = u.user_ref
WHERE o.operacion = 'mult' AND o.nivel_dominio >= 4;
```

### ✅ Actualizaciones Uniformes
```typescript
// Una función para cualquier operación
async function actualizarPDOperacion(userRef: string, operacion: string, pdGanados: number) {
  return supabase
    .from('pine_user_operations')
    .update({ pd_operacion: supabase.raw(`pd_operacion + ${pdGanados}`) })
    .eq('user_ref', userRef)
    .eq('operacion', operacion);
}
```

### ✅ Estadísticas Poderosas
```sql
-- Distribución de niveles por operación
SELECT 
  operacion,
  nivel_dominio,
  COUNT(*) as cantidad_usuarios
FROM pine_user_operations
GROUP BY operacion, nivel_dominio
ORDER BY operacion, nivel_dominio;

-- Promedio de PD por institución y operación
SELECT 
  u.institution_name,
  o.operacion,
  AVG(o.pd_operacion) as pd_promedio
FROM pine_user_operations o
JOIN pine_users u ON o.user_ref = u.user_ref
GROUP BY u.institution_name, o.operacion;
```

---

## 8. Metadata de Operaciones (Opcional)

Si quieres metadata de las operaciones (nombre, descripción, orden):

```sql
CREATE TABLE pine_operations_catalog (
  operacion TEXT PRIMARY KEY,
  nombre_display TEXT NOT NULL,
  descripcion TEXT,
  orden INTEGER NOT NULL,
  icono TEXT,
  color TEXT,
  activa BOOLEAN DEFAULT TRUE
);

INSERT INTO pine_operations_catalog VALUES
  ('suma', 'Suma', 'Operación de adición', 1, 'add', '#34C759', TRUE),
  ('resta', 'Resta', 'Operación de sustracción', 2, 'remove', '#FF9500', TRUE),
  ('mult', 'Multiplicación', 'Operación de multiplicación', 3, 'close', '#007AFF', TRUE),
  ('div', 'División', 'Operación de división', 4, 'slash', '#AF52DE', TRUE);
```

---

## ✅ Resumen de Cambios

| Tabla | Cambio |
|-------|--------|
| `pine_user_gamification` | Removidos campos por operación, solo datos globales |
| `pine_user_operations` | **NUEVA** - Tabla normalizada para operaciones |
| Vistas | Actualizadas para JOIN con pine_user_operations |
| Triggers | Actualización de nivel automática por operación |
| Functions | Simplificadas gracias a normalización |

---

¿Procedo a actualizar todos los scripts SQL con este diseño normalizado?
