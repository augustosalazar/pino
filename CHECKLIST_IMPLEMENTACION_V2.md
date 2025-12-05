# ✅ Checklist de Implementación V2

**Fecha inicio**: _________  
**Fecha objetivo**: _________

---

## 📋 FASE 1: Clases Base (Día 1)

### ConfigManager
- [ ] Crear `pineServer/v2/__init__.py`
- [ ] Crear `pineServer/v2/config_manager.py`
- [ ] Implementar `get_system_config(key)`
- [ ] Implementar `get_difficulty_config(op, nivel)`
- [ ] Implementar cache en memoria
- [ ] Crear `tests/test_config_manager.py`
- [ ] Test: Leer scoring.base_multiplier
- [ ] Test: Leer dificultad suma nivel 1
- [ ] Test: Cache funciona
- [ ] **CHECKPOINT**: Todas las configs se leen correctamente ✅

### Models
- [ ] Crear `pineServer/v2/models.py`
- [ ] Definir `Exercise` dataclass
- [ ] Definir `ExerciseResult` dataclass
- [ ] Definir `BatchResult` dataclass
- [ ] Definir `UserOperationState` dataclass
- [ ] **CHECKPOINT**: Models se pueden importar ✅

**Estimado**: 2-3 horas  
**Completado**: ___________

---

## 📋 FASE 2: Generadores (Día 2)

### ExerciseGenerator
- [ ] Crear `pineServer/v2/exercise_generator.py`
- [ ] Implementar `generate_exercise(op, nivel_invisible)`
- [ ] Implementar `_interpolate_operand_range(nivel_invisible, op)`
- [ ] Implementar `_generate_distractors(respuesta, num_opciones)`
- [ ] Manejar división exacta
- [ ] Test: Ejercicio nivel 1.0
- [ ] Test: Ejercicio nivel 2.5 (interpolación)
- [ ] Test: Ejercicio nivel 5.0
- [ ] Test: Distractores únicos y distintos
- [ ] **CHECKPOINT**: Ejercicios se generan con dificultad correcta ✅

### BatchGenerator
- [ ] Crear `pineServer/v2/batch_generator.py`
- [ ] Implementar `generate_batch(op, nivel_invisible)`
- [ ] Implementar distribución 2-6-2
- [ ] Leer config de `batch.distribution_*`
- [ ] Test: Batch tiene 10 ejercicios
- [ ] Test: Distribución correcta (2 fáciles, 6 medios, 2 difíciles)
- [ ] Test: Dificultades progresivas
- [ ] **CHECKPOINT**: Batches se generan correctamente ✅

**Estimado**: 3-4 horas  
**Completado**: ___________

---

## 📋 FASE 3: Evaluación (Día 3)

### PerformanceEvaluator
- [ ] Crear `pineServer/v2/performance_evaluator.py`
- [ ] Implementar `evaluate_performance(resultados, nivel_actual)`
- [ ] Implementar `_calculate_delta(success_rate)`
- [ ] Aplicar límites [1.0, 6.0]
- [ ] Test: 80% aciertos → sube 0.2
- [ ] Test: 40% aciertos → baja 0.1
- [ ] Test: 70% aciertos → sin cambio
- [ ] Test: No baja de 1.0
- [ ] Test: No sube de 6.0
- [ ] **CHECKPOINT**: Nivel invisible se ajusta correctamente ✅

### ScoringCalculator
- [ ] Crear `pineServer/v2/scoring_calculator.py`
- [ ] Implementar `calculate_score(ejercicios)`
- [ ] Implementar `calculate_pp(num_ejercicios)`
- [ ] Implementar `calculate_pd(num_correctos, op)`
- [ ] Implementar `calculate_xp(num_correctos)`
- [ ] Leer configs de `scoring.*`
- [ ] Test: Score con 10/10 correctos
- [ ] Test: Score con 5/10 correctos
- [ ] Test: Score con 0/10 correctos
- [ ] Test: PP, PD, XP correctos
- [ ] **CHECKPOINT**: Puntuación se calcula correctamente ✅

