# 📋 Plan de Implementación - Gamificación V2 (Backend)

**Fecha**: 2025-12-05  
**Estado**: ✅ Tablas creadas, configuración cargada  
**Siguiente**: Implementar lógica de negocio

---

## 🎯 OBJETIVO

Reemplazar el sistema de gamificación actual con un motor más robusto y flexible que usa **nivel invisible**, **configuraciones dinámicas** y **tracking detallado**.

---

## ✅ YA TENEMOS (Completado)

- ✅ Tablas V2 creadas y verificadas
- ✅ Campos nuevos agregados a tablas existentes
- ✅ Configuraciones del sistema (15 registros)
- ✅ Configuraciones de dificultad (20 registros)
- ✅ Endpoints de testing funcionando
- ✅ Inicialización automática al arrancar servidor

---

## 🚀 PLAN DE IMPLEMENTACIÓN

### **FASE 1: Clases Base y Configuración** (1-2 horas)

#### Paso 1.1: Crear ConfigManager
**Archivo**: `pineServer/v2/config_manager.py`

**Funcionalidad**:
- Leer configuraciones de `pine_configuracion_sistema`
- Leer configuraciones de `pine_configuracion_dificultad`
- Cache en memoria para performance
- Métodos helper para acceder a configs

**Métodos clave**:
```python
get_system_config(key: str) -> Any
get_difficulty_config(operacion: str, nivel: int) -> Dict
get_scoring_config() -> Dict
get_batch_config() -> Dict
```

**Testing**: Crear `test_config_manager.py` que verifique lectura de configs

---

#### Paso 1.2: Crear clases de dominio
**Archivo**: `pineServer/v2/models.py`

**Clases**:
```python
@dataclass
class Exercise:
    operand_1: int
    operand_2: int
    operacion: str
    respuesta_correcta: float
    dificultad: float
    tipo_respuesta: str
    opciones: Optional[List[int]]

@dataclass
class BatchResult:
    user_ref: str
    operacion: str
    ejercicios: List[ExerciseResult]
    nivel_invisible_antes: float
    nivel_invisible_despues: float
    score_ganado: int
    pp_ganados: int
    pd_ganados: int
```

**Testing**: No requiere testing aún (solo definiciones)

---

### **FASE 2: Generador de Ejercicios** (2-3 horas)

#### Paso 2.1: Crear ExerciseGenerator V2
**Archivo**: `pineServer/v2/exercise_generator.py`

**Funcionalidad**:
- Generar ejercicio basado en nivel invisible (float)
- Usar configuraciones de `pine_configuracion_dificultad`
- Interpolar entre niveles (ej: nivel 2.3 usa 30% de nivel 2 y 70% de nivel 3)
- Generar opciones incorrectas inteligentes

**Métodos clave**:
```python
generate_exercise(operacion: str, nivel_invisible: float) -> Exercise
_interpolate_operand_range(nivel_invisible: float, operacion: str) -> Tuple[int, int]
_generate_distractors(respuesta: int, num_opciones: int) -> List[int]
```

**Testing**: 
- Verificar que ejercicios estén en rango correcto
- Verificar interpolación entre niveles
- Probar con niveles extremos (1.0, 6.0)

---

#### Paso 2.2: Crear BatchGenerator V2
**Archivo**: `pineServer/v2/batch_generator.py`

**Funcionalidad**:
- Generar batch de 10 ejercicios con distribución 2-6-2
- 2 fáciles (nivel_invisible - 0.5)
- 6 centrales (nivel_invisible)
- 2 difíciles (nivel_invisible + 0.5)
- Usar config de `batch.distribution_*`

**Métodos clave**:
```python
generate_batch(user_ref: str, operacion: str, nivel_invisible: float) -> List[Exercise]
```

**Testing**:
- Verificar distribución correcta
- Verificar que dificultades sean progresivas

---

### **FASE 3: Evaluación y Ajuste** (2-3 horas)

#### Paso 3.1: Crear PerformanceEvaluator
**Archivo**: `pineServer/v2/performance_evaluator.py`

