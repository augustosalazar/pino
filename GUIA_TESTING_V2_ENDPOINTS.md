# Guía de Testing - Endpoints de Gamificación V2

**Fecha**: 2025-12-05  
**Base URL**: `http://localhost:8000/api/v2/test`

---

## 📋 ENDPOINTS DISPONIBLES

### 1. Verificación de Tablas

#### `GET /api/v2/test/verify/tables`
Verifica que todas las tablas nuevas existan y tengan los campos correctos.

**Ejemplo**:
```bash
curl http://localhost:8000/api/v2/test/verify/tables
```

**Respuesta esperada**:
```json
{
  "status": "verification_complete",
  "tables": {
    "pine_batches_completados": {
      "exists": true,
      "count": 0
    },
    "pine_configuracion_dificultad": {
      "exists": true,
      "count": 20
    },
    "pine_user_operations": {
      "exists": true,
      "has_nivel_invisible": true,
      "has_batches_desde_ultimo_miniboss": true,
      "has_miniboss_fallos_consecutivos": true
    },
    "pine_user_gamification": {
      "exists": true,
      "has_racha_maxima": true,
      "has_dias_validos_streak": true
    }
  }
}
```

---

### 2. Configuración del Sistema

#### `GET /api/v2/test/config/system`
Obtiene toda la configuración del sistema.

**Ejemplo**:
```bash
curl http://localhost:8000/api/v2/test/config/system
```

**Respuesta esperada**:
```json
{
  "status": "success",
  "count": 14,
  "config": [
    {
      "config_key": "scoring.base_multiplier",
      "config_value": {"value": 5, "type": "integer"},
      "description": "Multiplicador base: C × (value + d̄)"
    },
    ...
  ]
}
```

---

### 3. Configuración de Dificultad

#### `GET /api/v2/test/config/difficulty/{operacion}/{nivel}`
Obtiene la configuración de dificultad para una operación y nivel específicos.

**Ejemplo**:
```bash
# Obtener config de suma nivel 1
curl http://localhost:8000/api/v2/test/config/difficulty/suma/1

# Obtener config de multiplicación nivel 3
curl http://localhost:8000/api/v2/test/config/difficulty/mult/3
```

**Respuesta esperada**:
```json
{
  "status": "success",
  "config": {
    "operacion": "suma",
    "nivel": 1,
    "min_operando_1": 0,
    "max_operando_1": 10,
    "min_operando_2": 0,
    "max_operando_2": 10,
    "max_resultado": 20,
    "tipo_respuesta": "multiple_choice",
    "num_opciones": 4,
    "max_tiempo_segundos": 30,
    "dificultad_score": 1.0
  }
}
```

---

### 4. Actualizar Nivel Invisible

#### `POST /api/v2/test/operations/update-nivel-invisible`
Actualiza el nivel invisible de una operación para un usuario.

**Body**:
```json
{
  "user_ref": "USER_ID_AQUI",
  "operacion": "suma",
  "nivel_invisible": 2.5
}
```

**Ejemplo con curl**:
```bash
curl -X POST http://localhost:8000/api/v2/test/operations/update-nivel-invisible \
  -H "Content-Type: application/json" \
  -d '{
    "user_ref": "tu-user-id",
    "operacion": "suma",
    "nivel_invisible": 2.5
  }'
```

**Respuesta esperada**:
```json
{
  "status": "updated",
  "operation": {
    "operacion": "suma",
    "nivel_dominio": 1,
    "nivel_invisible": 2.5,
    "pd_operacion": 15,
    "unlocked": true
  }
}
```

---

### 5. Crear Batch de Prueba

#### `POST /api/v2/test/batches/create`
Crea un batch de prueba en `pine_batches_completados`.

**Body**:
```json
{
  "user_ref": "USER_ID_AQUI",
  "operacion": "suma",
  "batch_type": "regular",
  "nivel_central": 2,
  "ejercicios_correctos": 8,
  "total_ejercicios": 10
}
```

**Tipos de batch disponibles**:
- `"regular"` - Batch normal
- `"miniboss"` - Batch de mini-jefe
- `"endless"` - Batch de modo endless

**Ejemplo con curl**:
```bash
curl -X POST http://localhost:8000/api/v2/test/batches/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_ref": "tu-user-id",
    "operacion": "suma",
    "batch_type": "regular",
    "nivel_central": 2,
    "ejercicios_correctos": 8,
    "total_ejercicios": 10
  }'
```