### DominioLevelManager
- [ ] Crear `pineServer/v2/dominio_level_manager.py`
- [ ] Implementar `get_nivel_dominio(nivel_invisible)`
- [ ] Implementar `detect_level_change(nivel_antes, nivel_despues)`
- [ ] Implementar `log_level_change(user_ref, op, nivel_nuevo)`
- [ ] Test: Mapeo 1.0-1.9 → nivel 1
- [ ] Test: Mapeo 2.0-2.9 → nivel 2
- [ ] Test: Detectar cambio 1.9 → 2.1
- [ ] Test: No detectar cambio 2.1 → 2.3
- [ ] **CHECKPOINT**: Nivel dominio funciona ✅

**Estimado**: 3-4 horas  
**Completado**: ___________

---

## 📋 FASE 4: Miniboss (Día 4)

### MinibossDetector
- [ ] Crear `pineServer/v2/miniboss_detector.py`
- [ ] Implementar `is_miniboss_candidate(user_ref, op)`
- [ ] Verificar `batches_desde_ultimo_miniboss >= min`
- [ ] Verificar `nivel_invisible >= nivel_dominio + threshold`
- [ ] Verificar `miniboss_fallos_consecutivos < 3`
- [ ] Leer configs de `miniboss.*`
- [ ] Test: Candidato válido
- [ ] Test: No candidato (pocos batches)
- [ ] Test: No candidato (nivel bajo)
- [ ] Test: No candidato (3 fallos)
- [ ] **CHECKPOINT**: Detección de candidatos funciona ✅

### MinibossEvaluator
- [ ] Crear `pineServer/v2/miniboss_evaluator.py`
- [ ] Implementar `generate_miniboss_batch(op, nivel_siguiente)`
- [ ] Implementar `evaluate_miniboss(user_ref, resultados)`
- [ ] Implementar `update_on_success(user_ref, op, nuevo_nivel)`
- [ ] Implementar `update_on_failure(user_ref, op)`
- [ ] Registrar en `pine_mini_jefes_intentos`
- [ ] Test: Generar batch nivel siguiente
- [ ] Test: Evaluar aprobación (>= 80%)
- [ ] Test: Evaluar fallo (< 80%)
- [ ] Test: Actualizar contadores
- [ ] **CHECKPOINT**: Miniboss funciona end-to-end ✅

**Estimado**: 3-4 horas  
**Completado**: ___________

---

## 📋 FASE 5: Persistencia (Día 5)

### BatchRecorder
- [ ] Crear `pineServer/v2/batch_recorder.py`
- [ ] Implementar `record_batch(batch_result)`
- [ ] Serializar ejercicios a JSONB
- [ ] Implementar `update_user_operations(user_ref, op, updates)`
- [ ] Implementar `update_user_gamification(user_ref, pp, pd, xp)`
- [ ] Test: Insertar batch completo
- [ ] Test: Actualizar pine_user_operations
- [ ] Test: Actualizar pine_user_gamification
- [ ] Test: Verificar JSONB de ejercicios
- [ ] **CHECKPOINT**: Datos se guardan correctamente ✅

**Estimado**: 2-3 horas  
**Completado**: ___________

---

## 📋 FASE 6: Integración Start Session (Día 6)

### Modificar `/api/sessions/start`
- [ ] Backup código actual
- [ ] Leer `nivel_invisible` de pine_user_operations
- [ ] Importar componentes V2
- [ ] Detectar miniboss con `MinibossDetector`
- [ ] Generar batch con `BatchGenerator` o `MinibossEvaluator`
- [ ] Agregar `is_miniboss` a respuesta
- [ ] Agregar `nivel_invisible` a respuesta
- [ ] Test manual: Start session normal
- [ ] Test manual: Start session miniboss
- [ ] **CHECKPOINT**: Start session funciona con V2 ✅

**Estimado**: 2-3 horas  
**Completado**: ___________

---

## 📋 FASE 7: Integración Complete Session (Día 7)

