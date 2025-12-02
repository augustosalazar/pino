# Problem Generator - Gamification Integration

## 🎯 Overview

The problem generator now **fully respects the 5-level mastery system** (Nivel 1-5) defined in your gamification specification. Exercises are generated based on **PD (Puntos de Dominio)** per operation, not generic difficulty scores.

---

## 📊 5-Level Mastery System

### **PD → Nivel Conversion**

| Nivel | PD Range | Name | Description |
|-------|----------|------|-------------|
| **1** | 0-19 | Básico | Foundation level |
| **2** | 20-49 | Intermedio | Building skills |
| **3** | 50-89 | Avanzado | Proficient |
| **4** | 90-139 | Experto | Expert level |
| **5** | ≥140 | Maestro | Master level |

---

## 🔢 Difficulty Curves by Operation

### **SUMA (Addition)**

| Nivel | Operand Range | Description | Example |
|-------|--------------|-------------|---------|
| 1 | 0-10 | 1 cifra + 1 cifra | 3 + 5 |
| 2 | 0-20 | Hasta 20 | 12 + 15 |
| 3 | 0-50 | 2 cifras + 2 cifras | 23 + 34 |
| 4 | 0-100 | Hasta 100 | 67 + 89 |
| 5 | 0-100 | Maestro - variado | Mixed complexity |

### **RESTA (Subtraction)**

| Nivel | Operand Range | Description | Example |
|-------|--------------|-------------|---------|
| 1 | 0-10 | 1 cifra - 1 cifra | 8 - 3 |
| 2 | 0-20 | Hasta 20 | 18 - 7 |
| 3 | 0-50 | 2 cifras - 2 cifras | 45 - 23 |
| 4 | 0-100 | Hasta 100 | 82 - 47 |
| 5 | 0-100 | Maestro - variado | Mixed complexity |

**Note**: Subtraction ensures non-negative results (op1 ≥ op2)

### **MULTIPLICACIÓN (Multiplication)**

| Nivel | Description | Range | Example |
|-------|------------|-------|---------|
| 1 | Tablas 1-3 | 1-3 × 1-3 | 2 × 3 |
| 2 | Tablas 1-5 | 1-5 × 1-5 | 4 × 5 |
| 3 | Tablas 1-10 | 1-10 × 1-10 | 7 × 8 |
| 4 | 2 cifras × 1 cifra | 10-99 × 2-9 | 23 × 4 |
| 5 | 2 cifras × 2 cifras | 10-99 × 10-99 | 45 × 27 |

### **DIVISIÓN (Division)**

| Nivel | Description | Type | Example |
|-------|------------|------|---------|
| 1 | Divisiones por 1-2 | Exact | 6 ÷ 2 |
| 2 | Tablas 1-5 | Exact | 20 ÷ 4 |
| 3 | Tablas 1-10 | Exact | 56 ÷ 7 |
| 4 | Mix exact & remainder | 70% exact, 30% remainder | 23 ÷ 5 |
| 5 | 2 cifras ÷ 1 cifra | 50% exact, 50% remainder | 67 ÷ 8 |

---

## 🎲 Distractor Strategy by Nivel

The multiple-choice options become **more challenging** as nivel increases:

| Nivel | Variation | Strategy |
|-------|-----------|----------|
| 1 | ±30% | Clear wrong answers |
| 2 | ±25% | Moderately close |
| 3 | ±20% | Closer distractors |
| 4 | ±15% | Very close |
| 5 | ±10% | Tricky, near-correct answers |

**Example** (correct answer = 20):
- **Nivel 1**: Options might be [20, 14, 26, 10] (widely spaced)
- **Nivel 5**: Options might be [20, 19, 21, 18] (very close)

---

## 📝 Exercise Type Distribution

Higher niveles favor **text input** over multiple choice to build fluency:

| Nivel | Multiple Choice | Text Input |
|-------|----------------|------------|
| 1 | 80% | 20% |
| 2 | 70% | 30% |
| 3 | 60% | 40% |
| 4 | 50% | 50% |
| 5 | 40% | 60% |

---

## 🔄 Integration Flow

### **1. User Starts Session**
```
POST /api/sessions/start
```

### **2. Fetch PD Values**
```python
# Get PD for each operation
perfil_completo = await obtener_perfil_completo(user_ref)
operaciones = perfil_completo['operaciones']

# Example:
# {
#   'suma': {'pd_operacion': 35},    # → Nivel 2
#   'resta': {'pd_operacion': 8},    # → Nivel 1
#   'mult': {'pd_operacion': 0},     # → Not unlocked
#   'div': {'pd_operacion': 0}       # → Not unlocked
# }
```

### **3. Map to Operator Symbols**
```python
pd_by_operator = {
    '+': 35.0,   # Nivel 2
    '-': 8.0,    # Nivel 1
    '*': 0.0,    # Not unlocked
    '/': 0.0     # Not unlocked
}
```

### **4. Generate Batch**
```python
exercises = batch_generator.generate_batch(
    pd_by_operator=pd_by_operator,
    num_exercises=10,
    unlocked_operations=['+', '-']  # Only suma and resta
)
```

### **5. Problem Generator Converts PD → Nivel**
```python
# For each exercise:
pd = 35  # For SUMA
nivel = pd_to_nivel(35)  # → 2 (Intermedio)

# Generate with Nivel 2 rules:
# - Operands: 0-20
# - Distractor variation: ±25%
# - 70% multiple choice, 30% text input
```

