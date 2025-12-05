# Plan de Implementación del Nuevo Motor de Gamificación V2

**Fecha de creación**: 2025-12-05  
**Estado**: En planificación  
**Versión**: 1.0

---

## 📋 RESUMEN EJECUTIVO

Sistema de gamificación adaptable para matemáticas básicas (suma, resta, multiplicación, división).

### Conceptos Clave:
- **Nivel Visible**: Lo que ve el usuario, nunca baja (5 niveles: básico → maestro)
- **Nivel Invisible**: Nivel real interno para ajustar dificultad, sube y baja
- **Batch**: Tanda de 10 ejercicios con dificultad adaptativa
- **Tipos de Batch**: Regular (normal), Miniboss (prueba de nivel), Endless (modo infinito)

---

## 📊 PARTE 1: TABLAS DE ROBLE (SUPABASE)

### Notas Importantes:
- Roble NO soporta DEFAULT con funciones
- Roble NO soporta validaciones CHECK
- Todas las constraints UNIQUE se manejan en la aplicación
- UUIDs y timestamps se generan en el servidor Python

---

### 1. difficulty_levels
**Descripción**: Configuración de niveles de dificultad por operación

```sql
CREATE TABLE difficulty_levels (
    id UUID PRIMARY KEY,
    operation TEXT NOT NULL,
    level_name TEXT NOT NULL,
    level_number INT4 NOT NULL,
    min_operand_1 INT4 NOT NULL,
    max_operand_1 INT4 NOT NULL,
    min_operand_2 INT4 NOT NULL,
    max_operand_2 INT4 NOT NULL,
    max_result INT4,
    response_type TEXT NOT NULL,
    num_options INT4,
    max_time_seconds INT4,
    difficulty_score NUMERIC NOT NULL,
    config_version INT4 NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_difficulty_operation ON difficulty_levels(operation, level_number, config_version);
```

**Valores esperados**:
- `operation`: 'suma', 'resta', 'mult', 'div'
- `level_name`: 'basico', 'intermedio', 'avanzado', 'experto', 'maestro'
- `level_number`: 1, 2, 3, 4, 5
- `response_type`: 'multiple_choice', 'open'
- `difficulty_score`: 1.00 a 5.00
- `config_version`: Para A/B testing

---

### 2. user_operation_progress
**Descripción**: Progreso del usuario por operación (niveles visible e invisible)

```sql
CREATE TABLE user_operation_progress (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    operation TEXT NOT NULL,
    visible_level INT4 NOT NULL,
    invisible_level NUMERIC NOT NULL,
    last_miniboss_attempt TIMESTAMPTZ,
    miniboss_failures_since_last INT4 NOT NULL,
    batches_since_last_miniboss INT4 NOT NULL,
    total_exercises_attempted INT4 NOT NULL,
    total_exercises_correct INT4 NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_user_progress_user ON user_operation_progress(user_id);
CREATE INDEX idx_user_progress_user_op ON user_operation_progress(user_id, operation);
```

**Validaciones en aplicación**:
- UNIQUE(user_id, operation)
- visible_level: 1-5
- invisible_level: 1.00-6.00 (puede superar 5 para ajustes finos)

---

### 3. user_batches
**Descripción**: Historial de batches completados

```sql
CREATE TABLE user_batches (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    operation TEXT NOT NULL,
    batch_type TEXT NOT NULL,
    central_level INT4 NOT NULL,
    invisible_level_before NUMERIC NOT NULL,
    invisible_level_after NUMERIC NOT NULL,
    exercises_data JSONB NOT NULL,
    total_exercises INT4 NOT NULL,
    correct_exercises INT4 NOT NULL,
    score_earned INT4 NOT NULL,
    practice_points_earned INT4 NOT NULL,
    avg_difficulty NUMERIC NOT NULL,
    completed_at TIMESTAMPTZ NOT NULL,
    session_duration_seconds INT4,
    miniboss_passed BOOL,
    endless_streak INT4
);

CREATE INDEX idx_batches_user ON user_batches(user_id);
CREATE INDEX idx_batches_user_completed ON user_batches(user_id, completed_at);
CREATE INDEX idx_batches_operation ON user_batches(operation);
CREATE INDEX idx_batches_type ON user_batches(batch_type, completed_at);
```

**Valores esperados**:
- `batch_type`: 'regular', 'miniboss', 'endless'
- `exercises_data`: Array de objetos con estructura:
  ```json
  [
    {
      "exercise_number": 1,
      "operand_1": 5,
      "operand_2": 3,
      "correct_answer": 8,
      "user_answer": 8,
      "is_correct": true,
      "difficulty": 1.5,
      "time_taken_seconds": 3.2,
      "was_retry": false
    }
  ]
  ```

---

### 4. pending_retry_exercises
**Descripción**: Ejercicios fallados que deben repetirse en próximo batch

```sql
CREATE TABLE pending_retry_exercises (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    operation TEXT NOT NULL,
    level INT4 NOT NULL,
    operand_1 INT4 NOT NULL,
    operand_2 INT4 NOT NULL,
    failed_at TIMESTAMPTZ NOT NULL,
    retried BOOL NOT NULL,
    retried_at TIMESTAMPTZ
);

CREATE INDEX idx_pending_retry_user ON pending_retry_exercises(user_id, operation, retried);
```

**Lógica**: 
- Cuando un usuario falla un ejercicio ≤ nivel central, se registra aquí
- Se incluye en el próximo batch
- Se marca `retried = true` cuando se presenta

---

### 5. user_streaks
**Descripción**: Sistema de streak diario

```sql
CREATE TABLE user_streaks (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    current_streak_days INT4 NOT NULL,
    longest_streak_days INT4 NOT NULL,
    last_activity_date DATE NOT NULL,
    streak_score INT4 NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_streaks_user ON user_streaks(user_id);
```

**Validaciones en aplicación**:
- UNIQUE(user_id)
- Solo cuenta si el usuario tiene 4+ aciertos en el día
- Streak score: 5 + (3 × días), máx 30 días
- Máximo streak score: 5 + (3 × 30) = 95 puntos

---

