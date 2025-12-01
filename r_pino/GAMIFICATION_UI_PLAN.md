# 🎮 Plan de Implementación UI - Sistema de Gamificación
## Diseño Inspirado en Clash Royale

**Fecha:** 1 de Diciembre, 2025  
**Objetivo:** Implementar UI de gamificación en r_pino con diseño tipo Clash Royale  
**Backend:** ✅ Completado (todas las fases)  

---

## 🎨 Principios de Diseño (Clash Royale Style)

### Visual
- **Colores vibrantes** con gradientes
- **Animaciones fluidas** y satisfactorias
- **Partículas y efectos** para recompensas
- **Cards/Tarjetas** con sombras y profundidad
- **Progreso visual** con barras y niveles

### UX
- **Feedback inmediato** en cada acción
- **Celebraciones** por logros
- **Acceso fácil** a información de progreso
- **Gamificación visible** en todo momento

---

## 📋 Fases de Implementación UI

### FASE 1: Fundamentos y Vista de Progreso (Sesión 1)
**Tiempo estimado:** 60-90 min

#### 1.1. Crear componentes base de gamificación ⏱️ 20 min
**Archivos a crear:**
- `components/gamification/ProgressBar.tsx` - Barra de progreso con animación
- `components/gamification/StatCard.tsx` - Tarjeta de estadística
- `components/gamification/LevelBadge.tsx` - Badge de nivel
- `components/gamification/RewardAnimation.tsx` - Animación de recompensas

**Características:**
- Gradientes y sombras tipo Clash Royale
- Animaciones con `react-native-reanimated`
- Iconos y efectos visuales

#### 1.2. Pantalla de Perfil Gamificado ⏱️ 30 min
**Archivo:** `app/gamification-profile.tsx`

**Contenido:**
```
┌─────────────────────────────────────┐
│   [Avatar]   NIVEL 5                │
│   Usuario123                        │
│   ████████░░ 450/500 XP             │
├─────────────────────────────────────┤
│  📊 Estadísticas Globales           │
│   PP: 120 | PD: 230 | Racha: 7🔥   │
├─────────────────────────────────────┤
│  Operaciones Desbloqueadas          │
│  ✅ SUMA      [Nivel 3] ████░░      │
│  ✅ RESTA     [Nivel 2] ███░░░      │
│  🔒 MULT      [Bloqueada]           │
│  🔒 DIV       [Bloqueada]           │
├─────────────────────────────────────┤
│  🏆 Score Semanal: 156.4            │
│  📈 Ranking: #23 de 150             │
└─────────────────────────────────────┘
```

**Elementos:**
- Header con nivel y avatar
- Barra de XP animada
- Stats cards (PP/PD/Racha)
- Lista de operaciones con progreso
- Score semanal destacado

#### 1.3. Widget de progreso en pantalla principal ⏱️ 20 min
**Modificar:** `app/index.tsx`

**Agregar:**
- Banner superior con nivel y XP
- Indicador de racha diaria
- Quick stats (PP hoy, PD totales)
- Botón de acceso a perfil completo

---

### FASE 2: Integración de Recompensas en Sesiones (Sesión 2)
**Tiempo estimado:** 90 min

#### 2.1. Pantalla de resultados mejorada ⏱️ 40 min
**Modificar:** `app/results.tsx`

**Nuevo diseño:**
```
┌─────────────────────────────────────┐
│        ⭐ ¡EXCELENTE! ⭐            │
│           8/10 correctas            │
├─────────────────────────────────────┤
│  Recompensas Ganadas:               │
│                                     │
│  💎 +10 PP                          │
│  🏆 +16 PD (+3 bonus batch)         │
│  ✨ +32 XP                          │
│  🔥 +3 PD (racha diaria)            │
│                                     │
│  [Animación de monedas cayendo]    │
├─────────────────────────────────────┤
│  Progreso:                          │
│  Nivel: 4 → 5! 🎉                  │
│  SUMA: Nivel 2 ████░░               │
│                                     │
│  Items para mejorar: 2              │
│  Los verás en tu próximo batch      │
├─────────────────────────────────────┤
│  [Continuar] [Ver Perfil Completo]  │
└─────────────────────────────────────┘
```

**Características:**
- Animación de entrada (fade + scale)
- Contadores animados para recompensas
- Efecto de partículas si hay level up
- Confetti si ≥90% acierto
- Mostrar desbloqueos si hubo

