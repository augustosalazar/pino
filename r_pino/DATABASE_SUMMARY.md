# 📊 Resumen Ejecutivo: Base de Datos para Sistema de Gamificación

## 🎯 Objetivo

Implementar el esquema de base de datos completo que soporte el sistema de gamificación con:
- PP (Puntos de Práctica)
- PD (Puntos de Dominio - global y por operación)
- XP y Niveles de Jugador
- Mini-jefes y desbloqueos
- Leaderboard semanal
- Gestión de items pendientes

---

## 📋 Resumen de Tablas

| Tabla | Tipo | Campos Agregados | Propósito |
|-------|------|------------------|-----------|
| `pine_users` | **MODIFICADA** | 40+ campos | Estado principal del jugador (PP, PD, XP, niveles, desbloqueos) |
| `pine_sessions` | **MODIFICADA** | 12 campos | Tracking de puntos y estadísticas por sesión |
| `pine_records` | **MODIFICADA** | 7 campos | Detalles por ítem (intentos, puntos, repetición) |
| `pine_pending_items` | **NUEVA** | - | Items que deben repetirse en siguiente batch |
| `pine_weekly_leaderboard` | **NUEVA** | - | Histórico del leaderboard semanal |
| `pine_nivel_dominio_log` | **NUEVA** | - | Log de cambios de nivel por operación |
| `pine_mini_jefes_intentos` | **NUEVA** | - | Registro de intentos de mini-jefes |

---

## 🔑 Campos Clave en `pine_users`

### Puntos de Práctica (PP)
```
pp_total: INT        -- Total histórico
pp_dia: INT          -- Diario (se resetea 00:00)
pp_semana: INT       -- Semanal (se resetea lunes 00:00)
pp_dia_max: INT      -- Límite diario (default 30)
```

### Puntos de Dominio (PD)
```
pd_global: INT       -- PD totales acumulados
pd_semana: INT       -- PD de la semana (reseteable)
pd_suma: INT         -- PD específicos de SUMA
pd_resta: INT        -- PD específicos de RESTA
pd_mult: INT         -- PD específicos de MULTIPLICACIÓN
pd_div: INT          -- PD específicos de DIVISIÓN
```

### XP y Nivel
```
xp_total: INT        -- XP acumulada
nivel_jugador: INT   -- Nivel tipo RPG (calculado auto desde XP)
```

### Rachas
```
racha_dias: INT      -- Días consecutivos con actividad
racha_ultima_fecha: DATE
```

### Desbloqueos
```
unlocked_suma: BOOL (always TRUE)
unlocked_resta: BOOL
unlocked_mult: BOOL
unlocked_div: BOOL

miniboss_suma_completed: BOOL
miniboss_mult_completed: BOOL
miniboss_div_completed: BOOL

unlocked_mix_suma_resta: BOOL
unlocked_mix_mult_div: BOOL
unlocked_speed: BOOL
unlocked_bosses: BOOL
unlocked_elite: BOOL
unlocked_master: BOOL
```

---

## 🎮 Lógica de Negocio Implementada

### 1. Cálculo de Nivel de Jugador

**Fórmula**: `XP_requerido(L) = 50 * L^1.5`

**Implementación**: Trigger automático
```sql
-- Se actualiza automáticamente cuando cambia xp_total
CREATE TRIGGER actualizar_nivel_jugador
BEFORE UPDATE OF xp_total ON pine_users
FOR EACH ROW
EXECUTE FUNCTION trigger_actualizar_nivel_jugador();
```

**Ejemplos**:
- Nivel 1 → 2: Requiere ~71 XP
- Nivel 2 → 3: Requiere ~141 XP  
- Nivel 3 → 4: Requiere ~224 XP

### 2. Niveles de Dominio por Operación

**Rangos**:
| Nivel | PD Requeridos | Nombre |
|-------|---------------|--------|
| 0 | No desbloqueado | - |
| 1 | 0-19 | Básico |
| 2 | 20-49 | Intermedio |
| 3 | 50-89 | Avanzado |
| 4 | 90-139 | Experto |
| 5 | ≥140 | Maestro |

**Implementación**: Vista calculada
```sql
CREATE VIEW pine_user_operation_levels AS
SELECT 
  user_ref,
  CASE 
    WHEN pd_suma >= 140 THEN 5
    WHEN pd_suma >= 90 THEN 4
    ...
  END as nivel_suma,
  -- Similar para resta, mult, div
FROM pine_users;
```

### 3. Score Semanal (Leaderboard)

**Fórmula**: `Score = (PP_semana * 0.4) + (PD_semana * 0.6)`