### 6. user_practice_points
**Descripción**: Puntos de práctica para recompensas cosméticas

```sql
CREATE TABLE user_practice_points (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    total_points INT4 NOT NULL,
    points_spent INT4 NOT NULL,
    available_points INT4 NOT NULL,
    chests_opened INT4 NOT NULL,
    last_chest_at INT4 NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_practice_points_user ON user_practice_points(user_id);
```

**Validaciones en aplicación**:
- UNIQUE(user_id)
- available_points = total_points - points_spent
- Cofre cada 100 puntos (configurable)
- `last_chest_at`: marca de puntos del último cofre

---

### 7. leaderboard_weekly
**Descripción**: Tabla de clasificación semanal

```sql
CREATE TABLE leaderboard_weekly (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    week_start DATE NOT NULL,
    total_score INT4 NOT NULL,
    batches_completed INT4 NOT NULL,
    rank INT4,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_leaderboard_weekly_week ON leaderboard_weekly(week_start, rank);
CREATE INDEX idx_leaderboard_weekly_user ON leaderboard_weekly(user_id, week_start);
```

**Validaciones en aplicación**:
- UNIQUE(user_id, week_start)
- `week_start`: Siempre lunes de la semana
- Se recalcula rank cada vez que se actualiza

---

### 8. leaderboard_endless_monthly
**Descripción**: Tabla de clasificación endless mensual

```sql
CREATE TABLE leaderboard_endless_monthly (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    month_start DATE NOT NULL,
    best_streak INT4 NOT NULL,
    total_attempts INT4 NOT NULL,
    rank INT4,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_leaderboard_endless_month ON leaderboard_endless_monthly(month_start, rank);
CREATE INDEX idx_leaderboard_endless_user ON leaderboard_endless_monthly(user_id, month_start);
```

**Validaciones en aplicación**:
- UNIQUE(user_id, month_start)
- `month_start`: Siempre día 1 del mes
- `best_streak`: Mejor racha del mes en modo endless

---

### 9. gamification_config
**Descripción**: Configuración del sistema (para A/B testing)

```sql
CREATE TABLE gamification_config (
    id UUID PRIMARY KEY,
    config_key TEXT NOT NULL,
    config_value JSONB NOT NULL,
    version INT4 NOT NULL,
    active BOOL NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_config_key ON gamification_config(config_key, active);
```

**Validaciones en aplicación**:
- UNIQUE(config_key, version)
- Ejemplos de config_key:
  - `scoring.base_formula`
  - `scoring.participation_bonus`
  - `scoring.error_penalty`
  - `streak.min_correct_exercises`
  - `streak.max_days`
  - `practice_points.chest_interval`
  - `miniboss.min_batches_between`
  - `batch.size`

**Ejemplo de config_value**:
```json
{
  "value": 10,
  "type": "integer",
  "min": 0,
  "max": 100,
  "description": "Puntos de bonificación por completar batch"
}
```

---

## 🗺️ PARTE 2: PLAN DE IMPLEMENTACIÓN POR ETAPAS

### IMPORTANTE: Orden de Implementación
1. **Primero**: pineServer (backend Python)
2. **Después**: r_pino (frontend React Native)

---

## 🔧 FASE 1: FUNDAMENTOS Y CONFIGURACIÓN (pineServer)

### Etapa 1.1: Estructura de Clases Base ⏱️ 2-3 horas

**Archivos a crear**:
```
pineServer/
├── models/
│   └── gamification_v2/
│       ├── __init__.py
│       ├── operation.py         # Clase Operation
│       ├── exercise.py          # Clase Exercise
│       ├── difficulty_level.py  # Clase DifficultyLevel
│       └── batch.py             # Clase Batch (básica)
```

**Clase Operation** (`operation.py`):
```python
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Operation:
    """Representa una operación matemática"""
    name: str  # 'suma', 'resta', 'mult', 'div'
    symbol: str  # '+', '-', '×', '÷'
    display_name: str  # 'Suma', 'Resta', 'Multiplicación', 'División'
    
    def calculate(self, operand_1: int, operand_2: int) -> int:
        """Calcula el resultado de la operación"""
        pass
    
    def validate_operands(self, operand_1: int, operand_2: int) -> bool:
        """Valida que los operandos sean válidos para esta operación"""
        pass
```

**Clase DifficultyLevel** (`difficulty_level.py`):
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class DifficultyLevel:
    """Configuración de un nivel de dificultad"""
    operation: str
    level_name: str
    level_number: int
    min_operand_1: int
    max_operand_1: int
    min_operand_2: int
    max_operand_2: int
    max_result: Optional[int]
    response_type: str  # 'multiple_choice' | 'open'
    num_options: Optional[int]
    max_time_seconds: int
    difficulty_score: float
    config_version: int = 1
    
    @classmethod
    def from_db(cls, row: dict):
        """Crea instancia desde row de BD"""
        pass
```

**Clase Exercise** (`exercise.py`):
```python
from dataclasses import dataclass
from typing import List, Optional
import uuid
from datetime import datetime

@dataclass
class Exercise:
    """Representa un ejercicio individual"""
    id: str
    operation: str
    level: int
    operand_1: int
    operand_2: int
    correct_answer: int
    response_type: str
    options: Optional[List[int]]  # Para multiple choice
    difficulty_score: float
    max_time_seconds: int
    created_at: datetime
    
    @classmethod
    def generate(cls, operation: str, difficulty_level: 'DifficultyLevel') -> 'Exercise':
        """Genera un ejercicio basado en configuración de dificultad"""
        pass
    
    def to_dict(self) -> dict:
        """Serializa para enviar al frontend"""
        pass
```

**Clase Batch** (`batch.py`):
```python
from dataclasses import dataclass
from typing import List
from .exercise import Exercise

@dataclass
class Batch:
    """Representa un batch de ejercicios"""
    id: str
    operation: str
    batch_type: str  # 'regular' | 'miniboss' | 'endless'
    central_level: int
    exercises: List[Exercise]
    
    def get_avg_difficulty(self) -> float:
        """Calcula dificultad promedio del batch"""
        pass
    
    def to_dict(self) -> dict:
        """Serializa para enviar al frontend"""
        pass
