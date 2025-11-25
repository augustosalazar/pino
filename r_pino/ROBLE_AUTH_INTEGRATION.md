# Integración de Autenticación Roble con R_PINE

## Estado Actual

✅ **Backend preparado**: El endpoint `POST /api/users/ensure` crea automáticamente usuarios en `pine_users`

✅ **App funcional**: La app utiliza `AuthContext` para manejar el estado de autenticación y proteger rutas.

✅ **Servicio de Auth**: `services/auth.ts` maneja la comunicación con Roble Auth y sincroniza con `pine_users`.

## Estructura de Autenticación

### 1. Flujo Simplificado

El sistema ahora utiliza un enfoque directo:
1. **Roble Auth**: Maneja credenciales (email/password) y tokens (JWT).
2. **Pine Users**: Maneja datos de perfil y progreso del usuario.

**NO se utiliza** la tabla `company_id_user` ni el campo `company_id`.

### 2. Componentes Clave

#### A. AuthService (`services/auth.ts`)
Maneja:
- Login/Signup contra Roble Auth
- Almacenamiento local de tokens (AsyncStorage)
- Sincronización automática con `pine_users` vía `PineServerAPI.ensureUser`

#### B. AuthContext (`contexts/AuthContext.tsx`)
Provee:
- Estado global del usuario (`user`, `loading`)
- Métodos `login`, `signup`, `logout`
- Protección de navegación (redirige a `/login` si no está autenticado)

#### C. Login Screen (`app/login.tsx`)
- Interfaz para iniciar sesión o registrarse
- Maneja errores y estados de carga

### 3. Configuración Requerida

Asegúrate de tener las siguientes constantes configuradas en `services/auth.ts`:

```typescript
const ROBLE_PROJECT_ID = 'tracking_7d2ad2db74';
const ROBLE_BASE_URL = 'https://roble-api.openlab.uninorte.edu.co';
```

### 4. Flujo de Datos

#### Login
```
1. Usuario ingresa credenciales
2. POST /auth/login (Roble) → Recibe Tokens + UserID
3. POST /api/users/ensure (PineServer) → Sincroniza usuario en DB local
4. Guarda tokens en AsyncStorage
5. Actualiza estado global → Redirige a Home
```

#### Signup
```
1. Usuario ingresa datos
2. POST /auth/signup-direct (Roble) → Crea cuenta
3. POST /auth/login (Roble) → Obtiene tokens
4. POST /api/users/ensure (PineServer) → Crea perfil en DB local
5. Guarda tokens y actualiza estado
```

### 5. Uso en Componentes

```typescript
import { useAuth } from '../contexts/AuthContext';

export default function MyComponent() {
  const { user, logout } = useAuth();

  return (
    <View>
      <Text>Welcome, {user?.name}</Text>
      <Button onPress={logout} title="Logout" />
    </View>
  );
}
```

## Notas Importantes

- El `userId` es la fuente de verdad y es consistente entre Roble y PineServer.
- El nombre del usuario se almacena en `pine_users` y se recupera desde allí.
- Si el token expira, el `AuthContext` cerrará la sesión automáticamente.
