import { Stack } from 'expo-router';
import { AuthProvider } from '../contexts/AuthContext';
import '../i18n'; // Initialize i18n

export default function RootLayout() {
    return (
        <AuthProvider>
            <Stack>
                <Stack.Screen name="login" options={{ headerShown: false }} />
                <Stack.Screen name="index" options={{ headerShown: false }} />
                <Stack.Screen name="session" options={{ title: 'Exercise Session', headerShown: false }} />
                <Stack.Screen name="results" options={{ title: 'Results', presentation: 'modal' }} />
                <Stack.Screen name="stats" options={{ title: 'Statistics' }} />
                <Stack.Screen name="profile" options={{ headerShown: false }} />
                <Stack.Screen name="(admin)" options={{ headerShown: false }} />
            </Stack>
        </AuthProvider>
    );
}