### Modificar `/api/sessions/complete`
- [ ] Backup código actual
- [ ] Usar `PerformanceEvaluator` para nivel invisible
- [ ] Usar `ScoringCalculator` para puntuación
- [ ] Usar `DominioLevelManager` para nivel dominio
- [ ] Evaluar miniboss si aplica
- [ ] Usar `BatchRecorder` para guardar
- [ ] Actualizar `batches_desde_ultimo_miniboss`
- [ ] Retornar todos los datos necesarios
- [ ] Test manual: Complete session normal
- [ ] Test manual: Complete session miniboss aprobado
- [ ] Test manual: Complete session miniboss fallido
- [ ] **CHECKPOINT**: Complete session funciona con V2 ✅

**Estimado**: 3-4 horas  
**Completado**: ___________

---

## 📋 FASE 8: Testing E2E (Día 8)

### Escenarios de Testing
- [ ] Crear `test_v2_integration.py`
- [ ] Test: Usuario nuevo completa 5 batches
- [ ] Test: Usuario sube de nivel dominio
- [ ] Test: Usuario candidato → miniboss → aprueba
- [ ] Test: Usuario candidato → miniboss → falla 3 veces
- [ ] Test: Usuario con bajo rendimiento (nivel baja)
- [ ] Test: Verificar pine_batches_completados
- [ ] Test: Verificar pine_user_operations actualizado
- [ ] Test: Verificar pine_user_gamification actualizado
- [ ] Test: Verificar pine_mini_jefes_intentos
- [ ] **CHECKPOINT**: Todos los escenarios pasan ✅

**Estimado**: 3-4 horas  
**Completado**: ___________

---

## 📋 FASE 9: Feature Flag y Deploy (Día 9-10)

### Feature Flag
- [ ] Agregar env var `USE_GAMIFICATION_V2`
- [ ] Implementar switch en start_session
- [ ] Implementar switch en complete_session
- [ ] Test: V2 habilitado funciona
- [ ] Test: V2 deshabilitado usa legacy
- [ ] **CHECKPOINT**: Feature flag funciona ✅

### Migración de Usuarios
- [ ] Crear `migrate_users_to_v2.py`
- [ ] Calcular nivel_invisible desde nivel_dominio
- [ ] Inicializar contadores de miniboss
- [ ] Dry-run en staging
- [ ] Ejecutar en producción
- [ ] Verificar usuarios migrados
- [ ] **CHECKPOINT**: Usuarios migrados ✅

### Deploy
- [ ] Deploy a staging
- [ ] Probar con usuario de prueba
- [ ] Verificar logs (sin errores)
- [ ] Verificar performance (< 100ms)
- [ ] Habilitar V2 para 10% usuarios
- [ ] Monitorear 24h
- [ ] Habilitar V2 para 50% usuarios
- [ ] Monitorear 24h
- [ ] Habilitar V2 para 100% usuarios
- [ ] **CHECKPOINT**: V2 en producción ✅

**Estimado**: 4-6 horas  
**Completado**: ___________

---

## 🎯 CRITERIOS DE ÉXITO FINAL

- [ ] ✅ Todos los tests unitarios pasan
- [ ] ✅ Todos los tests de integración pasan
- [ ] ✅ Performance aceptable (< 100ms avg)
- [ ] ✅ Sin errores en logs de producción
- [ ] ✅ Frontend funciona sin cambios
- [ ] ✅ Métricas muestran mejora vs V1

---

## 📊 TRACKING DE TIEMPO

| Fase | Estimado | Real | Diferencia |
|------|----------|------|------------|
| Fase 1 | 2-3h | ___ | ___ |
| Fase 2 | 3-4h | ___ | ___ |
| Fase 3 | 3-4h | ___ | ___ |
| Fase 4 | 3-4h | ___ | ___ |
| Fase 5 | 2-3h | ___ | ___ |
| Fase 6 | 2-3h | ___ | ___ |
| Fase 7 | 3-4h | ___ | ___ |
| Fase 8 | 3-4h | ___ | ___ |
| Fase 9 | 4-6h | ___ | ___ |
| **TOTAL** | **25-35h** | ___ | ___ |

---

## 🐛 ISSUES ENCONTRADOS

| # | Descripción | Solución | Status |
|---|-------------|----------|--------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

---

**Firma**: ___________  
**Fecha completado**: ___________
