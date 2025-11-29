import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Appearance, ColorSchemeName } from 'react-native';

export type ThemeMode = 'light' | 'dark' | 'auto';

export interface Theme {
    // Background colors
    background: string;
    surface: string;
    surfaceSecondary: string;

    // Text colors
    text: string;
    textSecondary: string;
    textTertiary: string;

    // Primary colors
    primary: string;
    primaryLight: string;
    primaryDark: string;

    // UI elements
    border: string;
    divider: string;
    error: string;
    success: string;
    warning: string;

    // Card and shadows
    cardBackground: string;
    shadowColor: string;

    // Status bar
    statusBarStyle: 'light' | 'dark';
}

export const lightTheme: Theme = {
    background: '#F5F5F7',
    surface: '#FFFFFF',
    surfaceSecondary: '#F5F5F7',

    text: '#333333',
    textSecondary: '#666666',
    textTertiary: '#999999',

    primary: '#007AFF',
    primaryLight: '#5AC8FA',
    primaryDark: '#0051D5',

    border: '#E0E0E0',
    divider: '#E0E0E0',
    error: '#FF3B30',
    success: '#34C759',
    warning: '#FF9500',

    cardBackground: '#FFFFFF',
    shadowColor: '#000000',

    statusBarStyle: 'dark',
};

export const darkTheme: Theme = {
    background: '#000000',
    surface: '#1C1C1E',
    surfaceSecondary: '#2C2C2E',

    text: '#FFFFFF',
    textSecondary: '#ABABAB',
    textTertiary: '#6D6D6D',

    primary: '#0A84FF',
    primaryLight: '#5AC8FA',
    primaryDark: '#0051D5',

    border: '#38383A',
    divider: '#38383A',
    error: '#FF453A',
    success: '#32D74B',
    warning: '#FF9F0A',

    cardBackground: '#1C1C1E',
    shadowColor: '#000000',

    statusBarStyle: 'light',
};

interface ThemeContextType {
    theme: Theme;
    themeMode: ThemeMode;
    setThemeMode: (mode: ThemeMode) => Promise<void>;
    isDark: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const THEME_STORAGE_KEY = '@pino_theme_mode';

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [themeMode, setThemeModeState] = useState<ThemeMode>('auto');
    const [systemColorScheme, setSystemColorScheme] = useState<ColorSchemeName>(
        Appearance.getColorScheme()
    );

    // Load saved theme preference on mount
    useEffect(() => {
        loadThemePreference();

        // Listen for system theme changes
        const subscription = Appearance.addChangeListener(({ colorScheme }) => {
            setSystemColorScheme(colorScheme);
        });

        return () => subscription.remove();
    }, []);

    const loadThemePreference = async () => {
        try {
            const savedMode = await AsyncStorage.getItem(THEME_STORAGE_KEY);
            if (savedMode && (savedMode === 'light' || savedMode === 'dark' || savedMode === 'auto')) {
                setThemeModeState(savedMode as ThemeMode);
            }
        } catch (error) {
            console.error('Failed to load theme preference:', error);
        }
    };

    const setThemeMode = async (mode: ThemeMode) => {
        try {
            await AsyncStorage.setItem(THEME_STORAGE_KEY, mode);
            setThemeModeState(mode);
        } catch (error) {
            console.error('Failed to save theme preference:', error);
        }
    };

    // Determine the actual theme to use
    const getActiveTheme = (): Theme => {
        if (themeMode === 'auto') {
            return systemColorScheme === 'dark' ? darkTheme : lightTheme;
        }
        return themeMode === 'dark' ? darkTheme : lightTheme;
    };

    const theme = getActiveTheme();
    const isDark = theme === darkTheme;

    return (
        <ThemeContext.Provider value={{ theme, themeMode, setThemeMode, isDark }}>
            {children}
        </ThemeContext.Provider>
    );
};

export const useTheme = (): ThemeContextType => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
};
