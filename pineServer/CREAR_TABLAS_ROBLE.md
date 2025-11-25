# INSTRUCCIONES PARA CREAR TABLAS EN ROBLE

## IMPORTANTE: Las tablas NO existen actualmente

El script de inspección confirmó que las tablas `pino_*` **NO existen** en Roble.

Debes crearlas manualmente usando la interfaz web de Roble.

## Formato observado en Roble

Basado en la tabla `company_id_user` que existe, Roble:
- Crea automáticamente un campo `_id` (string, PRIMARY KEY)
- Usa los tipos especificados para las demás columnas
- NO necesitas incluir `_id` al insertar (se genera automáticamente)

## Tablas a crear (con prefijo pino_)

### 1. Tabla: pino_users

**Columnas TO DEFINE en Roble:**
- `user_id` - UUID
- `email` - VARCHAR (unique)
- `username` - VARCHAR
- `current_score` - INTEGER (default: 0)
- `created_at` - TIMESTAMP WITH TIME ZONE
- `updated_at` - TIMESTAMP WITH TIME ZONE

NO incluyas `_id` - Roble lo crea automáticamente.

---

### 2. Tabla: pino_exercise_sessions

**Columnas a definir:**
- `session_id` - UUID
- `user_id` - UUID
- `started_at` - TIMESTAMP WITH TIME ZONE
- `completed_at` - TIMESTAMP WITH TIME ZONE (nullable)
- `total_exercises` - INTEGER (default: 0)
- `correct_answers` - INTEGER (default: 0)
- `avg_difficulty` - NUMERIC
- `total_time_ms` - INTEGER
- `score_earned` - INTEGER (default: 0)

---

### 3. Tabla: pino_exercises

**Columnas a definir:**
- `exercise_id` - UUID
- `session_id` - UUID
- `user_id` - UUID
- `exercise_type` - SMALLINT
- `operator` - VARCHAR
- `operand_1` - INTEGER
- `operand_2` - INTEGER
- `correct_answer` - INTEGER
- `user_answer` - INTEGER (nullable)
- `options` - JSONB (nullable)
- `difficulty_level` - NUMERIC
- `is_correct` - BOOLEAN (nullable)
- `time_taken_ms` - INTEGER (nullable)
- `presented_at` - TIMESTAMP WITH TIME ZONE
- `answered_at` - TIMESTAMP WITH TIME ZONE (nullable)

---

### 4. Tabla: pino_user_difficulty_profile

**Columnas a definir:**
- `profile_id` - UUID
- `user_id` - UUID
- `operator` - VARCHAR
- `current_difficulty` - NUMERIC (default: 1.00)
- `success_rate` - NUMERIC (default: 0.00)
- `total_attempts` - INTEGER (default: 0)
- `total_correct` - INTEGER (default: 0)
- `updated_at` - TIMESTAMP WITH TIME ZONE

---

### 5. Tabla: pino_difficulty_adjustments

**Columnas a definir:**
- `adjustment_id` - UUID
- `user_id` - UUID
- `session_id` - UUID (nullable)
- `operator` - VARCHAR
- `previous_difficulty` - NUMERIC
- `new_difficulty` - NUMERIC
- `reason` - VARCHAR (nullable)
- `adjusted_at` - TIMESTAMP WITH TIME ZONE

---

## Pasos para crear en Roble:

1. Accede a la interfaz web de Roble
2. Ve a tu proyecto: `tracking_7d2ad2db74`
3. Para cada tabla:
   - Haz clic en "Create Table" o "Nueva Tabla"
   - Ingresa el nombre (ej: `pino_users`)
   - Agrega cada columna con su tipo
   - **NO agregues** el campo `_id` (se crea automáticamente)
   - Guarda la tabla

4. Después de crear todas las tablas, ejecuta:
   ```bash
   python inspect_tables.py
   ```
   Para verificar que existen.

5. Luego ejecuta:
   ```bash
   python test_database.py
   ```
   Para probar inserts y queries.

---

## Tipos de datos en Roble (referencia)

| Tipo SQL | Tipo Roble |
|----------|------------|
| UUID | uuid |
| VARCHAR | varchar |
| INTEGER | int4 |
| SMALLINT | int2 |
| NUMERIC | numeric |
| BOOLEAN | bool |
| JSONB | jsonb |
| TIMESTAMP WITH TIME ZONE | timestamptz |

---

## Ejemplo de inserción (después de crear tablas)

Una vez creadas las tablas, el formato de inserción será:

```python
# NO incluir _id ni timestamps con default
record = {
    "user_id": "uuid-string",
    "email": "test@test.com",
    "username": "Test User",
    "current_score": 0
    # Roble agregará automáticamente: _id, created_at, updated_at
}
```