**Funcionalidad**:
- Calcular nueva nivel invisible basado en resultados
- Fórmula: `Δnivel = 0.2 × (aciertos% - 0.7) / 0.3`
- Si aciertos >= 80%: sube 0.2
- Si aciertos < 40%: baja 0.1
- Limitar entre 1.0 y 6.0

**Métodos clave**:
```python
evaluate_performance(ejercicios: List[ExerciseResult], 
                    nivel_invisible_actual: float) -> float
calculate_delta(success_rate: float) -> float
```

**Testing**:
- Verificar ajustes con diferentes tasas de acierto
- Verificar límites (no bajar de 1.0, no subir de 6.0)

---

#### Paso 3.2: Crear ScoringCalculator
**Archivo**: `pineServer/v2/scoring_calculator.py`

**Funcionalidad**:
- Calcular score según fórmula V2
- `Score = Σ(C × (base_multiplier + d̄)) + bonus - penalty`
- Usar configs de `scoring.*`

**Métodos clave**:
```python
calculate_score(ejercicios: List[ExerciseResult]) -> int
calculate_pp(num_ejercicios: int) -> int
calculate_pd(num_correctos: int, operacion: str) -> int
calculate_xp(num_correctos: int) -> int
```

**Testing**:
- Verificar cálculos con diferentes escenarios
- Comparar con resultados esperados

---

### **FASE 4: Lógica de Nivel Dominio** (1-2 horas)

#### Paso 4.1: Crear DominioLevelManager
**Archivo**: `pineServer/v2/dominio_level_manager.py`

**Funcionalidad**:
- Determinar nivel dominio (1-5) desde nivel invisible
- Nivel 1: 1.0-1.9, Nivel 2: 2.0-2.9, etc.
- Detectar cambios de nivel
- Registrar en `pine_nivel_dominio_log`

**Métodos clave**:
```python
get_nivel_dominio(nivel_invisible: float) -> int
detect_level_change(nivel_antes: float, nivel_despues: float) -> Optional[int]
log_level_change(user_ref: str, operacion: str, nivel_nuevo: int)
```

**Testing**:
- Verificar mapeo correcto
- Verificar detección de cambios

---

### **FASE 5: Sistema de Miniboss** (2-3 horas)

#### Paso 5.1: Crear MinibossDetector
**Archivo**: `pineServer/v2/miniboss_detector.py`

**Funcionalidad**:
- Determinar si usuario es candidato a miniboss
- Condiciones:
  - `batches_desde_ultimo_miniboss >= min_batches_after_fail`
  - `nivel_invisible >= nivel_dominio + threshold`
  - No ha fallado 3 veces consecutivas
- Usar configs de `miniboss.*`

**Métodos clave**:
```python
is_miniboss_candidate(user_ref: str, operacion: str) -> bool
get_miniboss_config(operacion: str, nivel_dominio: int) -> Dict
```

**Testing**:
- Verificar condiciones
- Probar edge cases

---

#### Paso 5.2: Crear MinibossEvaluator
**Archivo**: `pineServer/v2/miniboss_evaluator.py`

**Funcionalidad**:
- Generar batch de miniboss (10 ejercicios del siguiente nivel)
- Evaluar si aprobó (>= 80% aciertos)
- Actualizar nivel dominio si aprobó
- Registrar intento en `pine_mini_jefes_intentos`

**Métodos clave**:
```python
generate_miniboss_batch(operacion: str, nivel_siguiente: int) -> List[Exercise]
evaluate_miniboss(user_ref: str, resultados: List[ExerciseResult]) -> bool
update_on_success(user_ref: str, operacion: str, nuevo_nivel: int)
update_on_failure(user_ref: str, operacion: str)
```

**Testing**:
- Simular aprobación y fallo
- Verificar actualización de contadores

---

### **FASE 6: Tracking y Persistencia** (1-2 horas)

#### Paso 6.1: Crear BatchRecorder
**Archivo**: `pineServer/v2/batch_recorder.py`

