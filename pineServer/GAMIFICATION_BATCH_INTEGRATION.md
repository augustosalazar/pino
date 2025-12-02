# Gamification-Aware Batch Generation

## 🎯 Overview

The exercise batch generator now **respects the gamification unlock system**, ensuring users only receive exercises for operations they've unlocked through gameplay progression.

---

## 🔄 How It Works

### **Before (Old System)**
❌ All users got the same distribution regardless of progress:
- 40% Addition (+)
- 20% Subtraction (-)
- 20% Multiplication (*)
- 20% Division (/)

**Problem**: New users would see multiplication and division before mastering basics!

### **After (New System)**
✅ Distribution adapts based on unlocked operations:
- **New user** (only suma): 100% addition
- **2 operations** unlocked: 60/40 split
- **3 operations** unlocked: 50/30/20 split
- **4 operations** unlocked: 40/25/20/15 split

---

## 📝 Implementation Details

### 1. **Updated Batch Generator**
📄 `/pineServer/generators/batch_generator.py`

```python
def generate_batch(
    self,
    difficulty_by_operator: Dict[str, float],
    num_exercises: int,
    unlocked_operations: List[str] = None  # ← NEW PARAMETER
) -> List[Exercise]:
```

**Key Features:**
- Accepts `unlocked_operations` list (e.g., `['+', '-']`)
- Filters operators to only include unlocked ones
- Dynamically adjusts distribution based on count
- Falls back to addition if no unlocks provided

### 2. **Updated Start Session Endpoint**
📄 `/pineServer/main.py` (lines 220-290)

```python
# Get unlocked operations from gamification system
unlocked_operations_names = await obtener_operaciones_disponibles(request.user_ref)
# Example: ['suma', 'resta']

# Map to operator symbols
unlocked_operators = ['+', '-']  # Based on above

# Pass to batch generator
exercises = container.batch_generator.generate_batch(
    difficulty_by_operator,
    num_new_exercises,
    unlocked_operations=unlocked_operators  # ← Respects unlocks
)
```

---

## 🎮 Progressive Unlock Flow

### **Level 1: New Player**
```
Unlocked: [suma]
Batch: 10 addition problems (100%)
```

### **Level 2: Unlocked Subtraction**
```
Unlocked: [suma, resta]
Batch: 6 addition (60%) + 4 subtraction (40%)
```

### **Level 3: Unlocked Multiplication**
```
Unlocked: [suma, resta, mult]
Batch: 5 addition (50%) + 3 subtraction (30%) + 2 multiplication (20%)
```

### **Level 4: All Operations**
```
Unlocked: [suma, resta, mult, div]
Batch: 4 addition (40%) + 2.5 subtraction (25%) + 2 multiplication (20%) + 1.5 division (15%)
```

---

## 🔧 Distribution Strategy

The `_create_distribution()` method implements smart splitting:

| # Unlocked | Distribution | Example (10 problems) |
|-----------|-------------|---------------------|
| 1 op | 100% | 10 of that operation |
| 2 ops | 60/40 | 6 primary + 4 secondary |
| 3 ops | 50/30/20 | 5 + 3 + 2 |
| 4 ops | 40/25/20/15 | 4 + 2.5 + 2 + 1.5 |

**Note:** Exercises are shuffled after distribution for randomness

---

## 🛡️ Safety Features

### **Fallback Protection**
```python
if not unlocked_operators:
    print("[WARNING] No operations unlocked, defaulting to addition")
    unlocked_operators = ['+']
```

Even if gamification data is missing, users will still get exercises (addition only).

### **Pending Items Filtering**
Only fetch pending items for **unlocked operations**:

```python
# OLD: Got pending items for ALL operations
for op_symbol, op_name in [('+', 'suma'), ('-', 'resta'), ('*', 'mult'), ('/', 'div')]:
    pending = await obtener_items_pendientes(...)

# NEW: Only unlocked operations
for op_name in unlocked_operations_names:
    pending = await obtener_items_pendientes(...)
```

---

## 🧪 Testing Examples

### **Test 1: New User (Only Suma)**
```python
unlocked = ['+']
batch = generate_batch(difficulty, 10, unlocked)
# Result: 10 addition problems
```

### **Test 2: Two Operations**
```python
unlocked = ['+', '-']
batch = generate_batch(difficulty, 10, unlocked)
# Result: ~6 addition + ~4 subtraction (shuffled)
```

### **Test 3: Legacy Mode (No Unlocks)**
```python
batch = generate_batch(difficulty, 10, unlocked_operations=None)
# Result: All 4 operations (backward compatible)
```

---

## 📊 Integration with Gamification

### **System Flow**
```
User starts session
    ↓
GET /api/sessions/start
    ↓
1. Fetch gamification profile
    ├─ obtener_operaciones_disponibles(user_ref)
    └─ Returns: ['suma', 'resta']
    ↓
2. Map to operator symbols
    └─ ['+', '-']
    ↓
3. Generate batch with unlocks
    ├─ Only uses: + and -
    ├─ Distribution: 60% + / 40% -
    └─ Shuffles for randomness
    ↓
4. Return exercises to user
```

---

## 🔑 Key Benefits

| Benefit | Description |
|---------|-------------|
| ✅ **Progressive Learning** | Users master basics before advanced ops |
| ✅ **Gamification Aligned** | Batch generation respects unlock system |
| ✅ **Dynamic Adaptation** | Distribution changes as user progresses |
| ✅ **Safety First** | Fallbacks prevent edge case failures |
| ✅ **Better UX** | No frustrating advanced problems too early |

---

## 📁 Modified Files

1. **`generators/batch_generator.py`**
   - Added `unlocked_operations` parameter
   - Implemented `_create_distribution()` method
   - Added operator filtering logic

2. **`main.py`** (start_session endpoint)
   - Fetch unlocked operations from gamification
   - Map Spanish names to symbols
   - Pass unlocks to batch generator
   - Filter pending items by unlocked ops

---

## 🚀 Deployment Notes

- **Backward Compatible**: If `unlocked_operations=None`, uses all operators
- **No Breaking Changes**: Existing code continues to work
- **Database Independent**: Works with or without gamification data

---

**Last Updated**: 2025-12-02
**Integration**: Gamification System v2.0