```

**Tareas**:
- [ ] Crear estructura de carpetas
- [ ] Implementar clase Operation con las 4 operaciones
- [ ] Implementar clase DifficultyLevel
- [ ] Implementar clase Exercise
- [ ] Implementar clase Batch básica
- [ ] Tests unitarios para cada clase

---

### Etapa 1.2: Sistema de Configuración ⏱️ 3-4 horas

**Archivos a crear**:
```
pineServer/
├── config/
│   └── gamification_v2/
│       ├── difficulty_config.json    # Config de niveles
│       ├── scoring_config.json       # Config de puntuación
│       └── system_config.json        # Config general
├── services/
│   └── gamification_v2/
│       ├── __init__.py
│       └── config_manager.py         # Gestor de configuración
```

**difficulty_config.json**:
```json
{
  "suma": {
    "1": {
      "level_name": "basico",
      "min_operand_1": 0,
      "max_operand_1": 10,
      "min_operand_2": 0,
      "max_operand_2": 10,
      "max_result": 20,
      "response_type": "multiple_choice",
      "num_options": 4,
      "max_time_seconds": 30,
      "difficulty_score": 1.0
    },
    "2": {
      "level_name": "intermedio",
      "min_operand_1": 10,
      "max_operand_1": 50,
      "min_operand_2": 10,
      "max_operand_2": 50,
      "max_result": 100,
      "response_type": "multiple_choice",
      "num_options": 4,
      "max_time_seconds": 45,
      "difficulty_score": 2.0
    }
  }
}
```

**Clase ConfigManager**:
```python
class ConfigManager:
    """Gestiona la configuración del sistema"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self._cache = {}
    
    def load_difficulty_levels(self, operation: str, config_version: int = 1) -> List[DifficultyLevel]:
        """Carga niveles de dificultad desde BD"""
        pass
    
    def get_system_config(self, key: str) -> dict:
        """Obtiene configuración del sistema"""
        pass
    
    def update_config(self, key: str, value: dict, version: int):
        """Actualiza configuración (admin only)"""
        pass
```

**Tareas**:
- [ ] Crear archivos de configuración JSON iniciales
- [ ] Implementar ConfigManager
- [ ] Script para poblar tabla `difficulty_levels`
- [ ] Script para poblar tabla `gamification_config`
- [ ] Tests del ConfigManager

---

### Etapa 1.3: Generador de Ejercicios Individual ⏱️ 4-5 horas

**Archivos a crear**:
```
pineServer/
└── services/
    └── gamification_v2/
        ├── exercise_generator.py      # Clase base abstracta
        └── standard_generator.py      # Implementación estándar
```

**Clase ExerciseGenerator** (abstracta):
```python
from abc import ABC, abstractmethod
from typing import List
from models.gamification_v2 import Exercise, DifficultyLevel

class ExerciseGenerator(ABC):
    """Clase base para generadores de ejercicios"""
    
    @abstractmethod
    def generate_exercise(self, operation: str, difficulty: DifficultyLevel) -> Exercise:
        """Genera un ejercicio individual"""
        pass
    
    @abstractmethod
    def generate_multiple_choice_options(self, correct_answer: int, num_options: int) -> List[int]:
        """Genera opciones para multiple choice"""
        pass
```

**Clase StandardExerciseGenerator**:
```python
import random
from typing import List
from .exercise_generator import ExerciseGenerator

class StandardExerciseGenerator(ExerciseGenerator):
    """Generador estándar de ejercicios"""
    
    def generate_exercise(self, operation: str, difficulty: DifficultyLevel) -> Exercise:
        """
        Genera ejercicio según configuración de dificultad
        - Selecciona operandos aleatorios dentro de rangos
        - Valida que el resultado esté dentro de max_result
        - Para división, asegura que sea exacta
        """
        pass
    
    def generate_multiple_choice_options(self, correct_answer: int, num_options: int) -> List[int]:
        """
        Genera opciones de respuesta
        - Incluye la respuesta correcta
        - Genera distractores cercanos al valor correcto
        - Evita duplicados
        - Baraja el orden
        """
        pass
    
    def _generate_valid_operands(self, operation: str, difficulty: DifficultyLevel) -> tuple:
        """Genera operandos válidos según operación"""
        pass
```

**Tareas**:
- [ ] Implementar ExerciseGenerator (clase abstracta)
- [ ] Implementar StandardExerciseGenerator
- [ ] Lógica especial para división (solo exactas)
- [ ] Generación inteligente de distractores
- [ ] Tests unitarios extensivos
- [ ] Validación de rangos y resultados

---

## 🎯 FASE 2: SISTEMA DE BATCHES (pineServer)

### Etapa 2.1: Mejora de Clase Batch ⏱️ 2 horas

**Actualizar** `batch.py`:
```python
@dataclass
class Batch:
    """Batch de ejercicios con metadatos"""
    id: str
    user_id: str
    operation: str
    batch_type: str
    central_level: int
    invisible_level: float
    exercises: List[Exercise]
    created_at: datetime
    
    def get_avg_difficulty(self) -> float:
        """Dificultad promedio"""
        return sum(e.difficulty_score for e in self.exercises) / len(self.exercises)
    
    def get_level_distribution(self) -> dict:
        """Distribución de niveles en el batch"""
        distribution = {}
        for ex in self.exercises:
            distribution[ex.level] = distribution.get(ex.level, 0) + 1
        return distribution
    
    def validate_structure(self) -> bool:
        """Valida que el batch cumple reglas estructurales"""
        pass
```

**Tareas**:
- [ ] Ampliar clase Batch con metadatos
- [ ] Métodos de validación
- [ ] Serialización completa

---

### Etapa 2.2: Generador de Batches Regular ⏱️ 5-6 horas

**Archivo**: `batch_generator.py`

```python
from abc import ABC, abstractmethod
from typing import List
from models.gamification_v2 import Batch, Exercise

class BatchGenerator(ABC):
    """Clase base para generadores de batches"""
    
    @abstractmethod
    def generate_batch(self, user_id: str, operation: str, invisible_level: float) -> Batch:
        """Genera un batch completo"""
        pass
```

**Archivo**: `regular_batch_generator.py`

```python
class RegularBatchGenerator(BatchGenerator):
    """
    Generador de batches regulares
    
    Estructura del batch (10 ejercicios):
    - 2 ejercicios: nivel_central - 1 (fáciles, warm-up)
    - 6 ejercicios: nivel_central (núcleo)
    - 2 ejercicios: nivel_central + 1 (desafío)
    
    Si hay ejercicios pendientes de retry, se integran en el nivel correspondiente
    """
    
    def __init__(self, exercise_generator, config_manager, supabase_client):
        self.exercise_gen = exercise_generator
        self.config = config_manager
        self.db = supabase_client
    
    def generate_batch(self, user_id: str, operation: str, invisible_level: float) -> Batch:
        """
        1. Determinar nivel central (round(invisible_level))
        2. Obtener ejercicios pendientes de retry
        3. Generar ejercicios nuevos para completar 10
        4. Distribuir según estructura estándar
        5. Ordenar: fáciles → centrales → difíciles
        """
        pass
    
    def _get_pending_retries(self, user_id: str, operation: str) -> List[Exercise]:
        """Obtiene ejercicios pendientes de BD"""
        pass
    
    def _determine_distribution(self, invisible_level: float, retry_exercises: List[Exercise]) -> dict:
        """Determina cuántos ejercicios de cada nivel"""
        pass
```

**Tareas**:
- [ ] Implementar BatchGenerator abstracto
- [ ] Implementar RegularBatchGenerator
- [ ] Integración de ejercicios retry
- [ ] Lógica de distribución adaptativa
- [ ] Tests de generación de batches

---

### Etapa 2.3: Generador de Batches Miniboss ⏱️ 3-4 horas

**Archivo**: `miniboss_batch_generator.py`

```python
class MinibossBatchGenerator(BatchGenerator):
    """
    Generador de batches miniboss (prueba de nivel)
    
    Características:
    - 10 ejercicios del nivel central únicamente
    - Solo respuestas abiertas (no multiple choice)
    - Criterios estrictos de tiempo
    """
    
    def generate_batch(self, user_id: str, operation: str, invisible_level: float) -> Batch:
        """
        1. Nivel central = nivel visible actual + 1
        2. Generar 10 ejercicios de ese nivel
        3. Todos con response_type = 'open'
        4. Tiempo más estricto
        """
        pass
    
    def get_success_criteria(self, invisible_level: float) -> dict:
        """
        Retorna criterios de éxito para el miniboss:
        {
            'min_correct': 8,  # 80% de aciertos
            'max_avg_time': 20  # segundos promedio
        }
        """
        pass
```

**Tareas**:
- [ ] Implementar MinibossBatchGenerator
- [ ] Definir criterios de éxito dinámicos
- [ ] Tests específicos para miniboss

---

### Etapa 2.4: Generador de Batches Endless ⏱️ 2-3 horas

**Archivo**: `endless_batch_generator.py`

```python
class EndlessBatchGenerator:
    """
    Generador para modo endless (un ejercicio a la vez)
    
    No genera "batches" completos, sino ejercicios individuales
    """
    
    def generate_next_exercise(self, user_id: str, operation: str, invisible_level: float) -> Exercise:
        """
        Genera el siguiente ejercicio para modo endless
        - Nivel = invisible_level actual
        - Dificultad consistente
        - No afecta progresión normal
        """
        pass
```

**Tareas**:
- [ ] Implementar EndlessBatchGenerator
- [ ] Lógica de un ejercicio a la vez
- [ ] Tests

---

## 📊 FASE 3: SISTEMA DE EVALUACIÓN (pineServer)

### Etapa 3.1: Evaluador de Respuestas ⏱️ 4-5 horas

**Archivo**: `evaluator.py`

```python
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

@dataclass
class ExerciseResult:
    """Resultado de un ejercicio individual"""
    exercise_id: str
    operand_1: int
    operand_2: int
    correct_answer: int
    user_answer: int
    is_correct: bool
    difficulty: float
    time_taken_seconds: float
    was_retry: bool

@dataclass
class BatchResult:
    """Resultado de un batch completo"""
    batch_id: str
    user_id: str
    operation: str
    batch_type: str
    central_level: int
    exercise_results: List[ExerciseResult]
    total_exercises: int
    correct_exercises: int
    avg_difficulty: float
    total_time_seconds: float

class Evaluator:
    """Evalúa respuestas y calcula estadísticas"""
    
    def __init__(self, supabase_client):
        self.db = supabase_client
    
    def evaluate_batch(self, batch: Batch, user_answers: List[dict]) -> BatchResult:
        """
        Evalúa todas las respuestas de un batch
        - Compara respuestas con soluciones correctas
        - Calcula estadísticas
        - Identifica ejercicios fallados para retry
        """
        pass
    
    def identify_failed_exercises_for_retry(self, batch_result: BatchResult, central_level: int) -> List[dict]:
        """
        Identifica ejercicios que deben repetirse:
        - Ejercicios fallados
        - Con nivel <= nivel_central
        """
        pass
    
    def save_failed_exercises(self, user_id: str, operation: str, failed_exercises: List[dict]):
        """Guarda ejercicios fallados en pending_retry_exercises"""
        pass
```

**Tareas**:
- [ ] Implementar clases de resultado
- [ ] Implementar Evaluator
- [ ] Lógica de identificación de retries
- [ ] Persistencia en BD
- [ ] Tests unitarios

---

### Etapa 3.2: Actualizador de Nivel Invisible ⏱️ 4-5 horas

**Archivo**: `invisible_level_updater.py`

```python
class InvisibleLevelUpdater:
    """
    Ajusta el nivel invisible según desempeño
    
    Reglas de ajuste:
    - Si correctos >= 80%: +0.2 al nivel invisible
    - Si correctos >= 60% y < 80%: +0.1
    - Si correctos >= 40% y < 60%: sin cambio
    - Si correctos < 40%: -0.1
    - Límites: 1.0 <= invisible_level <= 6.0
    """
    
    def __init__(self, config_manager):
        self.config = config_manager
    
    def calculate_new_invisible_level(
        self, 
        current_level: float, 
        batch_result: BatchResult
    ) -> float:
        """
        Calcula nuevo nivel invisible basado en desempeño
        - Considera porcentaje de aciertos
        - Considera dificultad promedio del batch
        - Ajuste suave y gradual
        """
        pass
    
    def _get_adjustment_delta(self, success_rate: float) -> float:
        """Obtiene el delta de ajuste según % de éxito"""
        adjustments = {
            0.8: 0.2,   # >= 80%
            0.6: 0.1,   # >= 60%
            0.4: 0.0,   # >= 40%
            0.0: -0.1   # < 40%
        }
        for threshold, delta in sorted(adjustments.items(), reverse=True):
            if success_rate >= threshold:
                return delta
        return -0.1
```

**Tareas**:
- [ ] Implementar InvisibleLevelUpdater
- [ ] Definir reglas de ajuste configurables
- [ ] Tests con diferentes escenarios
- [ ] Validación de límites

---

### Etapa 3.3: Detector de Miniboss ⏱️ 3-4 horas

**Archivo**: `miniboss_detector.py`

```python
class MinibossDetector:
    """
    Determina cuándo presentar un miniboss
    
    Condiciones:
    1. Nivel invisible >= nivel visible + 0.5
    2. Han pasado al menos 3 batches desde último miniboss fallido
    3. Últimos 3 batches tienen >= 70% de aciertos en promedio
    """
    
    def __init__(self, supabase_client, config_manager):
        self.db = supabase_client
        self.config = config_manager
    
    def should_present_miniboss(self, user_id: str, operation: str) -> bool:
        """
        Evalúa si debe presentarse un miniboss
        """
        # Obtener progreso del usuario
        progress = self._get_user_progress(user_id, operation)
        
        # Verificar condición de nivel
        if progress['invisible_level'] < progress['visible_level'] + 0.5:
            return False
        
        # Verificar batches desde último fallo
        if progress['batches_since_last_miniboss'] < 3:
            return False
        
        # Verificar desempeño reciente
        recent_performance = self._get_recent_performance(user_id, operation, num_batches=3)
        if recent_performance['avg_success_rate'] < 0.7:
            return False
        
        return True
    
    def _get_recent_performance(self, user_id: str, operation: str, num_batches: int) -> dict:
        """Obtiene estadísticas de batches recientes"""
        pass
```

**Tareas**:
- [ ] Implementar MinibossDetector
- [ ] Consultas a BD para histórico
- [ ] Lógica de decisión
- [ ] Tests con casos edge

---

## 💰 FASE 4: SISTEMA DE PUNTUACIÓN (pineServer)

### Etapa 4.1: Puntuación Base ⏱️ 3-4 horas

**Archivo**: `scoring_system.py`

```python
class ScoringSystem:
    """
    Sistema de puntuación
    
    Fórmula: max(0, C × (5 + d̄) + participación - penalización)
    
    Donde:
    - C = ejercicios correctos
    - d̄ = dificultad promedio
    - participación = 10 si completó todos
    - penalización = 2 × E (E = errores)
    """
    
    def __init__(self, config_manager):
        self.config = config_manager
    
    def calculate_score(self, batch_result: BatchResult) -> int:
        """
        Calcula puntuación total del batch
        
        Componentes:
        1. Base: C × (5 + d̄)
        2. Bonus participación: +10 si completó 10/10
        3. Penalización: -2 × errores
        4. Mínimo: 0
        """
        C = batch_result.correct_exercises
        T = batch_result.total_exercises
        E = T - C
        d = batch_result.avg_difficulty
        
        # Puntuación base
        base_score = C * (5 + d)
        
        # Bonificación por participación
        participation_bonus = 10 if T >= 10 else 0
        
        # Penalización suave
        error_penalty = 2 * E
        
        # Total
        total_score = base_score + participation_bonus - error_penalty
        
        # Límite mínimo
        return max(0, int(total_score))
    
    def get_score_breakdown(self, batch_result: BatchResult) -> dict:
        """Retorna desglose de puntuación para mostrar al usuario"""
        pass
```

**Tareas**:
- [ ] Implementar ScoringSystem
- [ ] Cálculo de puntuación
- [ ] Desglose detallado
- [ ] Tests con diferentes escenarios

---

### Etapa 4.2: Sistema de Streak ⏱️ 3-4 horas

**Archivo**: `streak_system.py`

```python
from datetime import date, timedelta

class StreakSystem:
    """
    Sistema de streak diario
    
    Reglas:
    - Solo cuenta si el usuario tiene >= 4 aciertos en el día
    - Streak score: 5 + (3 × días)
    - Máximo: 30 días
    """
    
    def __init__(self, supabase_client, config_manager):
        self.db = supabase_client
        self.config = config_manager
    
    def update_streak(self, user_id: str, batch_result: BatchResult) -> dict:
        """
        Actualiza el streak del usuario
        
        Lógica:
        1. Verificar si el batch cumple requisito mínimo (4+ aciertos)
        2. Obtener último streak del usuario
        3. Comparar fechas:
           - Mismo día: no afecta streak
           - Día consecutivo: incrementar streak
           - Días saltados: resetear a 1
        4. Calcular streak score
        5. Actualizar BD
        """
        pass
    
    def calculate_streak_score(self, streak_days: int) -> int:
        """
        Calcula puntuación del streak
        Fórmula: 5 + (3 × min(streak_days, 30))
        """
        capped_days = min(streak_days, 30)
        return 5 + (3 * capped_days)
    
    def _qualifies_for_streak(self, batch_result: BatchResult) -> bool:
        """Verifica si el batch califica para streak (>= 4 aciertos)"""
        return batch_result.correct_exercises >= 4
```

**Tareas**:
- [ ] Implementar StreakSystem
- [ ] Lógica de actualización diaria
- [ ] Cálculo de score
- [ ] Tests con diferentes escenarios de fechas

---

### Etapa 4.3: Puntos de Práctica ⏱️ 2-3 horas

**Archivo**: `practice_points_system.py`

```python
class PracticePointsSystem:
    """
    Sistema de puntos de práctica
    
    Reglas:
    - 1 punto por cada ejercicio intentado
    - Batch de 10 = 10 puntos
    - Cofre cada 100 puntos (configurable)
    """
    
    def __init__(self, supabase_client, config_manager):
        self.db = supabase_client
        self.config = config_manager
    
    def award_practice_points(self, user_id: str, batch_result: BatchResult) -> dict:
        """
        Otorga puntos de práctica
        
        Returns:
        {
            'points_earned': 10,
            'total_points': 250,
            'available_points': 250,
            'chest_unlocked': True,
            'chests_opened': 3
        }
        """
        points_earned = batch_result.total_exercises
        
        # Obtener estado actual
        current_state = self._get_practice_points_state(user_id)
        
        # Actualizar totales
        new_total = current_state['total_points'] + points_earned
        
        # Verificar si desbloqueó cofre
        chest_interval = self.config.get_system_config('practice_points.chest_interval')['value']
        chest_unlocked = (new_total // chest_interval) > (current_state['last_chest_at'] // chest_interval)
        
        # Actualizar BD
        self._update_practice_points(user_id, new_total, chest_unlocked)
        
        return {
            'points_earned': points_earned,
            'total_points': new_total,
            'chest_unlocked': chest_unlocked
        }
```

**Tareas**:
- [ ] Implementar PracticePointsSystem
- [ ] Lógica de cofres
- [ ] Actualización de BD
- [ ] Tests

---

## 🚀 FASE 5: MOTOR DE PROGRESIÓN (pineServer)

### Etapa 5.1: Motor Principal ⏱️ 5-6 horas

**Archivo**: `progression_engine.py`

```python
class ProgressionEngine:
    """
    Motor principal que coordina todo el flujo
    
    Responsabilidades:
    1. Determinar qué batch presentar
    2. Coordinar evaluación
    3. Actualizar nivel invisible
    4. Detectar eligibilidad para miniboss
    5. Gestionar ascensos de nivel visible
    """
    
    def __init__(
        self,
        supabase_client,
        config_manager,
        batch_generators: dict,
        evaluator,
        level_updater,
        miniboss_detector,
        scoring_system,
        streak_system,
        practice_points_system
    ):
        self.db = supabase_client
        self.config = config_manager
        self.generators = batch_generators
        self.evaluator = evaluator
        self.level_updater = level_updater
        self.miniboss_detector = miniboss_detector
        self.scoring = scoring_system
        self.streak = streak_system
        self.practice_points = practice_points_system
    
    def start_new_batch(self, user_id: str, operation: str) -> dict:
        """
        Inicia un nuevo batch
        
        1. Obtener progreso del usuario
        2. Decidir tipo de batch (regular vs miniboss)
        3. Generar batch apropiado
        4. Retornar batch al frontend
        """
        pass
    
    def submit_batch_results(self, batch_id: str, user_answers: List[dict]) -> dict:
        """
        Procesa resultados de un batch
        
        1. Evaluar respuestas
        2. Calcular puntuación
        3. Actualizar nivel invisible
        4. Actualizar streak
        5. Otorgar puntos de práctica
        6. Verificar ascenso de nivel (si es miniboss)
        7. Guardar en BD
        8. Retornar resumen al frontend
        """
        pass
    
    def _determine_batch_type(self, user_id: str, operation: str) -> str:
        """Decide si presentar regular o miniboss"""
        if self.miniboss_detector.should_present_miniboss(user_id, operation):
            return 'miniboss'
        return 'regular'
```

**Tareas**:
- [ ] Implementar ProgressionEngine
- [ ] Flujo completo de inicio de batch
- [ ] Flujo completo de submit
- [ ] Integración de todos los sistemas
- [ ] Tests de integración

---

### Etapa 5.2: Sistema de Ascenso de Nivel Visible ⏱️ 3-4 horas

**Archivo**: `level_up_system.py`

```python
class LevelUpSystem:
    """
    Gestiona ascensos de nivel visible
    
    Condiciones para subir:
    1. Aprobar miniboss (8+/10 correctos)
    2. Tiempo promedio aceptable
    3. Nivel invisible >= nivel_visible + 0.5
    """
    
    def __init__(self, supabase_client, config_manager):
        self.db = supabase_client
        self.config = config_manager
    
    def evaluate_miniboss_result(
        self, 
        user_id: str, 
        operation: str, 
        batch_result: BatchResult
    ) -> dict:
        """
        Evalúa si el usuario puede subir de nivel
        
        Returns:
        {
            'level_up': True,
            'new_visible_level': 3,
            'criteria_met': {
                'min_correct': True,
                'avg_time': True,
                'invisible_level': True
            }
        }
        """
        pass
    
    def apply_level_up(self, user_id: str, operation: str, new_level: int):
        """Aplica el ascenso de nivel en BD"""
        pass
    
    def handle_miniboss_failure(self, user_id: str, operation: str):
        """
        Maneja fallo de miniboss
        - Incrementa contador de fallos
        - Resetea contador de batches desde miniboss
        """
        pass
```

**Tareas**:
- [ ] Implementar LevelUpSystem
- [ ] Criterios de evaluación
- [ ] Actualización de BD
- [ ] Manejo de fallos
- [ ] Tests

---

### Etapa 5.3: Persistencia de Datos ⏱️ 3-4 horas

**Archivo**: `data_persistence.py`

```python
class DataPersistence:
    """Gestiona todas las operaciones de BD"""
    
    def __init__(self, supabase_client):
        self.db = supabase_client
    
    def save_completed_batch(
        self,
        batch: Batch,
        batch_result: BatchResult,
        score: int,
        practice_points: int,
        invisible_level_before: float,
        invisible_level_after: float,
        miniboss_passed: bool = None
    ):
        """Guarda batch completado en user_batches"""
        pass
    
    def update_user_progress(
        self,
        user_id: str,
        operation: str,
        new_invisible_level: float,
        new_visible_level: int = None
    ):
        """Actualiza user_operation_progress"""
        pass
    
    def update_leaderboards(self, user_id: str, score: int, batch_type: str):
        """Actualiza tablas de clasificación"""
        pass
```

**Tareas**:
- [ ] Implementar DataPersistence
- [ ] Métodos CRUD para todas las tablas
- [ ] Manejo de errores
- [ ] Tests

---

## 🌐 FASE 6: API ENDPOINTS (pineServer)

### Etapa 6.1: Endpoints Básicos ⏱️ 4-5 horas

**Archivo**: `routes/api_v2/gamification.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v2", tags=["gamification_v2"])

class StartBatchRequest(BaseModel):
    user_id: str
    operation: str  # 'suma', 'resta', 'mult', 'div'
    batch_type: str = 'auto'  # 'auto', 'regular', 'endless'

class SubmitBatchRequest(BaseModel):
    batch_id: str
    user_answers: List[dict]  # [{ exercise_id, user_answer, time_taken }]

@router.post("/batch/start")
async def start_batch(request: StartBatchRequest):
    """
    Inicia un nuevo batch
    
    Returns:
    {
        'batch_id': 'uuid',
        'operation': 'suma',
        'batch_type': 'regular',
        'exercises': [...],
        'central_level': 2,
        'is_miniboss': false
    }
    """
    pass

@router.post("/batch/submit")
async def submit_batch(request: SubmitBatchRequest):
    """
    Envía respuestas del batch
    
    Returns:
    {
        'score_earned': 75,
        'score_breakdown': {...},
        'correct_exercises': 8,
        'total_exercises': 10,
        'level_up': false,
        'new_invisible_level': 2.3,
        'streak_updated': true,
        'streak_days': 5,
        'practice_points_earned': 10,
        'chest_unlocked': false
    }
    """
    pass

@router.get("/progress/{user_id}")
async def get_user_progress(user_id: str):
    """
    Obtiene progreso completo del usuario
    
    Returns:
    {
        'operations': {
            'suma': {
                'visible_level': 2,
                'progress_to_next': 0.6,
                'total_exercises': 150,
                'accuracy': 0.82
            },
            ...
        },
        'streak': {...},
        'practice_points': {...}
    }
    """
    pass
```

**Tareas**:
- [ ] Crear router de FastAPI
- [ ] Implementar POST /batch/start
- [ ] Implementar POST /batch/submit
- [ ] Implementar GET /progress/:userId
- [ ] Validación de requests
- [ ] Manejo de errores HTTP
- [ ] Tests de endpoints

---

### Etapa 6.2: Endpoints de Clasificación ⏱️ 2-3 horas

```python
@router.get("/leaderboard/weekly")
async def get_weekly_leaderboard(week_start: str = None, limit: int = 100):
    """
    Obtiene ranking semanal
    
    Returns:
    {
        'week_start': '2025-12-02',
        'rankings': [
            {
                'rank': 1,
                'user_id': 'uuid',
                'username': 'Juan',
                'total_score': 1250,
                'batches_completed': 15
            },
            ...
        ]
    }
    """
    pass

@router.get("/leaderboard/endless")
async def get_endless_leaderboard(month_start: str = None, limit: int = 100):
    """
    Obtiene ranking endless mensual
    
    Returns:
    {
        'month_start': '2025-12-01',
        'rankings': [
            {
                'rank': 1,
                'user_id': 'uuid',
                'username': 'María',
                'best_streak': 45,
                'total_attempts': 12
            },
            ...
        ]
    }
    """
    pass
```

**Tareas**:
- [ ] Implementar GET /leaderboard/weekly
- [ ] Implementar GET /leaderboard/endless
- [ ] Cálculo de rankings
- [ ] Paginación
- [ ] Tests

---

### Etapa 6.3: Endpoints Admin ⏱️ 3 horas

```python
@router.get("/admin/config")
async def get_config(config_key: str = None):
    """Obtiene configuración del sistema"""
    pass

@router.put("/admin/config")
async def update_config(config_key: str, value: dict, version: int):
    """Actualiza configuración (requiere auth admin)"""
    pass

@router.get("/admin/stats")
async def get_system_stats():
    """Estadísticas generales del sistema"""
    pass
```

**Tareas**:
- [ ] Endpoints de configuración
- [ ] Autenticación admin
- [ ] Tests

---

## 📱 FASE 7: INTEGRACIÓN FRONTEND (r_pino)

### Etapa 7.1: Servicio de Comunicación ⏱️ 3-4 horas

**Archivo**: `services/gamification/GamificationServiceV2.ts`

```typescript
import { supabase } from '../supabase';

export interface BatchResponse {
    batch_id: string;
    operation: string;
    batch_type: string;
    exercises: Exercise[];
    central_level: number;
    is_miniboss: boolean;
}

export interface SubmitBatchResponse {
    score_earned: number;
    score_breakdown: object;
    correct_exercises: number;
    total_exercises: number;
    level_up: boolean;
    new_invisible_level: number;
    streak_updated: boolean;
    streak_days: number;
    practice_points_earned: number;
    chest_unlocked: boolean;
}

class GamificationServiceV2 {
    async startBatch(userId: string, operation: string): Promise<BatchResponse> {
        const response = await fetch(`${API_URL}/api/v2/batch/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, operation })
        });
        return response.json();
    }

    async submitBatch(batchId: string, userAnswers: any[]): Promise<SubmitBatchResponse> {
        const response = await fetch(`${API_URL}/api/v2/batch/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ batch_id: batchId, user_answers: userAnswers })
        });
        return response.json();
    }

    async getUserProgress(userId: string): Promise<any> {
        const response = await fetch(`${API_URL}/api/v2/progress/${userId}`);
        return response.json();
    }
}

export default new GamificationServiceV2();
```

**Tareas**:
- [ ] Crear GamificationServiceV2.ts
- [ ] Métodos para todos los endpoints
- [ ] Tipos TypeScript
- [ ] Manejo de errores

---

### Etapa 7.2: UI de Session Mejorada ⏱️ 6-8 horas

**Archivo**: `app/session-v2.tsx`

```typescript
import gamificationServiceV2 from '../services/gamification/GamificationServiceV2';

export default function SessionV2Screen() {
    const [batch, setBatch] = useState<BatchResponse | null>(null);
    const [currentExercise, setCurrentExercise] = useState(0);
    const [userAnswers, setUserAnswers] = useState<any[]>([]);
    const [startTime, setStartTime] = useState<number>(0);

    const startNewBatch = async () => {
        const batchData = await gamificationServiceV2.startBatch(user.id, 'suma');
        setBatch(batchData);
        setCurrentExercise(0);
        setUserAnswers([]);
        setStartTime(Date.now());
    };

    const submitAnswer = (answer: number) => {
        const timeTaken = (Date.now() - startTime) / 1000;
        const newAnswers = [...userAnswers, {
            exercise_id: batch.exercises[currentExercise].id,
            user_answer: answer,
            time_taken: timeTaken
        }];
        setUserAnswers(newAnswers);

        if (currentExercise < batch.exercises.length - 1) {
            setCurrentExercise(currentExercise + 1);
            setStartTime(Date.now());
        } else {
            finishBatch(newAnswers);
        }
    };

    const finishBatch = async (answers: any[]) => {
        const result = await gamificationServiceV2.submitBatch(batch.batch_id, answers);
        // Mostrar resultados, animaciones, etc.
    };

    // ... resto del componente
}
```

**Tareas**:
- [ ] Crear session-v2.tsx
- [ ] UI de ejercicios
- [ ] Barra de progreso del batch
- [ ] Timer por ejercicio
- [ ] Feedback visual
- [ ] Animaciones de transición
- [ ] Pantalla de resultados

---

### Etapa 7.3: UI de Miniboss ⏱️ 4-5 horas

**Archivo**: `app/miniboss-v2.tsx`

```typescript
export default function MinibossV2Screen() {
    // Componente especial para miniboss
    // - Indicadores de tiempo más estrictos
    // - Solo input abierto (sin opciones)
    // - Animación especial de ascenso si pasa
    // - Feedback de criterios cumplidos
}
```

**Tareas**:
- [ ] Crear miniboss-v2.tsx
- [ ] UI especializada
- [ ] Indicadores de criterios
- [ ] Animación de level-up
- [ ] Tests

---

### Etapa 7.4: UI de Endless Mode ⏱️ 4-5 horas

**Archivo**: `app/endless-v2.tsx`

```typescript
export default function EndlessV2Screen() {
    // Modo endless
    // - Un ejercicio a la vez
    // - Contador de streak en tiempo real
    // - Leaderboard integrado
    // - Termina al primer error
}
```

**Tareas**:
- [ ] Crear endless-v2.tsx
- [ ] Lógica de un ejercicio
- [ ] Contador de streak
- [ ] Integración con leaderboard
- [ ] Animaciones

---

### Etapa 7.5: Perfiles y Estadísticas ⏱️ 5-6 horas

**Archivo**: `app/profile-v2.tsx`

```typescript
export default function ProfileV2Screen() {
    // Panel de progreso completo
    // - Progreso por operación (solo nivel visible)
    // - Historial de batches
    // - Estadísticas de streak
    // - Puntos de práctica y cofres
    // - Tablas de clasificación
}
```

**Tareas**:
- [ ] Crear profile-v2.tsx
- [ ] Visualizaciones de progreso
- [ ] Gráficas de estadísticas
- [ ] Historial de batches
- [ ] Sistema de cofres
- [ ] Tests

---

## 🔄 FASE 8: MIGRACIÓN Y TESTING

### Etapa 8.1: Migración de Datos ⏱️ 6-8 horas

**Script**: `scripts/migrate_to_v2.py`

```python
"""
Script de migración de datos del sistema antiguo al nuevo

