# 🗄️ Migraciones para Roble - Sistema de Gamificación

## ⚠️ Limitaciones de Roble

Roble **NO soporta**:
- ❌ Funciones SQL
- ❌ Triggers
- ❌ CHECK constraints
- ❌ DEFAULT CURRENT_TIMESTAMP / NOW()
- ❌ BOOLEAN nativo

## ✅ Adaptaciones Realizadas

### 1. **Booleanos → INTEGER**
```sql
-- En vez de BOOLEAN
unlocked BOOLEAN DEFAULT FALSE

-- Usamos INTEGER
unlocked INTEGER DEFAULT 0  -- 0=false, 1=true
```

### 2. **Timestamps → TEXT**
```sql
-- En vez de TIMESTAMP DEFAULT CURRENT_TIMESTAMP
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

-- Usamos TEXT (ISO 8601)
created_at TEXT  -- "2024-11-30T10:15:00Z"
```

### 3. **Sin Funciones ni Triggers**
Toda la lógica se maneja en el **servidor**:
- Calcular niveles desde XP/PD
- Actualizar timestamps
- Crear perfiles de gamificación
- Validaciones

## 📁 Archivos de Migración

```
database_migrations/
├── README_ROBLE.md                        # Este archivo
├── 001_add_gamification_fields_roble.sql  # Tablas principales
├── 002_extend_pine_sessions_roble.sql     # Extensión de sessions
├── 003_extend_pine_records_roble.sql      # Extensión de records
└── 004_create_new_tables_roble.sql        # Tablas auxiliares
```

## 🚀 Ejecución

### En Roble Studio / Panel

Ejecuta **en orden**:

1. `001_add_gamification_fields_roble.sql`
2. `002_extend_pine_sessions_roble.sql`
3. `003_extend_pine_records_roble.sql`
4. `004_create_new_tables_roble.sql`

## 📊 Estructura de Tablas

### `pine_user_gamification`

| Campo | Tipo | Valor Inicial |
|-------|------|---------------|
| `user_ref` | TEXT PK | - |
| `pp_total, pp_dia, pp_semana` | INTEGER | 0 |
| `pd_global, pd_semana` | INTEGER | 0 |
| `xp_total` | INTEGER | 0 |
| `nivel_jugador` | INTEGER | 1 |
| `racha_dias` | INTEGER | 0 |
| `unlocked_*` | INTEGER | 0 (false) |
| `created_at, updated_at` | TEXT | NULL (servidor) |

### `pine_user_operations`

| Campo | Tipo | Valor Inicial |
|-------|------|---------------|
| `id` | INTEGER PK | AUTO |
| `user_ref` | TEXT | - |
| `operacion` | TEXT | 'suma', 'resta', 'mult', 'div' |
| `pd_operacion` | INTEGER | 0 |
| `nivel_dominio` | INTEGER | 0 |
| `unlocked` | INTEGER | 0 (false) |
| `miniboss_completed` | INTEGER | 0 (false) |
| `total_ejercicios, total_correctos` | INTEGER | 0 |
| `created_at, updated_at` | TEXT | NULL |

## 💻 Lógica en el Servidor

### 1. Crear Perfil de Gamificación

```typescript
// Al crear usuario
async function crearPerfilGamificacion(userRef: string) {
  const now = new Date().toISOString();
  
  // 1. Crear perfil
  await db.insert('pine_user_gamification', {
    user_ref: userRef,
    pp_total: 0,
    pp_dia: 0,
    pp_semana: 0,
    pd_global: 0,
    pd_semana: 0,
    xp_total: 0,
    nivel_jugador: 1,
    racha_dias: 0,
    unlocked_mix_suma_resta: 0,
    unlocked_mix_mult_div: 0,
    unlocked_speed: 0,
    unlocked_bosses: 0,
    unlocked_elite: 0,
    unlocked_master: 0,
    semana_inicio: now,
    created_at: now,
    updated_at: now
  });
  
  // 2. Crear 4 operaciones
  const operaciones = ['suma', 'resta', 'mult', 'div'];
  for (const op of operaciones) {
    await db.insert('pine_user_operations', {
      user_ref: userRef,
      operacion: op,
      pd_operacion: 0,
      nivel_dominio: op === 'suma' ? 1 : 0,
      unlocked: op === 'suma' ? 1 : 0,  // Solo suma desbloqueada
      miniboss_completed: 0,
      miniboss_attempts: 0,
      total_ejercicios: 0,
      total_correctos: 0,
      created_at: now,
      updated_at: now
    });
  }
}
```

### 2. Calcular Nivel de Jugador

```typescript
function calcularNivelJugador(xpTotal: number): number {
  let nivel = 1;
  while (xpTotal >= 50 * Math.pow(nivel + 1, 1.5)) {
    nivel++;
  }
  return nivel;
}

// Al actualizar XP
async function actualizarXP(userRef: string, xpGanado: number) {
  const user = await db.get('pine_user_gamification', { user_ref: userRef });
  const nuevoXP = user.xp_total + xpGanado;
  const nivelAnterior = user.nivel_jugador;
  const nivelNuevo = calcularNivelJugador(nuevoXP);
  
  let pdBonus = 0;
  if (nivelNuevo > nivelAnterior) {
    // Bonus por subir de nivel
    pdBonus = 20 * nivelNuevo;
  }
  
  await db.update('pine_user_gamification', 
    { user_ref: userRef },
    {
      xp_total: nuevoXP,
      nivel_jugador: nivelNuevo,
      pd_global: user.pd_global + pdBonus,
      pd_semana: user.pd_semana + pdBonus,
      updated_at: new Date().toISOString()
    }
  );
}
```

### 3. Calcular Nivel de Dominio