**Funcionalidad**:
- Guardar batch completo en `pine_batches_completados`
- Serializar ejercicios a JSONB
- Actualizar `pine_user_operations` con nuevos valores
- Actualizar `pine_user_gamification` con PP, PD, XP

**Métodos clave**:
```python
record_batch(batch_result: BatchResult) -> int
update_user_operations(user_ref: str, operacion: str, updates: Dict)
update_user_gamification(user_ref: str, pp: int, pd: int, xp: int)
```

**Testing**:
- Verificar inserción correcta
- Verificar actualización de totales

---

### **FASE 7: Integración con Endpoints** (2-3 horas)

#### Paso 7.1: Modificar `/api/sessions/start`
**Archivo**: `pineServer/main.py`

**Cambios**:
1. Leer `nivel_invisible` en lugar de usar dificultad legacy
2. Usar `BatchGenerator` V2
3. Detectar si es candidato a miniboss
4. Retornar flag `is_miniboss` en respuesta

**Pseudocódigo**:
```python
@app.post("/api/sessions/start")
async def start_session_v2(request: StartSessionRequest):
    # 1. Get user operations
    operations = get_user_operations(user_ref)
    
    # 2. Check miniboss candidacy
    is_miniboss = miniboss_detector.is_miniboss_candidate(...)
    
    # 3. Generate batch
    if is_miniboss:
        exercises = miniboss_evaluator.generate_miniboss_batch(...)
    else:
        exercises = batch_generator.generate_batch(...)
    
    # 4. Return session
    return {
        "session_id": ...,
        "exercises": exercises,
        "is_miniboss": is_miniboss
    }
```

---

#### Paso 7.2: Modificar `/api/sessions/complete`
**Archivo**: `pineServer/main.py`

**Cambios**:
1. Usar `PerformanceEvaluator` V2 para nivel invisible
2. Usar `ScoringCalculator` V2 para puntuación
3. Actualizar nivel dominio si cambió
4. Si era miniboss, evaluar resultado
5. Guardar en `pine_batches_completados`

**Pseudocódigo**:
```python
@app.post("/api/sessions/complete")
async def complete_session_v2(request: CompleteSessionRequest):
    # 1. Get current state
    operation = get_user_operation(user_ref, operacion)
    nivel_invisible_actual = operation['nivel_invisible']
    
    # 2. Evaluate performance
    nivel_nuevo = evaluator.evaluate_performance(...)
    score = scoring.calculate_score(...)
    
    # 3. Check level change
    nivel_dominio_nuevo = level_manager.detect_level_change(...)
    
    # 4. If miniboss, evaluate
    if is_miniboss:
        aprobado = miniboss_evaluator.evaluate_miniboss(...)
        if aprobado:
            nivel_dominio_nuevo += 1
    
    # 5. Record batch
    batch_recorder.record_batch(...)
    
    # 6. Return results
    return {
        "score": score,
        "nivel_invisible": nivel_nuevo,
        "nivel_dominio": nivel_dominio_nuevo,
        "level_up": nivel_dominio_nuevo > nivel_dominio_actual,
        ...
    }
```

---

### **FASE 8: Testing End-to-End** (2-3 horas)

#### Paso 8.1: Crear flujo de testing completo
**Archivo**: `test_v2_integration.py`

**Escenarios**:
1. Usuario nuevo → batch normal → progresión
2. Usuario candidato → miniboss → aprobación
3. Usuario candidato → miniboss → fallo
4. Ascenso de nivel dominio
5. Bajo rendimiento → ajuste hacia abajo

**Testing**:
- Ejecutar cada escenario
- Verificar estado final en BD
- Verificar logs y tracking

---

#### Paso 8.2: Verificar compatibilidad con frontend
**Tareas**:
- Verificar que respuestas del backend sean compatibles con frontend actual
- Agregar campos opcionales para no romper código existente
- Documentar nuevos campos disponibles

---

### **FASE 9: Migración Gradual** (1-2 horas)

#### Paso 9.1: Feature flag para V2
**Archivo**: `pineServer/main.py`

