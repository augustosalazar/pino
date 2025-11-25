# Internationalization (i18n) Setup Guide

## Overview
The R_PINE app now supports multiple languages! Text automatically adapts to the user's device language, with support for English and Spanish.

## Installation

### Step 1: Install Dependencies
Run this command to install the required i18n packages:

```bash
npm install
```

This will install:
- `i18next` - Core internationalization framework
- `react-i18next` - React bindings for i18next
- `expo-localization` - Device language detection

### Step 2: Verify Installation
Check that the packages are installed:
```bash
npm list i18next react-i18next expo-localization
```

## How It Works

### 1. Language Detection
The app automatically detects the user's device language on first launch:
- **English device** → App shows English
- **Spanish device** → App shows Spanish
- **Other languages** → Falls back to English

### 2. Language Storage
The selected language is saved to AsyncStorage, so it persists across app restarts.

### 3. Translation Files
Translations are stored in JSON files:
- `locales/en.json` - English translations
- `locales/es.json` - Spanish translations

## File Structure

```
r_pino/
├── locales/
│   ├── en.json          # English translations
│   └── es.json          # Spanish translations
├── i18n.ts              # i18n configuration
├── app/
│   ├── _layout.tsx      # ✅ Initializes i18n
│   ├── login.tsx        # ✅ Updated with translations
│   ├── index.tsx        # 🔄 Needs update (see below)
│   └── session.tsx      # 🔄 Needs update (see below)
```

## Screens Updated

### ✅ Login Screen (Complete)
All text has been replaced with translation keys:
- Welcome messages
- Form labels
- Button text
- Error messages

### 🔄 Remaining Screens
You need to manually update these screens:
1. **index.tsx** (Home Screen)
2. **session.tsx** (Exercise Session)
3. **results.tsx** (Results Screen - if exists)
4. **stats.tsx** (Statistics Screen - if exists)

## How to Use Translations in Code

### 1. Import the Hook
```typescript
import { useTranslation } from 'react-i18next';
```

### 2. Use in Component
```typescript
export default function MyScreen() {
    const { t } = useTranslation();
    
    return (
        <View>
            <Text>{t('common.loading')}</Text>
            <Text>{t('home.welcome', { name: 'User' })}</Text>
        </View>
    );
}
```

### 3. Translation Key Format
```typescript
t('category.key')              // Simple translation
t('category.key', { var })     // With variables
```

## Available Translation Keys

### Common
```typescript
t('common.logout')         // "Logout" / "Cerrar sesión"
t('common.loading')        // "Loading..." / "Cargando..."
t('common.error')          // "Error" / "Error"
t('common.retry')          // "Retry" / "Reintentar"
t('common.submit')         // "Submit" / "Enviar"
t('common.cancel')         // "Cancel" / "Cancelar"
```

### Auth (Login/Sign up)
```typescript
t('auth.welcomeBack')      // "Welcome Back"
t('auth.createAccount')    // "Create Account"  
t('auth.email')            // "Email"
t('auth.password')         // "Password"
t('auth.signIn')           // "Sign In"
// ... see locales/en.json for complete list
```

### Home Screen
```typescript
t('home.title')            // "R_PINE"
t('home.welcome', { name })// "Welcome, {name}"
t('home.currentScore')     // "Current Score"
t('home.sessions')         // "Sessions"
// ... see locales/en.json for complete list
```

### Session Screen
```typescript
t('session.solveThis')     // "Solve this:"
t('session.difficulty', { level }) // "Difficulty: {level}"
t('session.enterAnswer')   // "Enter your answer"
```

## Adding a New Language

### 1. Create Translation File
Create `locales/fr.json` (for French, for example):
```json
{
  "common": {
    "logout": "Déconnexion",
    "loading": "Chargement...",
    ...
  },
  ...
}
```

### 2. Register in i18n.ts
```typescript
import fr from './locales/fr.json';

i18n.init({
  resources: {
    en: { translation: en },
    es: { translation: es },
    fr: { translation: fr },  // Add this
  },
  ...
});
```

### 3. Update Type
```typescript
export const changeLanguage = async (languageCode: 'en' | 'es' | 'fr') => {
  await i18n.changeLanguage(languageCode);
};
```

## Manual Language Switching

To add a language selector in your app:

```typescript
import { changeLanguage, getCurrentLanguage } from '../i18n';

// In your component
const currentLang = getCurrentLanguage();

const switchToSpanish = () => {
  changeLanguage('es');
};

const switchToEnglish = () => {
  changeLanguage('en');
};
```

## Testing

### Test Different Languages

1. **Change Device Language**:
   - iOS: Settings → General → Language & Region
   - Android: Settings → System → Languages
   - Web: Browser settings

2. **Or Use Code**:
   ```typescript
   import { changeLanguage } from '../i18n';
   changeLanguage('es'); // Force Spanish
   changeLanguage('en'); // Force English
   ```

### Verify Translations
1. Start the app
2. Check that login screen shows correct language
3. Try changing device language
4. Restart app - should show new language

## Translation Guidelines

### DO ✅
- Use descriptive keys: `auth.emailPlaceholder` not `email1`
- Group by feature: `home.*`, `auth.*`, `session.*`
- Use interpolation for dynamic text: `{name}`, `{count}`
- Keep translations short and clear
- Test both languages

### DON'T ❌
- Hardcode text strings
- Use generic keys: `text1`, `label2`
- Forget to add to both language files
- Use complex HTML in translations
- Mix languages in same key

## Common Issues

### Issue: Translations not showing
**Solution**: Make sure you:
1. Installed packages: `npm install`
2. Imported i18n in `_layout.tsx`
3. Used `const { t } = useTranslation()` in component
4. Restarted development server

### Issue: "Cannot find module 'i18next'"
**Solution**: Run `npm install` to install dependencies

### Issue: Wrong language showing
**Solution**: 
1. Check device language settings
2. Clear AsyncStorage: `await AsyncStorage.removeItem('@r_pino_language')`
3. Restart app

## Next Steps

To complete the internationalization:

1. ✅ Install dependencies: `npm install`
2. 🔄 Update remaining screens (index, session, results, stats)
3. 🔄 Test both English and Spanish
4. 🔄 Add language selector UI (optional)
5. 🔄 Add more languages (optional)

## Example: Updating a Screen

Before:
```typescript
<Text>Welcome, {user.name}</Text>
<TouchableOpacity><Text>Start Session</Text></TouchableOpacity>
```

After:
```typescript
import { useTranslation } from 'react-i18next';

const { t } = useTranslation();

<Text>{t('home.welcome', { name: user.name })}</Text>
<TouchableOpacity><Text>{t('home.startNewSession')}</Text></TouchableOpacity>
```

## Resources

- [i18next Documentation](https://www.i18next.com/)
- [react-i18next Documentation](https://react.i18next.com/)
- [Expo Localization](https://docs.expo.dev/versions/latest/sdk/localization/)