#### 2.2. Componentes de recompensas ⏱️ 30 min
**Archivos a crear:**
- `components/gamification/RewardCard.tsx`
- `components/gamification/LevelUpModal.tsx`
- `components/gamification/UnlockAnimation.tsx`

#### 2.3. Servicio de gamificación ⏱️ 20 min
**Archivo:** `services/gamification/GamificationService.ts`

**Funciones:**
```typescript
- getProfile(userRef): Promise<GamificationProfile>
- updateFromSession(sessionResult): void
- checkUnlocks(): UnlockInfo
- getWeeklyLeaderboard(): Promise<LeaderboardEntry[]>
```

---

### FASE 3: Mini-jefes UI (Sesión 3)
**Tiempo estimado:** 90 min

#### 3.1. Pantalla de mini-jefes ⏱️ 40 min
**Archivo:** `app/miniboss.tsx`

**Diseño:**
```
┌─────────────────────────────────────┐
│      🐉 MINI-JEFES DISPONIBLES      │
├─────────────────────────────────────┤
│  ┌───────────────────────────────┐  │
│  │  🐉 Mini-jefe de SUMA        │  │
│  │  Desbloquea: RESTA           │  │
│  │                              │  │
│  │  15 ejercicios en 60s        │  │
│  │  ≥70% acierto, 0 reintentos  │  │
│  │                              │  │
│  │  Requisitos:                 │  │
│  │  ✅ 30 PD Globales           │  │
│  │  ✅ Nivel 2 en SUMA          │  │
│  │                              │  │
│  │  [INTENTAR] (disponible)     │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  ⚔️ Mini-jefe de MULT        │  │
│  │  🔒 Bloqueado                │  │
│  │  Requiere RESTA desbloqueada │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

**Características:**
- Cards con sombras y gradientes
- Indicadores de requisitos (✅/❌)
- Estado del mini-jefe (disponible/bloqueado/completado)
- Animación de "pulso" si está disponible

#### 3.2. Sesión de mini-jefe ⏱️ 30 min
**Archivo:** `app/miniboss-session.tsx`

**Elementos especiales:**
- Timer prominente con cambio de color (verde→amarillo→rojo)
- Contador de aciertos actual
- NO permitir reintentos (UI bloqueada)
- Advertencias visuales al fallar

#### 3.3. Resultado de mini-jefe ⏱️ 20 min
**Archivo:** `app/miniboss-result.tsx`

**Diseño éxito:**
```
┌─────────────────────────────────────┐
│      🎊 ¡VICTORIA! 🎊              │
│                                     │
│  Mini-jefe de SUMA completado      │
│                                     │
│  14/15 correctas (93%)              │
│  Tiempo: 52.5s / 60s                │
│                                     │
│  [Animación épica de victoria]      │
│                                     │
│  🎁 RESTA DESBLOQUEADA! 🎁         │
│                                     │
│  [Continuar a Nueva Aventura]       │
└─────────────────────────────────────┘
```

**Diseño fallo:**
```
┌─────────────────────────────────────┐
│         😓 Casi lo logras           │
│                                     │
│  9/15 correctas (60%)               │
│  Necesitas ≥70%                     │
│                                     │
│  Sigue practicando SUMA             │
│  Actual: Nivel 2 (25 PD)            │
│  Necesitas: Nivel 2 (20 PD) ✅      │
│                                     │
│  [Reintentar] [Practicar Más]       │
└─────────────────────────────────────┘
```

---

### FASE 4: Leaderboard y Elementos Sociales (Sesión 4)
**Tiempo estimado:** 60 min

#### 4.1. Pantalla de leaderboard ⏱️ 40 min
**Archivo:** `app/leaderboard.tsx`

**Diseño:**
```
┌─────────────────────────────────────┐
│      🏆 RANKING SEMANAL 🏆          │
│      Score = 0.4×PP + 0.6×PD        │
├─────────────────────────────────────┤
│  [Global] [Mi Institución]          │
├─────────────────────────────────────┤
│  🥇 1. Usuario_A    Score: 285.6    │
│     [Nivel 8] 🔥 14 días            │
│                                     │
│  🥈 2. Usuario_B    Score: 267.2    │
│     [Nivel 7] 🔥 21 días            │
│                                     │
│  🥉 3. Usuario_C    Score: 251.8    │
│     [Nivel 6] 🔥 7 días             │
│                                     │
│  ...                                │
│                                     │
│  📍 23. TÚ          Score: 156.4    │
│     [Nivel 5] 🔥 7 días             │
│                                     │
│  ...                                │
└─────────────────────────────────────┘
```

**Características:**
- Top 3 con medallas especiales
- Highlight de posición del usuario
- Tabs para filtros
- Pull to refresh
- Animación al cargar

#### 4.2. Widget de racha en múltiples pantallas ⏱️ 20 min

- Agregar indicador de racha en header
- Animación de llama 🔥
- Tooltip explicativo

---

## 🎨 Paleta de Colores (Clash Royale Inspired)

```typescript
const GameColors = {
  // Primarios
  gold: '#FFD700',
  silver: '#C0C0C0',
  bronze: '#CD7F32',
  
  // Por nivel
  level1: '#8B4513', // Bronce
  level2: '#C0C0C0', // Plata
  level3: '#FFD700', // Oro
  level4: '#9370DB', // Púrpura
  level5: '#00CED1', // Turquesa brillante
  
  // Estados
  success: '#00FF00',
  warning: '#FFA500',
  danger: '#FF0000',
  
  // Fondos
  cardBg: 'rgba(30, 30, 50, 0.9)',
  overlayBg: 'rgba(0, 0, 0, 0.7)',
  
  // Gradientes
  xpGradient: ['#4facfe', '#00f2fe'],
  ppGradient: ['#43e97b', '#38f9d7'],
  pdGradient: ['#fa709a', '#fee140'],
  
  // Efectos
  glow: '#FFD700',
  shadow: 'rgba(0, 0, 0, 0.3)',
};
```

---

## 📦 Componentes a Crear

### Core Components
```
components/gamification/
├── ProgressBar.tsx           - Barra de progreso
├── StatCard.tsx              - Tarjeta de stat
├── LevelBadge.tsx            - Badge de nivel
├── RewardAnimation.tsx       - Animación de recompensa
├── RewardCard.tsx            - Card de recompensa
├── LevelUpModal.tsx          - Modal de level up
├── UnlockAnimation.tsx       - Animación de desbloqueo
├── StreakIndicator.tsx       - Indicador de racha
├── OperationCard.tsx         - Card de operación
├── MinibossCard.tsx          - Card de mini-jefe
└── LeaderboardEntry.tsx      - Entrada de leaderboard
```

### Screens
```
app/
├── gamification-profile.tsx  - Perfil completo
├── miniboss.tsx              - Lista de mini-jefes
├── miniboss-session.tsx      - Sesión de mini-jefe
├── miniboss-result.tsx       - Resultado de mini-jefe
└── leaderboard.tsx           - Leaderboard semanal
```

### Services
```
services/gamification/
├── GamificationService.ts    - Servicio principal
├── types.ts                  - TypeScript types
└── utils.ts                  - Utilidades
```

---

## 🔧 Dependencias Necesarias

```json
{
  "react-native-reanimated": "^3.x",  // Animaciones
  "react-native-svg": "^13.x",        // SVG para iconos
  "lottie-react-native": "^6.x",      // Animaciones Lottie
  "react-native-confetti-canvas": "^1.x" // Confetti
}
```

---

## ✅ Checklist de Implementación

### Fase 1: Fundamentos
- [ ] Crear componentes base
- [ ] Implementar pantalla de perfil
- [ ] Agregar widget en home
- [ ] Integrar con backend

### Fase 2: Recompensas
- [ ] Mejorar pantalla de resultados
- [ ] Crear animaciones de recompensas
- [ ] Implementar servicio de gamificación
- [ ] Probar level ups

### Fase 3: Mini-jefes
- [ ] Pantalla de lista de mini-jefes
- [ ] Sesión especial de mini-jefe
- [ ] Pantalla de resultados épica
- [ ] Integrar con desbloqueos

### Fase 4: Social
- [ ] Pantalla de leaderboard
- [ ] Indicadores de racha
- [ ] Filtros y tabs
- [ ] Pull to refresh

---

## 🎯 Prioridades para Primera Sesión

1. **Componentes base** (ProgressBar, StatCard, LevelBadge)
2. **Pantalla de perfil** completa
3. **Widget en home** para acceso rápido
4. **Integración básica** con backend

**Tiempo estimado:** 60-90 minutos  
**Objetivo:** Usuario puede ver su progreso completo de gamificación

---

**Siguiente sesión:** Fase 2 - Recompensas en sesiones
