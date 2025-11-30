import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { useTheme, ThemeMode } from '../contexts/ThemeContext';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';

export default function SettingsScreen() {
    const router = useRouter();
    const { theme, themeMode, setThemeMode, isDark } = useTheme();

    const themeOptions: { value: ThemeMode; label: string; icon: string }[] = [
        { value: 'light', label: 'Light Mode', icon: 'sunny' },
        { value: 'dark', label: 'Dark Mode', icon: 'moon' },
        { value: 'auto', label: 'Auto (System)', icon: 'phone-portrait' },
    ];

    const handleThemeChange = async (mode: ThemeMode) => {
        await setThemeMode(mode);
    };

    return (
        <View style={[styles.container, { backgroundColor: theme.background }]}>
            <StatusBar style={theme.statusBarStyle} />

            <ScrollView contentContainerStyle={styles.content}>
                <View style={styles.header}>
                    <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
                        <Ionicons name="arrow-back" size={24} color={theme.primary} />
                    </TouchableOpacity>
                    <Text style={[styles.title, { color: theme.text }]}>Settings</Text>
                    <View style={{ width: 24 }} />
                </View>

                <View style={[styles.card, { backgroundColor: theme.cardBackground }]}>
                    <View style={styles.section}>
                        <Text style={[styles.sectionTitle, { color: theme.text }]}>
                            Appearance
                        </Text>
                        <Text style={[styles.sectionDescription, { color: theme.textSecondary }]}>
                            Choose your preferred theme
                        </Text>

                        <View style={styles.optionsContainer}>
                            {themeOptions.map((option) => (
                                <TouchableOpacity
                                    key={option.value}
                                    style={[
                                        styles.optionButton,
                                        {
                                            backgroundColor: theme.surface,
                                            borderColor: theme.border,
                                        },
                                        themeMode === option.value && {
                                            backgroundColor: theme.primary,
                                            borderColor: theme.primary,
                                        },
                                    ]}
                                    onPress={() => handleThemeChange(option.value)}
                                >
                                    <View style={styles.optionContent}>
                                        <Ionicons
                                            name={option.icon as any}
                                            size={24}
                                            color={
                                                themeMode === option.value
                                                    ? '#FFFFFF'
                                                    : theme.primary
                                            }
                                        />
                                        <Text
                                            style={[
                                                styles.optionLabel,
                                                {
                                                    color:
                                                        themeMode === option.value
                                                            ? '#FFFFFF'
                                                            : theme.text,
                                                },
                                            ]}
                                        >
                                            {option.label}
                                        </Text>
                                    </View>
                                    {themeMode === option.value && (
                                        <Ionicons
                                            name="checkmark-circle"
                                            size={24}
                                            color="#FFFFFF"
                                        />
                                    )}
                                </TouchableOpacity>
                            ))}
                        </View>
                    </View>

                    <View style={[styles.divider, { backgroundColor: theme.divider }]} />

                    <View style={styles.section}>
                        <Text style={[styles.sectionTitle, { color: theme.text }]}>
                            Preview
                        </Text>
                        <View style={[styles.previewCard, { backgroundColor: theme.surface }]}>
                            <View style={styles.previewHeader}>
                                <Ionicons name="calculator" size={32} color={theme.primary} />
                                <Text style={[styles.previewTitle, { color: theme.text }]}>
                                    Pino Math
                                </Text>
                            </View>
                            <Text style={[styles.previewText, { color: theme.textSecondary }]}>
                                This is how your app will look with the selected theme
                            </Text>
                            <View style={styles.previewButtons}>
                                <View
                                    style={[
                                        styles.previewButton,
                                        { backgroundColor: theme.primary },
                                    ]}
                                >
                                    <Text style={styles.previewButtonText}>Primary</Text>
                                </View>
                                <View
                                    style={[
                                        styles.previewButton,
                                        {
                                            backgroundColor: theme.surface,
                                            borderWidth: 1,
                                            borderColor: theme.border,
                                        },
                                    ]}
                                >
                                    <Text style={[styles.previewButtonText, { color: theme.text }]}>
                                        Secondary
                                    </Text>
                                </View>
                            </View>
                        </View>
                    </View>
                </View>

                <View style={styles.infoContainer}>
                    <Ionicons name="information-circle-outline" size={20} color={theme.textTertiary} />
                    <Text style={[styles.infoText, { color: theme.textTertiary }]}>
                        The 'Auto' mode will automatically switch between light and dark themes based
                        on your device's system settings.
                    </Text>
                </View>
            </ScrollView>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    content: {
        padding: 20,
        paddingTop: 20,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 24,
    },
    backButton: {
        padding: 8,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
    },
    card: {
        borderRadius: 16,
        padding: 24,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 3,
    },
    section: {
        marginBottom: 24,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: '600',
        marginBottom: 8,
    },
    sectionDescription: {
        fontSize: 14,
        marginBottom: 16,
    },
    optionsContainer: {
        gap: 12,
    },
    optionButton: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: 16,
        borderRadius: 12,
        borderWidth: 2,
    },
    optionContent: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 12,
    },
    optionLabel: {
        fontSize: 16,
        fontWeight: '500',
    },
    divider: {
        height: 1,
        marginBottom: 24,
    },
    previewCard: {
        padding: 20,
        borderRadius: 12,
        gap: 16,
    },
    previewHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 12,
    },
    previewTitle: {
        fontSize: 20,
        fontWeight: 'bold',
    },
    previewText: {
        fontSize: 14,
        lineHeight: 20,
    },
    previewButtons: {
        flexDirection: 'row',
        gap: 12,
    },
    previewButton: {
        flex: 1,
        paddingVertical: 12,
        borderRadius: 8,
        alignItems: 'center',
    },
    previewButtonText: {
        color: '#FFFFFF',
        fontWeight: '600',
    },
    infoContainer: {
        flexDirection: 'row',
        gap: 8,
        marginTop: 16,
        paddingHorizontal: 8,
    },
    infoText: {
        flex: 1,
        fontSize: 12,
        lineHeight: 18,
    },
});