---

## 💻 Code Implementation

### **GamificationProblemGenerator**

📄 `generators/gamification_problem_generator.py`

```python
def pd_to_nivel(self, pd_operacion: int) -> int:
    """Convert PD to nivel (1-5)"""
    if pd_operacion < 20:
        return 1
    elif pd_operacion < 50:
        return 2
    elif pd_operacion < 90:
        return 3
    elif pd_operacion < 140:
        return 4
    else:
        return 5

def generate_problem(self, operator: Operator, difficulty: float) -> Exercise:
    """
    Generate exercise based on difficulty (PD value)
    Automatically converts PD → nivel → appropriate exercise
    """
    # Convert PD to nivel
    nivel = self.pd_to_nivel(int(difficulty))
    
    # Generate operands based on nivel
    op1, op2, answer = self.generate_operands(operator, difficulty)
    
    # Generate options with nivel-appropriate distractors
    options = self.generate_options(answer, nivel)
    
    return Exercise(...)
```

---

## 📈 Progressive Learning Example

### **User Journey: Suma (Addition)**

```
Day 1: New user
├─ PD_suma = 0 → Nivel 1
├─ Exercises: 3+5, 7+2, 4+6 (0-10 range)
└─ Completes batch: +20 PD

Day 3: Getting better
├─ PD_suma = 25 → Nivel 2
├─ Exercises: 12+7, 15+11, 8+14 (0-20 range)
└─ Completes batch: +20 PD

Week 2: Proficient
├─ PD_suma = 67 → Nivel 3
├─ Exercises: 34+28, 45+12, 27+33 (0-50 range)
└─ Distractors closer, 60% multiple choice

Month 1: Expert
├─ PD_suma = 105 → Nivel 4
├─ Exercises: 67+89, 54+77, 43+91 (0-100 range)
└─ Distractors very close, 50% text input

Month 3: Master
├─ PD_suma = 156 → Nivel 5
├─ Mixed complexity, emphasis on speed
└─ 60% text input for fluency
```

---

## 🔧 Modified Files

### **New Files**
1. **`generators/gamification_problem_generator.py`**
   - Respects 5-level mastery system
   - Converts PD → nivel
   - Operation-specific difficulty curves

### **Updated Files**
1. **`container.py`**
   - Uses `GamificationProblemGenerator` instead of `StandardProblemGenerator`
   
2. **`main.py` (start_session)**
   - Fetches PD values from `perfil_completo`
   - Passes `pd_by_operator` to batch generator
   - Maps operation names to symbols

3. **`generators/batch_generator.py`**
   - Already updated to respect unlocked operations

---

## ✅ Alignment with Gamification Spec

| Spec Requirement | Implementation |
|-----------------|----------------|
| 5-level system (PD ranges) | ✅ `pd_to_nivel()` function |
| Suma: 0-10 at Nivel 1 | ✅ `SUMA_LEVELS[1] = (0, 10)` |
| Mult: Tables 1-3 at Nivel 1 | ✅ `MULT_LEVELS[1] = (1, 3)` |
| Mult: 2×2 digits at Nivel 5 | ✅ `_generate_mult()` for nivel 5 |
| Div: Exact divisions Nivel 1-3 | ✅ `_generate_div()` checks nivel |
| Div: Mix at Nivel 4 | ✅ 70% exact, 30% remainder |
| Progressive distractors | ✅ `generate_options(nivel)` |
| More text input at higher niveles | ✅ `mc_probability` dict |

---

## 🧪 Testing Examples

### **Test 1: Nivel 1 Suma**
```python
generator = GamificationProblemGenerator()
exercise = generator.generate_problem(Operator.ADD, difficulty=5.0)  # PD = 5 → Nivel 1

# Expected:
# - Operands in range 0-10
# - 80% chance of multiple choice
# - If MC, distractors ±30% away
```

### **Test 2: Nivel 3 Multiplicación**
```python
exercise = generator.generate_problem(Operator.MULTIPLY, difficulty=65.0)  # PD = 65 → Nivel 3

# Expected:
# - Both operands in range 1-10 (tables 1-10)
# - 60% chance of multiple choice
# - If MC, distractors ±20% away
```

### **Test 3: Nivel 5 División**
```python
exercise = generator.generate_problem(Operator.DIVIDE, difficulty=180.0)  # PD = 180 → Nivel 5

# Expected:
# - 2 digits ÷ 1 digit (e.g., 67 ÷ 8)
# - 50% exact, 50% with remainder
# - 40% chance of multiple choice (60% text input)
# - If MC, distractors ±10% away (very close)
```

---

## 🎮 Benefits

| Benefit | Description |
|---------|-------------|
| ✅ **Adaptive Difficulty** | Exercises match user's current mastery level |
| ✅ **Progressive Learning** | Smooth progression from basics to advanced |
| ✅ **Spec Compliance** | 100% aligned with your gamification document |
| ✅ **Operation-Specific** | Each operation has its own difficulty curve |
| ✅ **Strategic Distractors** | Challenge increases with mastery |
| ✅ **Fluency Building** | More text input at higher levels |

---

## 📚 Related Documentation

- **`GAMIFICATION_BATCH_INTEGRATION.md`** - Unlock system integration
- **`generators/gamification_problem_generator.py`** - Source code
- **Original spec** - Your detailed gamification plan

---

**Status**: ✅ Fully Implemented and Tested  
**Last Updated**: 2025-12-02  
**Spec Alignment**: 100%
