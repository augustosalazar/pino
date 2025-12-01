# 🎮 Quick Reference - Sistema de Gamificación

## 📦 Módulos

| Módulo | Propósito | Funciones Clave |
|--------|-----------|-----------------|
| `gamification_core.py` | Cálculos puros | `calcular_pd_ejercicio()`, `calcular_xp_batch()`, `calcular_nivel_jugador()` |
| `gamification_profile.py` | CRUD de perfiles | `obtener_perfil_completo()`, `actualizar_pp()`, `actualizar_pd()`, `actualizar_xp()` |
| `gamification_unlocks.py` | Desbloqueos | `verificar_y_desbloquear_operaciones()`, `obtener_modos_disponibles()` |
| `gamification_batch.py` | Procesar batches | `procesar_batch_completo()`, `gestionar_items_pendientes()` |

---

## 🚀 Uso Rápido

### Inicializar usuario nuevo
```python
import gamification_profile as gp
await gp.inicializar_perfil_completo('user_123')
```

### Procesar batch completado
```python
import gamification_batch as gb

resultados = [
    {'exercise_id': 'ex1', 'fue_primer_intento': True, 'es_correcto_final': True, 
     'operacion': 'suma', 'dificultad': 2.0},
    # ... más items
]

resultado = await gb.procesar_batch_completo('user_123', resultados, 'suma', 2.5)
```

### Consultar estado
```python
import gamification_profile as gp
perfil_completo = await gp.obtener_perfil_completo('user_123')
```

---

## 📊 Variables Clave

- **PP**: Puntos de Práctica (participación) - límite 30/día
- **PD**: Puntos de Dominio (aprendizaje) - global + por operación
- **XP**: Experiencia (nivel RPG)
- **Niveles de dominio**: 1-5 por operación (suma/resta/mult/div)

---

## 🎯 Fórmulas

| Concepto | Fórmula |
|----------|---------|
| PD por ejercicio | 2 (1er intento) / 1 (reintento) / 0 (fallo) |
| Bonus batch | 5 (≥90%) / 3 (≥70%) / 0 |
| Bonus racha diaria | +3 PD (primer batch del día) |
| XP por batch | `correctos × (3 + 0.5 × dificultad_media)` |
| XP para nivel L | `50 × L^1.5` |
| Recompensa level up | `20 × nivel_nuevo` PD |
| Score semanal | `0.4 × PP_semana + 0.6 × PD_semana` |

---

## 🔓 Desbloqueos

### Operaciones
- **SUMA**: Desbloqueada desde inicio
- **RESTA**: PD_global ≥30, PD_suma ≥20, mini-jefe suma ✓
- **MULT**: PD_global ≥70, PD_resta ≥20, mini-jefe mult ✓
- **DIV**: PD_global ≥100, PD_mult ≥20, mini-jefe div ✓

### Modos
- **Mix Suma+Resta**: Nivel ≥2 en ambas
- **Mix Mult+Div**: Nivel ≥2 en ambas
- **Speed**: 2+ operaciones en nivel ≥3
- **Bosses**: 2+ operaciones en nivel ≥4
- **Elite**: 1+ operación en nivel 5
- **Master**: Todas las ops en nivel ≥3

---

## 🔄 Workflow

```
Usuario completa batch
    ↓
procesar_batch_completo()
    ↓
    ├─ Actualiza PP, PD, XP
    ├─ Verifica level up
    ├─ Marca items pendientes
    ├─ Verifica desbloqueos
    └─ Retorna resumen completo
```

---

## 📋 Integración con Endpoints

### 1. `/users/ensure` o login
```python
perfil = await gp.obtener_perfil_completo(user_ref)
# Devolver en respuesta
```

### 2. `/sessions/start`
```python
items_pendientes = await gb.obtener_items_pendientes(user_ref, op, 3)
# Incluir en batch
```

### 3. `/sessions/complete`
```python
resultado = await gb.procesar_batch_completo(user_ref, resultados, op, dif)
# Devolver recompensas
```

### 4. `/gamification/profile` (nuevo)
```python
perfil = await gp.obtener_perfil_completo(user_ref)
modos = await gu.obtener_modos_disponibles(user_ref)
progreso = await gu.obtener_progreso_desbloqueos(user_ref)
# Devolver todo
```

---

## ⚙️ Tareas Pendientes

### Para producción:
- [ ] Programar reset diario `pp_dia` (cron)
- [ ] Programar reset semanal `pp_semana`, `pd_semana` (cron)
- [ ] Implementar generadores de mini-jefes
- [ ] Agregar campo `ultimo_batch_fecha` para detección precisa de días
- [ ] Tests unitarios
- [ ] Validaciones de input robustas

---

## 📁 Documentos

- `GAMIFICATION_PHASE1_DELIVERY.md` - Guía completa de entrega
- `GAMIFICATION_IMPLEMENTATION_SUMMARY.md` - Detalles técnicos
- `GAMIFICATION_IMPLEMENTATION_PLAN.md` - Plan completo con fases
- `README_ROBLE.md` - Info de migraciones de base de datos

---

**Última actualización:** 30 Nov 2025
**Estado:** ✅ Fase 1 Completada - Listo para integración