**Respuesta esperada**:
```json
{
  "status": "created",
  "batch": {
    "id": 123,
    "user_ref": "tu-user-id",
    "batch_type": "regular",
    "operacion": "suma",
    "nivel_central": 2,
    "score_ganado": 58
  },
  "score_ganado": 58,
  "nivel_invisible_change": 0.2
}
```

---

### 6. Agregar Configuración de Dificultad

#### `POST /api/v2/test/config/difficulty/add`
Agrega una nueva configuración de dificultad personalizada.

**Body**:
```json
{
  "operacion": "suma",
  "nivel": 6,
  "min_operando_1": 1000,
  "max_operando_1": 5000,
  "min_operando_2": 1000,
  "max_operando_2": 5000,
  "max_resultado": 10000,
  "tipo_respuesta": "abierta",
  "num_opciones": null,
  "max_tiempo_segundos": 120,
  "dificultad_score": 6.0
}
```

**Ejemplo con curl**:
```bash
curl -X POST http://localhost:8000/api/v2/test/config/difficulty/add \
  -H "Content-Type: application/json" \
  -d '{
    "operacion": "suma",
    "nivel": 6,
    "min_operando_1": 1000,
    "max_operando_1": 5000,
    "min_operando_2": 1000,
    "max_operando_2": 5000,
    "max_resultado": 10000,
    "tipo_respuesta": "abierta",
    "max_tiempo_segundos": 120,
    "dificultad_score": 6.0
  }'
```

---

### 7. Consultar Operaciones de Usuario

#### `GET /api/v2/test/user/{user_ref}/operations`
Obtiene todas las operaciones de un usuario con los nuevos campos.

**Ejemplo**:
```bash
curl http://localhost:8000/api/v2/test/user/tu-user-id/operations
```

**Respuesta esperada**:
```json
{
  "status": "success",
  "user_ref": "tu-user-id",
  "count": 4,
  "operations": [
    {
      "operacion": "suma",
      "nivel_dominio": 2,
      "nivel_invisible": 2.3,
      "pd_operacion": 25,
      "unlocked": true,
      "miniboss_completed": false,
      "miniboss_attempts": 1,
      "batches_desde_ultimo_miniboss": 5,
      "miniboss_fallos_consecutivos": 1,
      "total_ejercicios": 150,
      "total_correctos": 120
    },
    ...
  ]
}
```

---

### 8. Consultar Batches de Usuario

#### `GET /api/v2/test/user/{user_ref}/batches?limit=10`
Obtiene el historial de batches completados por el usuario.

**Parámetros**:
- `limit` (opcional): Número de batches a retornar (default: 10)

**Ejemplo**:
```bash
# Últimos 10 batches
curl http://localhost:8000/api/v2/test/user/tu-user-id/batches

# Últimos 20 batches
curl http://localhost:8000/api/v2/test/user/tu-user-id/batches?limit=20
```

**Respuesta esperada**:
```json
{
  "status": "success",
  "user_ref": "tu-user-id",
  "count": 5,
  "batches": [
    {
      "id": 123,
      "batch_type": "regular",
      "operacion": "suma",
      "nivel_central": 2,
      "nivel_invisible_antes": 2.1,
      "nivel_invisible_despues": 2.3,
      "ejercicios_correctos": "8/10",
      "score_ganado": 58,
      "pp_ganados": 10,
      "miniboss_aprobado": null,
      "endless_streak": null,
      "completado_en": "2025-12-05T16:30:00Z"
    },
    ...
  ]
}
```

---

### 9. Consultar Perfil de Gamificación

#### `GET /api/v2/test/user/{user_ref}/gamification`
Obtiene el perfil de gamificación con los nuevos campos.

**Ejemplo**:
```bash
curl http://localhost:8000/api/v2/test/user/tu-user-id/gamification
```

**Respuesta esperada**:
```json
{
  "status": "success",
  "user_ref": "tu-user-id",
  "profile": {
    "pp_total": 250,
    "pd_global": 120,
    "xp_total": 1500,
    "nivel_jugador": 5,
    "racha_dias": 7,
    "racha_maxima": 15,
    "dias_validos_streak": 25,
    "racha_ultima_fecha": "2025-12-05"
  }
}
```

---

### 10. Estadísticas de Batches

#### `GET /api/v2/test/stats/batches`
Obtiene estadísticas generales de todos los batches completados.

**Ejemplo**:
```bash
curl http://localhost:8000/api/v2/test/stats/batches
```

**Respuesta esperada**:
```json
{
  "status": "success",
  "total_batches": 145,
  "by_type": {
    "regular": 120,
    "miniboss": 20,
    "endless": 5
  },
  "by_operation": {
    "suma": 80,
    "resta": 40,
    "mult": 20,
    "div": 5
  }
}
```

