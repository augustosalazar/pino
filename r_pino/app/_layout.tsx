import { Stack } from 'expo-router';
import { Platform } from 'react-native';
import { AuthProvider } from '../contexts/AuthContext';
import { ThemeProvider } from '../contexts/ThemeContext';
import '../i18n'; // Initialize i18n

export default function RootLayout() {
    // Hide back button on web
    const screenOptions = Platform.OS === 'web' ? {
        headerLeft: () => null,
    } : {};

    return (
        <ThemeProvider>
            <AuthProvider>
                <Stack screenOptions={screenOptions}>
                    <Stack.Screen name="login" options={{ headerShown: false }} />
                    <Stack.Screen name="index" options={{ headerShown: false }} />
                    <Stack.Screen name="session" options={{ title: 'Exercise Session', headerShown: false }} />
                    <Stack.Screen name="results" options={{ title: 'Results', presentation: 'modal', headerShown: false }} />
                    <Stack.Screen name="stats" options={{ headerShown: false }} />
                    <Stack.Screen name="profile" options={{ headerShown: false }} />
                    <Stack.Screen name="gamification-profile" options={{ headerShown: false }} />
                    <Stack.Screen name="settings" options={{ headerShown: false }} />
                    <Stack.Screen name="(admin)" options={{ headerShown: false }} />
                    <Stack.Screen name="miniboss" options={{ headerShown: false }} />
                    <Stack.Screen name="leaderboard" options={{ headerShown: false }} />
                </Stack>
            </AuthProvider>
        </ThemeProvider>
    );
}
