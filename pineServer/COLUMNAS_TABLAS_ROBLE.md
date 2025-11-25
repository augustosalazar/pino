# Columnas para las tablas PINE en Roble

## IMPORTANTE
- **NO crear** campo `_id` - Roble lo genera automáticamente
- **NO crear** campos de ID personalizados (user_id, session_id, profile_id, exercise_id, adjustment_id)
- **SÍ crear** campos de referencia (`user_ref`, `session_ref`) para las relaciones entre tablas

## Tipo de datos recomendado
- Usar **VARCHAR** en lugar de UUID para mejor compatibilidad con Roble

---

## Tabla: pine_users

**Columnas a crear:**
- `email` - VARCHAR
- `username` - VARCHAR  
- `current_score` - INTEGER (con default: 0)
- `created_at` - TIMESTAMP (opcional, con default: now())
- `updated_at` - TIMESTAMP (opcional, con default: now())

**NO incluir:** `_id` (auto-generado), `user_id`

---

## Tabla: pine_exercise_sessions

**Columnas a crear:**
- `user_ref` - VARCHAR (referencia al _id de pine_users)
- `started_at` - TIMESTAMP  
- `completed_at` - TIMESTAMP (nullable)
- `total_exercises` - INTEGER (default: 0)
- `correct_answers` - INTEGER (default: 0)
- `avg_difficulty` - NUMERIC
- `total_time_ms` - INTEGER
- `score_earned` - INTEGER (default: 0)

**NO incluir:** `_id` (auto-generado), `session_id`

---

## Tabla: pine_exercises

**Columnas a crear:**
- `session_ref` - VARCHAR (referencia al _id de pine_exercise_sessions)
- `user_ref` - VARCHAR (referencia al _id de pine_users)
- `exercise_type` - INTEGER (1 o 2)
- `operator` - VARCHAR ('+', '-', '*', '/')
- `operand_1` - INTEGER
- `operand_2` - INTEGER
- `correct_answer` - INTEGER
- `user_answer` - INTEGER (nullable)
- `options` - JSONB (nullable)
- `difficulty_level` - NUMERIC
- `is_correct` - BOOLEAN (nullable)
- `time_taken_ms` - INTEGER (nullable)
- `presented_at` - TIMESTAMP
- `answered_at` - TIMESTAMP (nullable)

**NO incluir:** `_id` (auto-generado), `exercise_id`

---

## Tabla: pine_user_difficulty_profile

**Columnas a crear:**
- `user_ref` - VARCHAR (referencia al _id de pine_users)
- `operator` - VARCHAR ('+', '-', '*', '/')
- `current_difficulty` - NUMERIC (default: 1.00)
- `success_rate` - NUMERIC (default: 0.00)
- `total_attempts` - INTEGER (default: 0)
- `total_correct` - INTEGER (default: 0)
- `updated_at` - TIMESTAMP

**NO incluir:** `_id` (auto-generado), `profile_id`

**CONSTRAINT:** Unique en (user_ref, operator) - si Roble lo soporta

---

## Tabla: pine_difficulty_adjustments

**Columnas a crear:**
- `user_ref` - VARCHAR (referencia al _id de pine_users)
- `session_ref` - VARCHAR (referencia al _id de pine_exercise_sessions, nullable)
- `operator` - VARCHAR ('+', '-', '*', '/')
- `previous_difficulty` - NUMERIC
- `new_difficulty` - NUMERIC
- `reason` - VARCHAR (nullable)
- `adjusted_at` - TIMESTAMP

**NO incluir:** `_id` (auto-generado), `adjustment_id`

---

## Resumen de cambios vs. diseño original

| Original | Nuevo |
|----------|-------|
| user_id (UUID) | _id (auto) |
| session_id (UUID) | _id (auto) |
| profile_id (UUID) | _id (auto) |
| exercise_id (UUID) | _id (auto) |
| adjustment_id (UUID) | _id (auto) |
| Foreign keys con UUID | user_ref, session_ref (VARCHAR) |

---

## Verificación después de crear las columnas

Ejecutar:
```bash
python test_database_v2.py
```

Este script:
1. Inserta un usuario (obtiene su _id)
2. Usa ese _id como `user_ref` en las demás tablas
3. Verifica que las relaciones funcionen correctamente
