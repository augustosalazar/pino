# 📋 Plan de Implementación - Sistema de Gamificación

## Estado Actual
✅ Base de datos migrada y verificada en Roble
✅ Tablas creadas: `pine_user_gamification`, `pine_user_operations`, `pine_pending_items`, etc.
✅ Script de verificación funcionando

## Fases de Implementación

---

## FASE 1: Lógica Core de Gamificación ✅ COMPLETADA

### Step 1.1: Crear módulo de cálculos de gamificación ✅ COMPLETADO
**Archivo:** `gamification_core.py`
**Contenido:**
- ✅ Funciones puras para cálculo de XP
- ✅ Funciones para cálculo de niveles de jugador
- ✅ Funciones para cálculo de niveles de dominio por operación
- ✅ Constantes del sistema

**Entregables:**
```python
# Funciones creadas:
✅ calcular_pd_ejercicio(fue_primer_intento, es_correcto)
✅ calcular_bonus_batch(porcentaje_acierto)
✅ calcular_nivel_dominio(pd_operacion)
✅ calcular_xp_batch(correctos, dificultad_media)
✅ calcular_nivel_jugador(xp_total)
✅ calcular_pd_levelup(nivel)
✅ verificar_levelup(xp_anterior, xp_nueva)
✅ verificar_desbloqueo_resta/mult/div()
✅ verificar_desbloqueos_modos()
✅ calcular_score_semanal()
✅ debe_repetirse_item()
```

### Step 1.2: Crear módulo de gestión de perfil de usuario ✅ COMPLETADO
**Archivo:** `gamification_profile.py`
**Contenido:**
- ✅ Inicializar perfil de gamificación para usuario nuevo
- ✅ Inicializar operaciones para usuario
- ✅ Obtener estado completo de gamificación
- ✅ Actualizar PP, PD, XP

**Entregables:**
```python
# Funciones creadas:
✅ crear_perfil_gamificacion(user_ref)
✅ inicializar_operaciones(user_ref)
✅ inicializar_perfil_completo(user_ref)
✅ obtener_perfil_gamificacion(user_ref)
✅ obtener_operaciones_usuario(user_ref)
✅ obtener_operacion(user_ref, operacion)
✅ obtener_perfil_completo(user_ref)
✅ actualizar_pp(user_ref, cantidad)
✅ actualizar_pd(user_ref, pd_global, pd_operacion, operacion)
✅ actualizar_xp(user_ref, xp)
✅ actualizar_racha(user_ref, incrementar)
✅ incrementar_estadisticas_operacion()
✅ resetear_pp_dia(user_ref)
✅ resetear_semana(user_ref)
```

### Step 1.3: Crear módulo de desbloqueos ✅ COMPLETADO
**Archivo:** `gamification_unlocks.py`
**Contenido:**
- ✅ Verificar condiciones de desbloqueo de operaciones
- ✅ Verificar condiciones de desbloqueo de modos
- ✅ Actualizar flags de desbloqueo

**Entregables:**
```python
# Funciones creadas:
✅ verificar_y_desbloquear_operaciones(user_ref)
✅ desbloquear_operacion(user_ref, operacion)
✅ marcar_minijefe_completado(user_ref, operacion)
✅ registrar_intento_minijefe(user_ref, operacion)
✅ verificar_y_actualizar_modos(user_ref)
✅ obtener_modos_disponibles(user_ref)
✅ obtener_operaciones_disponibles(user_ref)
✅ puede_realizar_operacion(user_ref, operacion)
✅ obtener_progreso_desbloqueos(user_ref)
```

### Step 1.4: Crear módulo de procesamiento de batch ✅ COMPLETADO
**Archivo:** `gamification_batch.py`
**Contenido:**
- ✅ Procesar resultados de un batch completo
- ✅ Calcular bonificaciones
- ✅ Gestionar items pendientes
- ✅ Gestionar racha diaria