Mapeo:
- gamification_profile → user_operation_progress
- Calcular nivel invisible inicial basado en desempeño histórico
- Migrar historial de ejercicios a formato nuevo
"""

def migrate_user_progress():
    """Migra progreso de usuarios"""
    pass

def calculate_initial_invisible_level(user_id: str, operation: str) -> float:
    """Calcula nivel invisible inicial basado en historial"""
    pass

def validate_migration():
    """Valida que la migración fue exitosa"""
    pass
```

**Tareas**:
- [ ] Script de migración
- [ ] Cálculo de niveles invisibles iniciales
- [ ] Validación de integridad
- [ ] Rollback plan
- [ ] Tests

---

### Etapa 8.2: Testing A/B ⏱️ 4-5 horas

**Implementar**:
- [ ] Feature flags en BD
- [ ] Endpoint para asignar usuarios a grupos
- [ ] Dashboard de métricas
- [ ] Comparación de resultados

---

### Etapa 8.3: Optimización ⏱️ 3-4 horas

**Tareas**:
- [ ] Cacheo de configuraciones
- [ ] Índices de BD optimizados
- [ ] Queries optimizadas
- [ ] Pruebas de carga
- [ ] Monitoreo de performance

---

## ⏱️ ESTIMACIÓN TOTAL DE TIEMPO

### pineServer (Backend):
- **Fase 1**: 9-12 horas
- **Fase 2**: 12-15 horas
- **Fase 3**: 11-14 horas
- **Fase 4**: 8-11 horas
- **Fase 5**: 11-14 horas
- **Fase 6**: 9-11 horas
- **Subtotal Backend**: **60-77 horas**

### r_pino (Frontend):
- **Fase 7**: 22-28 horas
- **Subtotal Frontend**: **22-28 horas**

### Migración y Testing:
- **Fase 8**: 13-17 horas

### **TOTAL ESTIMADO: 95-122 horas** (12-15 días de trabajo intensivo)

---

## 📋 CHECKLIST DE INICIO

Antes de comenzar la implementación:

- [ ] Crear todas las tablas en Roble
- [ ] Poblar difficulty_levels con configuración inicial
- [ ] Poblar gamification_config con parámetros del sistema
- [ ] Crear estructura de carpetas en pineServer
- [ ] Instalar dependencias necesarias
- [ ] Configurar variables de entorno

---

## 🚦 NEXT STEPS

**¿Listo para comenzar?**

Sugerencia: Empezar con **Etapa 1.1: Estructura de Clases Base**

Esto establecerá los fundamentos del sistema y permitirá iterar rápidamente.

---

**Última actualización**: 2025-12-05  
**Autor**: Sistema de Gamificación V2  
**Estado**: Documento de planificación
