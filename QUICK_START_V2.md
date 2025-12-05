# 🚀 Quick Start - Implementación V2

## ✅ Estado Actual
- Tablas creadas ✅
- Configuraciones cargadas ✅  
- Endpoints de testing funcionando ✅

## 🎯 Próximos Pasos

### **Semana 1: Core del Sistema**

#### DÍA 1 - Setup y Configuración
```
□ Crear v2/ directory
□ ConfigManager - Leer configs de BD
□ Models - Dataclasses para Exercise, BatchResult
□ Test: Verificar lectura de configs
```

#### DÍA 2 - Generación de Ejercicios  
```
□ ExerciseGenerator - Generar ejercicio por nivel invisible
□ BatchGenerator - Generar batch con distribución 2-6-2
□ Test: Verificar rangos y dificultades
```

#### DÍA 3 - Evaluación
```
□ PerformanceEvaluator - Ajustar nivel invisible
□ ScoringCalculator - Calcular puntuación V2
□ DominioLevelManager - Mapear nivel invisible → dominio
□ Test: Verificar cálculos
```

#### DÍA 4 - Miniboss
```
□ MinibossDetector - Detectar candidatos
□ MinibossEvaluator - Generar y evaluar miniboss
□ Test: Simular aprobación/fallo
```

#### DÍA 5 - Persistencia
```
□ BatchRecorder - Guardar en pine_batches_completados
□ Test: Verificar inserción completa
```

### **Semana 2: Integración**

#### DÍA 6-7 - Modificar Endpoints
```
□ Modificar /api/sessions/start
  - Usar BatchGenerator V2
  - Detectar miniboss
  
□ Modificar /api/sessions/complete
  - Usar PerformanceEvaluator V2
  - Usar ScoringCalculator V2
  - Guardar batch completo
```

#### DÍA 8 - Testing E2E
```
□ Test: Usuario nuevo
□ Test: Progresión normal
□ Test: Miniboss aprobado
□ Test: Miniboss fallido
□ Test: Cambio de nivel
```

#### DÍA 9-10 - Deploy
```
□ Feature flag USE_GAMIFICATION_V2
□ Script de migración de usuarios
□ Deploy a staging
□ Verificar en producción
```

---

## 📁 Estructura de Archivos

```
pineServer/
├── v2/                              # ← Nuevo directorio
│   ├── __init__.py
│   ├── config_manager.py           # Fase 1
│   ├── models.py                   # Fase 1
│   ├── exercise_generator.py       # Fase 2
│   ├── batch_generator.py          # Fase 2
│   ├── performance_evaluator.py    # Fase 3
│   ├── scoring_calculator.py       # Fase 3
│   ├── dominio_level_manager.py    # Fase 4
│   ├── miniboss_detector.py        # Fase 5
│   ├── miniboss_evaluator.py       # Fase 5
│   └── batch_recorder.py           # Fase 6
├── main.py                          # Modificar Fase 7
└── tests/                           # ← Tests
    ├── test_config_manager.py
    ├── test_generators.py
    ├── test_evaluators.py
    └── test_integration_v2.py
```

---

## 🔑 Componentes Clave

### 1. ConfigManager
```python
class ConfigManager:
    def get_system_config(key: str) -> Any
    def get_difficulty_config(op: str, nivel: int) -> Dict
```

### 2. ExerciseGenerator
```python
class ExerciseGenerator:
    def generate(operacion: str, nivel_invisible: float) -> Exercise
```

### 3. BatchGenerator
```python
class BatchGenerator:
    def generate_batch(op: str, nivel: float) -> List[Exercise]
```

### 4. PerformanceEvaluator
```python
class PerformanceEvaluator:
    def evaluate(results: List, nivel_actual: float) -> float
```

### 5. MinibossDetector
```python
class MinibossDetector:
    def is_candidate(user_ref: str, op: str) -> bool
```

---

## 🧪 Testing Rápido

```bash
# Test configs
python -m pytest tests/test_config_manager.py

# Test generadores
python -m pytest tests/test_generators.py

# Test evaluadores
python -m pytest tests/test_evaluators.py

# Test integración
python -m pytest tests/test_integration_v2.py

# Test E2E
python test_v2_integration.py
```

---

## ⚡ Quick Commands

```bash
# Iniciar servidor con V2
USE_GAMIFICATION_V2=true uvicorn main:app --reload

# Verificar tablas
python check_v2_tables.py

# Limpiar datos de prueba
python cleanup_test_config.py

# Migrar usuarios
python migrate_users_to_v2.py
```

---

## 🎯 Checklist de Deploy

### Pre-deploy
- [ ] Todos los tests pasan
- [ ] Configuraciones validadas
- [ ] Feature flag implementado
- [ ] Backup de BD

### Deploy
- [ ] Deploy a staging
- [ ] Probar con usuario de prueba
- [ ] Verificar logs
- [ ] Habilitar V2 gradualmente

### Post-deploy
- [ ] Monitorear errores
- [ ] Verificar performance
- [ ] Feedback de usuarios
- [ ] Ajustar configs si es necesario

---

## 📞 Para Dudas

Revisar:
- `PLAN_IMPLEMENTACION_V2_BACKEND.md` - Plan completo
- `PLAN_GAMIFICATION_V2.md` - Diseño del sistema
- `TABLAS_MODIFICACIONES_V2.md` - Esquema de BD
- `GUIA_TESTING_V2_ENDPOINTS.md` - Testing

---

**Comenzar por**: Día 1 - ConfigManager