```typescript
function obtenerNivelDominio(pdOperacion: number): number {
  if (pdOperacion >= 140) return 5;
  if (pdOperacion >= 90) return 4;
  if (pdOperacion >= 50) return 3;
  if (pdOperacion >= 20) return 2;
  if (pdOperacion > 0) return 1;
  return 0;  // No desbloqueado
}

// Al actualizar PD de operación
async function actualizarPDOperacion(
  userRef: string, 
  operacion: string, 
  pdGanado: number
) {
  const op = await db.get('pine_user_operations', {
    user_ref: userRef,
    operacion: operacion
  });
  
  const nuevoPD = op.pd_operacion + pdGanado;
  const nivelAnterior = op.nivel_dominio;
  const nivelNuevo = obtenerNivelDominio(nuevoPD);
  
  await db.update('pine_user_operations',
    { user_ref: userRef, operacion: operacion },
    {
      pd_operacion: nuevoPD,
      nivel_dominio: nivelNuevo,
      updated_at: new Date().toISOString()
    }
  );
  
  // Si cambió de nivel, registrar en log
  if (nivelNuevo !== nivelAnterior) {
    await db.insert('pine_nivel_dominio_log', {
      user_ref: userRef,
      operacion: operacion,
      nivel_anterior: nivelAnterior,
      nivel_nuevo: nivelNuevo,
      pd_operacion: nuevoPD,
      fecha: new Date().toISOString()
    });
  }
}
```

### 4. Actualizar Racha

```typescript
async function actualizarRacha(userRef: string) {
  const user = await db.get('pine_user_gamification', { user_ref: userRef });
  const hoy = new Date().toISOString().split('T')[0];  // "2024-11-30"
  const ultimaRacha = user.racha_ultima_fecha;
  
  if (ultimaRacha === hoy) {
    // Ya se actualizó hoy
    return user.racha_dias;
  }
  
  const ayer = new Date();
  ayer.setDate(ayer.getDate() - 1);
  const ayerStr = ayer.toISOString().split('T')[0];
  
  let nuevaRacha = 1;
  if (ultimaRacha === ayerStr) {
    // Fue ayer, incrementar
    nuevaRacha = user.racha_dias + 1;
  }
  
  await db.update('pine_user_gamification',
    { user_ref: userRef },
    {
      racha_dias: nuevaRacha,
      racha_ultima_fecha: hoy,
      updated_at: new Date().toISOString()
    }
  );
  
  return nuevaRacha;
}
```

### 5. Reseteo Diario

```typescript
async function resetearDia() {
  const hoy = new Date().toISOString().split('T')[0];
  
  await db.execute(`
    UPDATE pine_user_gamification
    SET pp_dia = 0,
        pp_ultima_fecha = '${hoy}',
        updated_at = '${new Date().toISOString()}'
    WHERE pp_ultima_fecha < '${hoy}' OR pp_ultima_fecha IS NULL
  `);
}
```

### 6. Reseteo Semanal

```typescript
async function resetearSemana() {
  const now = new Date();
  const semanaId = getISOWeek(now);  // "2024-W48"
  const nowISO = now.toISOString();
  
  // 1. Guardar en leaderboard
  const usuarios = await db.query(`
    SELECT user_ref, pp_semana, pd_semana, semana_inicio
    FROM pine_user_gamification
    WHERE pp_semana > 0 OR pd_semana > 0
  `);
  
  for (const u of usuarios) {
    const score = (u.pp_semana * 0.4) + (u.pd_semana * 0.6);
    await db.insert('pine_weekly_leaderboard', {
      user_ref: u.user_ref,
      semana_id: semanaId,
      pp_semana: u.pp_semana,
      pd_semana: u.pd_semana,
      score_semanal: score,
      fecha_inicio: u.semana_inicio,
      fecha_fin: nowISO,
      created_at: nowISO,
      updated_at: nowISO
    });
  }
  
  // 2. Resetear contadores
  await db.execute(`
    UPDATE pine_user_gamification
    SET pp_semana = 0,
        pd_semana = 0,
        semana_inicio = '${nowISO}',
        updated_at = '${nowISO}'
  `);
}
```

## 🔄 Cronjobs

Configurar en el servidor:

```typescript
// Diario a las 00:00
cron.schedule('0 0 * * *', async () => {
  await resetearDia();
});

// Lunes a las 00:00
cron.schedule('0 0 * * 1', async () => {
  await resetearSemana();
});
```

## 🔍 Queries Útiles

### Obtener perfil completo

```typescript
const perfil = await db.get('pine_user_gamification', { user_ref: userId });
const operaciones = await db.query(`
  SELECT * FROM pine_user_operations 
  WHERE user_ref = ? 
  ORDER BY operacion
`, [userId]);
```

### Leaderboard actual

```typescript
const leaderboard = await db.query(`
  SELECT 
    g.user_ref,
    u.username,
    g.pp_semana,
    g.pd_semana,
    (g.pp_semana * 0.4 + g.pd_semana * 0.6) as score_semanal
  FROM pine_user_gamification g
  JOIN pine_users u ON g.user_ref = u.user_ref
  WHERE g.pp_semana > 0 OR g.pd_semana > 0
  ORDER BY score_semanal DESC
  LIMIT 10
`);
```

## ✅ Checklist Post-Migración

- [ ] Tablas creadas (001-004)
- [ ] Crear perfiles para usuarios existentes (desde servidor)
- [ ] Implementar funciones de cálculo en servidor
- [ ] Configurar cronjobs de reseteo
- [ ] Probar creación de usuario nuevo
- [ ] Probar actualización de puntos

---

**Versión**: 3.0-Roble  
**Compatibilidad**: Roble (sin funciones SQL)  
**Lógica**: 100% en servidor
