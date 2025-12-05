# 🎮 Gamificación V2 - Resumen de Testing

**Fecha**: 2025-12-05  
**Estado**: ✅ Endpoints de testing listos

---

## 📦 ARCHIVOS CREADOS

### 1. Endpoints de Testing
**Archivo**: `pineServer/gamification_v2_test_endpoints.py`
- ✅ 10 endpoints para probar tablas nuevas
- ✅ Verificación de tablas y campos
- ✅ CRUD de configuraciones
- ✅ Creación de batches de prueba
- ✅ Consultas de datos de usuario

### 2. Script de Migración SQL
**Archivo**: `pineServer/database_migrations/005_add_gamification_v2_fields.sql`
- ✅ Modificación de 2 tablas existentes
- ✅ Creación de 4 tablas nuevas
- ✅ Población de datos iniciales
- ✅ Configuración completa de niveles 1-5

### 3. Script de Ejecución
**Archivo**: `pineServer/database_migrations/run_migration_005.py`
- ✅ Ejecuta la migración
- ✅ Verifica que todo esté correcto
- ✅ Reporta errores

### 4. Documentación
**Archivos**:
- `TABLAS_MODIFICACIONES_V2.md` - Detalle de cambios en BD
- `GUIA_TESTING_V2_ENDPOINTS.md` - Guía de uso de endpoints
- `RESUMEN_TESTING_V2.md` - Este archivo

---

## 🏗️ CAMBIOS EN LA BASE DE DATOS

### Tablas Modificadas (2):

#### `pine_user_operations`
```sql
+ nivel_invisible FLOAT4 DEFAULT 1.0
+ batches_desde_ultimo_miniboss INT4 DEFAULT 0
+ miniboss_fallos_consecutivos INT4 DEFAULT 0
```

#### `pine_user_gamification`
```sql
+ racha_maxima INT4 DEFAULT 0
+ dias_validos_streak INT4 DEFAULT 0
```

### Tablas Nuevas (4):

1. **`pine_batches_completados`** - Historial de batches
   - Guarda todos los batches con detalles completos
   - Incluye ejercicios_data como JSONB
   - Tracking de nivel invisible antes/después

2. **`pine_configuracion_dificultad`** - Config de niveles
   - Parámetros por operación y nivel
   - Rangos de operandos configurables
   - Soporte para A/B testing (config_version)

3. **`pine_leaderboard_endless_mensual`** - Ranking endless
   - Tabla de clasificación para modo endless
   - Tracking mensual de mejor streak

4. **`pine_configuracion_sistema`** - Configuración global
   - Parámetros del sistema (puntuación, streak, etc.)
   - Valores en JSONB para flexibilidad
   - 15 configuraciones iniciales

---

## 🚀 PASOS PARA PROBAR

### Paso 1: Ejecutar Migración

**Opción A - Manual** (Ejecutar SQL directo en Roble):
```bash
# Copiar el contenido de 005_add_gamification_v2_fields.sql
# Pegarlo y ejecutarlo en el editor SQL de Roble
```

**Opción B - Script Python** (Necesita ajuste para Roble):
```bash
cd pineServer/database_migrations
python run_migration_005.py
```

> ⚠️ **NOTA**: El script Python necesita un método para ejecutar SQL en roble_client.
> Por ahora, usa la Opción A (manual).

---

### Paso 2: Iniciar el Servidor

