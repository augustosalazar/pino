# Cron Jobs para Sistema de Gamificación

## 🕐 Tareas Programadas

Este documento describe cómo configurar tareas automáticas para el mantenimiento del sistema de gamificación.

---

## 📋 Tareas Requeridas

### Diarias (Medianoche)
1. **Reset de PP diario** - Resetea `pp_dia` a 0
2. **Verificación de rachas** - Rompe rachas de usuarios inactivos

### Semanales (Lunes medianoche)
3. **Reset semanal** - Resetea `pp_semana` y `pd_semana` a 0

---

## 🐧 Linux/Mac - Crontab

### Configurar Crontab

```bash
# Editar crontab
crontab -e

# Agregar estas líneas:

# Tarea diaria a medianoche (reset PP + rachas)
0 0 * * * cd /path/to/pineServer && python gamification_admin.py daily >> logs/daily_task.log 2>&1

# Tarea semanal (lunes a medianoche)
0 0 * * 1 cd /path/to/pineServer && python gamification_admin.py weekly >> logs/weekly_task.log 2>&1
```

### Explicación del formato cron
```
*     *     *     *     *
│     │     │     │     │
│     │     │     │     └─── Día de la semana (0-7, 0 y 7 = domingo)
│     │     │     └─────---- Mes (1-12)
│     │     └───────────---- Día del mes (1-31)
│     └─────────────────---- Hora (0-23)
└───────────────────────---- Minuto (0-59)
```

### Ejemplos adicionales
```bash
# Solo reset de PP a las 00:00
0 0 * * * cd /path/to/pineServer && python gamification_admin.py reset-pp

# Solo verificar rachas a las 00:05
5 0 * * * cd /path/to/pineServer && python gamification_admin.py check-streaks

# Reset semanal (domingo a medianoche)
0 0 * * 0 cd /path/to/pineServer && python gamification_admin.py weekly
```

---

## 🪟 Windows - Task Scheduler

### Método 1: Interfaz Gráfica

1. **Abrir Task Scheduler**
   - Presiona `Win + R`
   - Escribe `taskschd.msc`
   - Presiona Enter

2. **Crear Tarea Básica**
   - Clic en "Create Basic Task"
   - Nombre: "Gamification Daily Reset"
   - Descripción: "Reset diario de PP y verificación de rachas"

3. **Trigger (Cuándo ejecutar)**
   - Selecciona "Daily"
   - Hora: 00:00:00
   - Repetir cada 1 día

4. **Action (Qué ejecutar)**
   - Acción: "Start a program"
   - Program/script: `C:\Path\To\Python\python.exe`
   - Arguments: `gamification_admin.py daily`
   - Start in: `C:\desarrollo\pino\pineServer`

5. **Repetir para tarea semanal**
   - Nombre: "Gamification Weekly Reset"
   - Trigger: Weekly, Monday, 00:00
   - Arguments: `gamification_admin.py weekly`

### Método 2: PowerShell Script

```powershell
# Guardar como: setup_gamification_tasks.ps1

# Tarea diaria
$dailyAction = New-ScheduledTaskAction -Execute "python.exe" `
    -Argument "gamification_admin.py daily" `
    -WorkingDirectory "C:\desarrollo\pino\pineServer"

$dailyTrigger = New-ScheduledTaskTrigger -Daily -At 00:00

Register-ScheduledTask -TaskName "Gamification Daily Reset" `
    -Action $dailyAction `
    -Trigger $dailyTrigger `
    -Description "Reset diario de PP y rachas"

# Tarea semanal
$weeklyAction = New-ScheduledTaskAction -Execute "python.exe" `
    -Argument "gamification_admin.py weekly" `
    -WorkingDirectory "C:\desarrollo\pino\pineServer"

$weeklyTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 00:00

Register-ScheduledTask -TaskName "Gamification Weekly Reset" `
    -Action $weeklyAction `
    -Trigger $weeklyTrigger `
    -Description "Reset semanal de PP y PD"

Write-Host "Tareas creadas exitosamente!"
```

Ejecutar como administrador:
```powershell
powershell -ExecutionPolicy Bypass -File setup_gamification_tasks.ps1
```

---

## 🐳 Docker - Cron Jobs

Si estás usando Docker, crea un servicio separado para cron jobs:

### docker-compose.yml
```yaml
services:
  # ... otros servicios ...

  gamification-cron:
    build: ./pineServer
    command: cron -f
    volumes:
      - ./pineServer:/app
      - ./pineServer/logs:/app/logs
    environment:
      - ROBLE_PROJECT_ID=${ROBLE_PROJECT_ID}
      - ROBLE_BASE_URL=${ROBLE_BASE_URL}
      - ADMIN_EMAIL=${ADMIN_EMAIL}
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
```

### Dockerfile para cron
```dockerfile
FROM python:3.9

WORKDIR /app

# Instalar cron
RUN apt-get update && apt-get install -y cron

# Copiar archivos
COPY . .

# Instalar dependencias
RUN pip install -r requirements.txt

# Copiar crontab
COPY crontab /etc/cron.d/gamification-cron
RUN chmod 0644 /etc/cron.d/gamification-cron
RUN crontab /etc/cron.d/gamification-cron

# Crear log file
RUN touch /var/log/cron.log

CMD ["cron", "-f"]
```

### Archivo crontab
```bash
# /etc/cron.d/gamification-cron
0 0 * * * cd /app && python gamification_admin.py daily >> /app/logs/daily.log 2>&1
0 0 * * 1 cd /app && python gamification_admin.py weekly >> /app/logs/weekly.log 2>&1
```

---

## 🧪 Testing de Tareas

### Probar manualmente
```bash
# Ejecutar tarea diaria
python gamification_admin.py daily

# Ejecutar tarea semanal
python gamification_admin.py weekly

# Ver info de tareas
python gamification_admin.py info
```

### Verificar logs (Linux/Mac)
```bash
# Ver logs de cron
tail -f /var/log/syslog | grep gamification

# Ver logs de la aplicación
tail -f logs/daily_task.log
tail -f logs/weekly_task.log
```

### Verificar logs (Windows)
```powershell
# Ver historial de tareas
Get-ScheduledTask -TaskName "Gamification*" | Get-ScheduledTaskInfo

# Ver logs en Event Viewer
eventvwr.msc
# Navegar a: Windows Logs > Application
# Filtrar por: Task Scheduler
```

---

## 📊 Monitoreo

### Crear endpoint de health check
Agregar a `main.py`:
```python
@app.get("/api/admin/last-reset")
async def get_last_reset():
    """
    Verifica cuándo fue el último reset
    """
    # Implementar lógica para verificar último reset
    # Por ejemplo, guardar timestamp en un archivo o DB
    pass
```

### Alertas
Configurar alertas si las tareas fallan:
- Email usando SMTP
- Webhook a Slack/Discord
- Logging a servicio externo (Sentry, etc.)

---

## ⚠️ Troubleshooting

### Cron no ejecuta
```bash
# Verificar que cron esté corriendo
sudo systemctl status cron

# Ver logs de cron
grep CRON /var/log/syslog

# Verificar permisos
ls -la /path/to/pineServer/gamification_admin.py
```

### Task Scheduler no ejecuta
1. Verificar que la tarea esté habilitada
2. Ejecutar manualmente para ver errores
3. Verificar permisos de usuario
4. Revisar Event Viewer para errores

### Variables de entorno no se cargan
```bash
# En el script de cron, cargar .env explícitamente
# Agregar al inicio del script:
export $(cat /path/to/pineServer/.env | xargs)
```

---

## 📝 Checklist de Implementación

- [ ] Instalar Python y dependencias
- [ ] Probar `python gamification_admin.py info`
- [ ] Crear directorio de logs: `mkdir logs`
- [ ] Configurar cron jobs / Task Scheduler
- [ ] Ejecutar tarea manual de prueba
- [ ] Verificar logs
- [ ] Configurar monitoreo/alertas (opcional)
- [ ] Documentar para el equipo

---

## 🔧 Configuración Recomendada

Para producción, se recomienda:

1. **Usar supervisor/systemd** (Linux) para mantener los procesos vivos
2. **Logging robusto** con rotación de archivos
3. **Alertas automáticas** en caso de fallo
4. **Backup** de la base de datos antes de resets
5. **Dry-run mode** para testing sin afectar datos

---

**Nota:** Asegúrate de que las variables de entorno estén configuradas correctamente para que `roble_client` funcione.