**Implementación**: Vista en tiempo real
```sql
CREATE VIEW pine_current_leaderboard AS
SELECT 
  user_ref,
  username,
  pp_semana,
  pd_semana,
  (pp_semana * 0.4 + pd_semana * 0.6) as score_semanal,
  RANK() OVER (ORDER BY score DESC) as ranking
FROM pine_users
WHERE pp_semana > 0 OR pd_semana > 0
ORDER BY score_semanal DESC;
```

### 4. Reseteos Automáticos

**Diario (00:00)**:
```sql
SELECT resetear_dia();
-- Resetea pp_dia a 0 para todos los usuarios
```

**Semanal (Lunes 00:00)**:
```sql
SELECT resetear_semana();
-- 1. Guarda datos en pine_weekly_leaderboard
-- 2. Calcula rankings
-- 3. Resetea pp_semana y pd_semana a 0
```

---

## 📈 Flujo de Datos en una Sesión

### Inicio de Sesión
```
1. Cliente: POST /sessions/start
2. Server crea registro en pine_sessions
3. Server obtiene pending_items del usuario
4. Server genera batch de 10 items (incluye pending + nuevos)
5. Retorna batch al cliente
```

### Durante la Sesión
```
1. Usuario responde cada item
2. Cliente rastrea:
   - Intento 1: correcto/incorrecto
   - Intento 2: correcto/incorrecto (si aplica)
   - Tiempo por item
3. Se marca items para repetición si fallan
```

### Completar Sesión
```
1. Cliente: POST /sessions/{id}/complete
2. Server procesa cada item:
   
   a) PP por item:
      - +1 PP por item mostrado
      - Verificar límite diario (pp_dia_max)
   
   b) PD por item:
      - Primer intento correcto: +2 PD (global + operación)
      - Reintento correcto: +1 PD (global + operación)
      - Doble fallo: 0 PD
      - Marca item para repetir si falló
   
   c) Guardar en pine_records:
      - fue_primer_intento
      - requirio_reintento
      - pp_ganados, pd_ganados
      - debe_repetirse
   
   d) Si item falló:
      - INSERT en pine_pending_items

3. Calcular XP del batch:
   XP = C * (3 + 0.5 * dificultad_media)
   
4. Aplicar bonus de batch:
   - Si ≥90% correctos: +5 PD
   - Si ≥70% correctos: +3 PD
   
5. Si es primer batch del día:
   - Actualizar racha: actualizar_racha(user_ref)
   - Si racha activa: +3 PD bonus

6. Actualizar pine_users:
   - pp_dia += pp_ganados (si <limite)
   - pp_semana += pp_ganados
   - pp_total += pp_ganados
   - pd_global += pd_batch (items + bonus + racha)
   - pd_semana += pd_batch
   - pd_[operacion] += pd_operacion (para cada op en batch)
   - xp_total += xp_batch

7. Triggers automáticos:
   - nivel_jugador se actualiza desde xp_total
   - Si cambió nivel: otorgar 20*L PD
   - Si cambió nivel de dominio: log en nivel_dominio_log

8. Verificar desbloqueos:
   - Operaciones (si cumple condiciones + mini-jefe)
   - Modos de juego (si cumple niveles)
   
9. Actualizar pine_sessions:
   - pp_ganados, pd_ganados, xp_ganados
   - bonus aplicados
   - estadísticas del batch
   
10. Retornar al cliente:
    - Estadísticas de la sesión
    - Puntos ganados
    - Niveles actualizados
    - Desbloqueos nuevos (si hay)
```

---

## 🏆 Mini-Jefes

### Datos Almacenados

En `pine_mini_jefes_intentos`:
```
- mini_jefe: 'suma', 'mult', 'div'
- exito: BOOL
- total_items, items_correctos
- porcentaje_acierto
- tiempo_total_segundos
- reintentos_usados
- operacion_desbloqueada (si exito)
- fecha
```

### Condiciones de Éxito

| Mini-jefe | Items | Tiempo | Acierto | Reintentos | Desbloquea |
|-----------|-------|--------|---------|------------|------------|
| SUMA | 15 | ≤60s | ≥70% | 0 | RESTA |
| MULT | 12 | ≤90s | ≥80% | - | - |
| DIV | 10 | - | ≥75% | 0 ayudas | - |

Al completar exitosamente:
```sql
UPDATE pine_users
SET 
  miniboss_[tipo]_completed = TRUE,
  unlocked_[operacion] = TRUE  -- según mini-jefe
WHERE user_ref = ?;

INSERT INTO pine_mini_jefes_intentos (...);
```

