import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import { getLocales } from 'expo-localization';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

import en from './locales/en.json';
import es from './locales/es.json';

const LANGUAGE_KEY = '@r_pino_language';

// Get device/browser language
const getBrowserLanguage = (): string => {
    // On web, check browser language first
    if (Platform.OS === 'web' && typeof navigator !== 'undefined') {
        const browserLang = navigator.language.split('-')[0]; // Get 'es' from 'es-MX'
        if (browserLang === 'en' || browserLang === 'es') {
            return browserLang;
        }
    }

    // Fallback to expo-localization
    const deviceLang = getLocales()[0]?.languageCode;
    if (deviceLang === 'en' || deviceLang === 'es') {
        return deviceLang;
    }

    // Default to Spanish
    return 'es';
};

const detectedLanguage = getBrowserLanguage();

// Configure i18next
i18n
    .use(initReactI18next)
    .init({
        compatibilityJSON: 'v3',
        resources: {
            en: { translation: en },
            es: { translation: es },
        },
        lng: detectedLanguage, // Will be overwritten by stored preference if exists
        fallbackLng: 'es', // Changed from 'en' to 'es' - Spanish is now default
        interpolation: {
            escapeValue: false, // React already escapes values
        },
        react: {
            useSuspense: false,
        },
    });

// Load saved language preference (AsyncStorage works on all platforms)
if (Platform.OS === 'web') {
    AsyncStorage.getItem(LANGUAGE_KEY).then((savedLanguage) => {
        if (savedLanguage && (savedLanguage === 'en' || savedLanguage === 'es')) {
            i18n.changeLanguage(savedLanguage);
        }
    }).catch(() => {
        // Ignore errors on initial load
    });
}

// Save language preference when changed
i18n.on('languageChanged', (lng: string) => {
    if (Platform.OS === 'web') {
        AsyncStorage.setItem(LANGUAGE_KEY, lng).catch(() => {
            // Ignore storage errors
        });
    }
});

export default i18n;

// Helper to change language
export const changeLanguage = async (languageCode: 'en' | 'es') => {
    await i18n.changeLanguage(languageCode);
};

// Helper to get current language
export const getCurrentLanguage = (): string => {
    return i18n.language;
};