```bash
cd pineServer
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

### Paso 3: Verificar Tablas

```bash
curl http://localhost:8000/api/v2/test/verify/tables
```

**Respuesta esperada**:
```json
{
  "status": "verification_complete",
  "tables": {
    "pine_batches_completados": {"exists": true, "count": 0},
    "pine_configuracion_dificultad": {"exists": true, "count": 20},
    "pine_configuracion_sistema": {"exists": true, "count": 15},
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

### Paso 4: Verificar Configuración del Sistema

```bash
curl http://localhost:8000/api/v2/test/config/system
```

Deberías ver **15 configuraciones** incluyendo:
- `scoring.base_multiplier`
- `streak.min_correct`
- `miniboss.min_batches_after_fail`
- etc.

---

### Paso 5: Verificar Configuración de Dificultad

```bash
# Nivel 1 de suma
curl http://localhost:8000/api/v2/test/config/difficulty/suma/1

# Nivel 5 de multiplicación
curl http://localhost:8000/api/v2/test/config/difficulty/mult/5
```

Deberías ver configuraciones para **20 niveles** (4 operaciones × 5 niveles).

---

### Paso 6: Probar con Usuario Real

```bash
# Obtener operaciones de un usuario
curl http://localhost:8000/api/v2/test/user/TU_USER_ID/operations

# Ver perfil de gamificación
curl http://localhost:8000/api/v2/test/user/TU_USER_ID/gamification
```

---

### Paso 7: Crear Batch de Prueba

```bash
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
```

---

### Paso 8: Ver Historial de Batches

```bash
curl http://localhost:8000/api/v2/test/user/TU_USER_ID/batches?limit=10
```

---

## 📊 ENDPOINTS DISPONIBLES

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v2/test/verify/tables` | GET | Verifica tablas y campos |
| `/api/v2/test/config/system` | GET | Configuración del sistema |
| `/api/v2/test/config/difficulty/{op}/{nivel}` | GET | Config de dificultad |
| `/api/v2/test/operations/update-nivel-invisible` | POST | Actualiza nivel invisible |
| `/api/v2/test/batches/create` | POST | Crea batch de prueba |
| `/api/v2/test/config/difficulty/add` | POST | Agrega config personalizada |
| `/api/v2/test/user/{user_ref}/operations` | GET | Operaciones del usuario |
| `/api/v2/test/user/{user_ref}/batches` | GET | Historial de batches |
| `/api/v2/test/user/{user_ref}/gamification` | GET | Perfil de gamificación |
| `/api/v2/test/stats/batches` | GET | Estadísticas globales |

---

## ✅ CHECKLIST DE VERIFICACIÓN

- [ ] Migración ejecutada sin errores
- [ ] Servidor iniciado correctamente
- [ ] Endpoint `/verify/tables` retorna `exists: true` para todas las tablas
- [ ] pine_user_operations tiene los 3 campos nuevos
- [ ] pine_user_gamification tiene los 2 campos nuevos
- [ ] pine_configuracion_sistema tiene 15 registros
- [ ] pine_configuracion_dificultad tiene 20 registros (4 ops × 5 niveles)
- [ ] Se puede crear un batch de prueba
- [ ] Se puede consultar el historial de batches
- [ ] Se puede actualizar nivel_invisible

---

## 🐛 TROUBLESHOOTING

### Error: "Module not found: gamification_v2_test_endpoints"
```
Solución: Asegúrate de estar en el directorio pineServer al iniciar el servidor
cd pineServer
uvicorn main:app --reload
```

### Error: "Table does not exist"
```
Solución: Ejecuta la migración 005_add_gamification_v2_fields.sql en Roble
```

### Error: "User operation not found"
```
Solución: El usuario debe tener un perfil de gamificación creado primero.
Usa los endpoints existentes (/api/users/ensure) para crear el perfil.
```

### Error al crear batch: "Operation not found"
```
Solución: Verifica que el user_ref y la operación existan en pine_user_operations
```

---

## 📝 PRÓXIMOS PASOS

Una vez que los endpoints de testing funcionen correctamente:

1. **Implementar lógica real** (Fase 1 del plan):
   - Clases base (Operation, Exercise, Batch)
   - ConfigManager para leer configuraciones
   - ExerciseGenerator

2. **Generadores de batches** (Fase 2):
   - RegularBatchGenerator
   - MinibossBatchGenerator
   - EndlessBatchGenerator

3. **Sistema de evaluación** (Fase 3):
   - Evaluator
   - InvisibleLevelUpdater
   - MinibossDetector

4. **Endpoints de producción** (Fase 6):
   - `/api/v2/batch/start`
   - `/api/v2/batch/submit`
   - `/api/v2/progress/{user_id}`

---

## 📚 DOCUMENTACIÓN COMPLETA

Para más detalles, consulta:

- **`TABLAS_MODIFICACIONES_V2.md`** - Esquema de BD completo
- **`GUIA_TESTING_V2_ENDPOINTS.md`** - Ejemplos detallados de cada endpoint
- **`PLAN_GAMIFICATION_V2.md`** - Plan completo de implementación

---

**Última actualización**: 2025-12-05  
**Estado**: ✅ Listo para pruebas