---

## 📊 Vistas Útiles

### 1. `pine_user_operation_levels`
Devuelve niveles 1-5 por operación + PD actuales

### 2. `pine_current_leaderboard`
Leaderboard en tiempo real con score y ranking

### 3. `pine_user_progress_summary`
Resumen completo:
- Puntos (PP, PD, XP)
- Niveles (jugador + por operación)
- Desbloqueos (operaciones + modos)
- XP para siguiente nivel
- % progreso al siguiente nivel

### 4. `pine_pending_items_summary`
Conteo de items pendientes por operación

---

## 🔄 Mantenimiento

### Cronjobs Requeridos

**1. Diario (00:00)**
```sql
SELECT resetear_dia();
```

**2. Semanal (Lunes 00:00)**
```sql
SELECT resetear_semana();
```

### Limpieza Periódica (Opcional)

**Items pendientes antiguos** (>30 días completados):
```sql
DELETE FROM pine_pending_items
WHERE completado = TRUE 
  AND fecha_fallo < NOW() - INTERVAL '30 days';
```

**Logs de nivel antiguos** (>90 días):
```sql
DELETE FROM pine_nivel_dominio_log
WHERE fecha < NOW() - INTERVAL '90 days';
```

---

## 🔐 Seguridad (RLS)

Para Supabase con Row Level Security:

```sql
-- Usuarios ven solo sus datos
CREATE POLICY "own_data" ON pine_users FOR SELECT 
USING (auth.uid()::text = user_ref);

CREATE POLICY "own_pending" ON pine_pending_items FOR SELECT
USING (auth.uid()::text = user_ref);

-- Leaderboard público
CREATE POLICY "public_leaderboard" ON pine_weekly_leaderboard FOR SELECT
TO authenticated USING (true);

-- Admins ven todo
CREATE POLICY "admin_all" ON pine_users FOR ALL
USING (
  EXISTS (
    SELECT 1 FROM pine_users 
    WHERE user_ref = auth.uid()::text AND user_type = 2
  )
);
```

---

## ✅ Checklist de Implementación

### Base de Datos
- [ ] Aplicar migración 001 (campos en pine_users)
- [ ] Aplicar migración 002 (extensión pine_sessions)
- [ ] Aplicar migración 003 (extensión pine_records)
- [ ] Aplicar migración 004 (tablas nuevas)
- [ ] Aplicar migración 005 (vistas)
- [ ] Aplicar migración 006 (funciones y triggers)
- [ ] Configurar cronjobs (diario y semanal)
- [ ] Configurar RLS policies (si aplica)
- [ ] Verificar índices creados
- [ ] Probar funciones con datos de ejemplo

### Servidor (Siguiente Paso)
- [ ] Actualizar endpoints de sesiones
- [ ] Implementar lógica de PP/PD/XP
- [ ] Implementar mini-jefes
- [ ] Implementar leaderboard
- [ ] Implementar gestión de items pendientes
- [ ] Actualizar generador de ejercicios
- [ ] Implementar verificación de desbloqueos

### App (Paso Final)
- [ ] Actualizar UI con puntos y niveles
- [ ] Implementar pantalla de progreso
- [ ] Implementar leaderboard
- [ ] Implementar mini-jefes
- [ ] Actualizar flujo de sesiones
- [ ] Animaciones de recompensas

---

## 📊 Métricas y KPIs

El sistema permite rastrear:

### Por Usuario
- Engagement: racha_dias, pp_dia, sesiones/día
- Progreso: nivel_jugador, niveles_operacion, pd_global
- Habilidad: PD vs PP ratio, % aciertos, tiempo promedio

### Por Cohorte
- Distribución de niveles
- Tasas de desbloqueo
- Tiempo promedio para alcanzar hitos
- Retención (racha promedio)

### Sistema Global
- Items pendientes totales
- Distribución en leaderboard
- Mini-jefes completados vs intentados
- Operaciones más/menos practicadas

---

## 🎯 Próximos Pasos

1. ✅ **COMPLETADO**: Esquema de base de datos diseñado
2. ⏭️ **SIGUIENTE**: Implementación en el servidor (PineServer)
3. ⏭️ **DESPUÉS**: Implementación en la app (r_pino)

📁 Ver:
- `SERVER_IMPLEMENTATION_PLAN.md` - Plan para el servidor
- `APP_IMPLEMENTATION_PLAN.md` - Plan para la app

---

**Status**: ✅ Base de datos lista para implementación  
**Versión**: 1.0.0  
**Fecha**: 2024-11-30