---

## 🧪 FLUJO DE PRUEBAS RECOMENDADO

### Paso 1: Verificar Tablas
```bash
curl http://localhost:8000/api/v2/test/verify/tables
```

### Paso 2: Verificar Configuración del Sistema
```bash
curl http://localhost:8000/api/v2/test/config/system
```

### Paso 3: Verificar Configuración de Dificultad
```bash
# Probar cada operación y nivel
curl http://localhost:8000/api/v2/test/config/difficulty/suma/1
curl http://localhost:8000/api/v2/test/config/difficulty/suma/5
curl http://localhost:8000/api/v2/test/config/difficulty/mult/3
```

### Paso 4: Obtener ID de Usuario
```bash
# Usa un user_ref existente de tu base de datos
# Por ejemplo, el que se obtiene al hacer login
```

### Paso 5: Consultar Estado Actual
```bash
curl http://localhost:8000/api/v2/test/user/TU_USER_ID/operations
curl http://localhost:8000/api/v2/test/user/TU_USER_ID/gamification
```

### Paso 6: Actualizar Nivel Invisible
```bash
curl -X POST http://localhost:8000/api/v2/test/operations/update-nivel-invisible \
  -H "Content-Type: application/json" \
  -d '{
    "user_ref": "TU_USER_ID",
    "operacion": "suma",
    "nivel_invisible": 2.5
  }'
```

### Paso 7: Crear Batches de Prueba
```bash
# Batch regular exitoso
curl -X POST http://localhost:8000/api/v2/test/batches/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_ref": "TU_USER_ID",
    "operacion": "suma",
    "batch_type": "regular",
    "nivel_central": 2,
    "ejercicios_correctos": 8,
    "total_ejercicios": 10
  }'

# Batch miniboss aprobado
curl -X POST http://localhost:8000/api/v2/test/batches/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_ref": "TU_USER_ID",
    "operacion": "suma",
    "batch_type": "miniboss",
    "nivel_central": 3,
    "ejercicios_correctos": 9,
    "total_ejercicios": 10
  }'

# Batch endless
curl -X POST http://localhost:8000/api/v2/test/batches/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_ref": "TU_USER_ID",
    "operacion": "mult",
    "batch_type": "endless",
    "nivel_central": 2,
    "ejercicios_correctos": 15,
    "total_ejercicios": 15
  }'
```

### Paso 8: Verificar Historial
```bash
curl http://localhost:8000/api/v2/test/user/TU_USER_ID/batches?limit=20
```

### Paso 9: Verificar Estadísticas Globales
```bash
curl http://localhost:8000/api/v2/test/stats/batches
```

---

## 📊 CASOS DE USO PARA PROBAR

### Caso 1: Progresión Normal
1. Usuario empieza con nivel_invisible = 1.0
2. Completa varios batches regulares con 7-8/10 aciertos
3. Nivel invisible sube gradualmente: 1.0 → 1.2 → 1.4 → 1.6
4. Al llegar a 1.5, es candidato para miniboss

### Caso 2: Ascenso de Nivel
1. Usuario en nivel_dominio = 1, nivel_invisible = 1.6
2. Completa miniboss con 9/10 aciertos
3. Sube a nivel_dominio = 2
4. Nivel invisible se ajusta

### Caso 3: Bajo Rendimiento
1. Usuario completa batch con 3/10 aciertos
2. Nivel invisible baja: 2.0 → 1.9
3. Siguiente batch tiene ejercicios más fáciles

### Caso 4: Racha Diaria
1. Usuario completa batch con 4+ aciertos
2. racha_dias incrementa
3. dias_validos_streak incrementa
4. racha_maxima se actualiza si supera el récord

---

## 🔧 TROUBLESHOOTING

### Error: "Table not found"
```
Solución: Ejecutar el script de migración 005_add_gamification_v2_fields.sql
```

### Error: "User operation not found"
```
Solución: El usuario debe tener operaciones creadas primero.
Usar los endpoints existentes para crear el perfil de gamificación.
```

### Error: "duplicate key value violates unique constraint"
```
Solución: Ya existe una configuración para esa operación/nivel.
Usar un nivel diferente o modificar la existente.
```

---

## 📝 NOTAS IMPORTANTES

1. **Datos de Prueba**: Estos endpoints solo deben usarse en desarrollo
2. **User Ref**: Necesitas un user_ref válido existente en la BD
3. **Migración**: Asegúrate de ejecutar la migración antes de probar
4. **Configuración**: La configuración del sistema se pobla automáticamente al crear las tablas

---

**Última actualización**: 2025-12-05