**Entregables:**
```python
# Funciones creadas:
✅ procesar_batch_completo(user_ref, resultados_items, operacion)
✅ gestionar_items_pendientes(user_ref, items_fallados)
✅ obtener_items_pendientes(user_ref, operacion, limite)
✅ marcar_item_pendiente_completado(user_ref, exercise_ref)
✅ verificar_y_actualizar_racha(user_ref)
✅ obtener_estadisticas_batch(user_ref)
```

---

## FASE 2: Integración con Endpoints ✅ COMPLETADA

### Step 2.1: Actualizar endpoint de inicio de sesión ✅ COMPLETADO
- ✅ Verificar/crear perfil de gamificación al hacer login
- ✅ Devolver estado de gamificación en respuesta

**Implementado en:** `/api/users/ensure`
- Inicializa perfil para usuarios nuevos
- Obtiene perfil para usuarios existentes
- Retorna perfil completo en respuesta

### Step 2.2: Actualizar endpoint de inicio de batch ✅ COMPLETADO
- ✅ Incluir items pendientes en el batch
- ⚠️ Ajustar dificultad según nivel de dominio (parcial)

**Implementado en:** `/api/sessions/start`
- Lee items pendientes de todas las operaciones
- Ajusta cantidad de ejercicios nuevos
- **TODO:** Convertir pending_items en Exercises

### Step 2.3: Actualizar endpoint de finalización de batch ✅ COMPLETADO
- ✅ Llamar a `procesar_batch_completo()`
- ✅ Calcular y devolver recompensas
-✅ Verificar level ups
- ✅ Verificar desbloqueos

**Implementado en:** `/api/sessions/{session_id}/complete`
- Procesa gamificación completa después de guardar resultados
- Mapea operadores a nombres en español
- Determina operación principal automáticamente
- Retorna objeto `gamification` completo

### Step 2.4: Crear endpoint de estado de gamificación ✅ COMPLETADO
- ✅ Obtener perfil completo
- ✅ Devolver progreso por operación
- ✅ Devolver desbloqueos actuales

**Implementado en:** `/api/users/{user_ref}/gamification` (GET)
- Retorna perfil completo
- Retorna operaciones con niveles
- Retorna modos disponibles
- Retorna progreso hacia desbloqueos

---

## FASE 3: Mini-jefes y Modos Especiales (Pendiente)

### Step 3.1: Crear módulo de mini-jefes
- Generar batch de mini-jefe según tipo
- Validar completitud de mini-jefe
- Registrar intentos

### Step 3.2: Endpoints de mini-jefes
- Iniciar mini-jefe
- Completar mini-jefe
- Consultar progreso de mini-jefes

---

## FASE 4: Leaderboard y Reseteos (Siguiente Sesión)

### Step 4.1: Sistema de score semanal
- Calcular score semanal
- Endpoint de leaderboard

### Step 4.2: Tareas programadas
- Reset diario de PP_dia
- Reset semanal de PP_semana y PD_semana
- Verificación de rachas

---

## FASE 5: Testing y Refinamiento (Siguiente Sesión)

### Step 5.1: Tests unitarios
- Tests de cálculos core
- Tests de desbloqueos
- Tests de batch processing

### Step 5.2: Tests de integración
- Flujo completo de usuario nuevo
- Flujo de progresión y desbloqueos
- Flujo de mini-jefes

---

## Prioridades para ESTA Sesión

1. ✅ **Step 1.1** - Módulo de cálculos core (CRÍTICO)
2. ✅ **Step 1.2** - Módulo de gestión de perfil (CRÍTICO)
3. ✅ **Step 1.3** - Módulo de desbloqueos (IMPORTANTE)
4. ✅ **Step 1.4** - Módulo de procesamiento de batch (IMPORTANTE)

**Tiempo estimado:** 50 minutos
**Objetivo:** Tener la lógica core lista para integrar en los endpoints

---

## Siguiente Sesión

5. **Step 2.1-2.4** - Integración con endpoints existentes
6. Pruebas básicas de flujo completo