**Implementación**:
```python
USE_GAMIFICATION_V2 = os.getenv("USE_GAMIFICATION_V2", "false").lower() == "true"

if USE_GAMIFICATION_V2:
    # Usar lógica V2
else:
    # Usar lógica legacy
```

**Beneficio**: Poder alternar entre V1 y V2 sin cambiar código

---

#### Paso 9.2: Migración de usuarios existentes
**Script**: `migrate_users_to_v2.py`

**Funcionalidad**:
- Para cada usuario:
  - Calcular `nivel_invisible` desde `nivel_dominio`
  - Inicializar `batches_desde_ultimo_miniboss = 0`
  - Inicializar `miniboss_fallos_consecutivos = 0`
  - Preservar progreso actual

---

## 📊 ORDEN RECOMENDADO DE IMPLEMENTACIÓN

```
Día 1: FASES 1-2
├─ ConfigManager
├─ Models
├─ ExerciseGenerator
└─ BatchGenerator

Día 2: FASES 3-4
├─ PerformanceEvaluator
├─ ScoringCalculator
└─ DominioLevelManager

Día 3: FASE 5
├─ MinibossDetector
└─ MinibossEvaluator

Día 4: FASES 6-7
├─ BatchRecorder
├─ Modificar start_session
└─ Modificar complete_session

Día 5: FASES 8-9
├─ Testing E2E
├─ Feature flag
└─ Migración de usuarios
```

---

## 🎯 CRITERIOS DE ÉXITO

### Por Fase:
- **Fase 1**: Configs se leen correctamente desde BD
- **Fase 2**: Ejercicios generados con dificultad correcta
- **Fase 3**: Nivel invisible se ajusta según desempeño
- **Fase 4**: Nivel dominio se actualiza correctamente
- **Fase 5**: Miniboss se detecta y evalúa correctamente
- **Fase 6**: Batches se guardan con toda la información
- **Fase 7**: Endpoints funcionan end-to-end
- **Fase 8**: Todos los escenarios pasan
- **Fase 9**: V2 funciona en producción sin errores

### General:
- ✅ Todos los tests unitarios pasan
- ✅ Tests de integración pasan
- ✅ Performance aceptable (< 100ms por batch)
- ✅ Sin errores en logs
- ✅ Frontend funciona sin cambios

---

## 📝 NOTAS IMPORTANTES

### Compatibilidad con Legacy:
- Mantener endpoints existentes funcionando
- No eliminar tabla `pine_user_difficulty_profile` todavía
- Agregar campos nuevos como opcionales en respuestas

### Performance:
- Cachear configuraciones en memoria
- Usar conexión pool para BD
- Batch insert donde sea posible

### Seguridad:
- Validar todos los inputs
- No confiar en datos del cliente
- Recalcular todo en servidor

### Logging:
- Log de cada cambio de nivel
- Log de cada miniboss attempt
- Log de errores con contexto completo

---

## 🔧 HERRAMIENTAS ÚTILES

### Durante desarrollo:
- `check_v2_tables.py` - Verificar estado de tablas
- `test_insert_config.py` - Probar inserción de configs
- Endpoints `/api/v2/test/*` - Testing manual

### Debugging:
- Logs del servidor con nivel DEBUG
- Queries directas a Roble para verificar estado
- Postman/curl para probar endpoints

---

## ❓ DECISIONES PENDIENTES

1. **¿Cómo manejar endless mode?**
   - ¿Generar usando nivel invisible del usuario?
   - ¿O nivel fijo por tipo de endless?

2. **¿Streak se mantiene igual?**
   - ¿Usar misma lógica que V1?
   - ¿O modificar con configs de `streak.*`?

3. **¿Migración gradual o completa?**
   - ¿Feature flag por usuario?
   - ¿O switch global?

4. **¿Mantener compatibilidad con V1?**
   - ¿Por cuánto tiempo?
   - ¿Deprecar endpoints viejos?

---

**Última actualización**: 2025-12-05  
**Estado**: Listo para comenzar implementación
