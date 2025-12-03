import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useTheme, ThemeMode } from '../contexts/ThemeContext';

export default function SettingsScreen() {
    const router = useRouter();
    const { themeMode, setThemeMode } = useTheme();

    const themeOptions: { value: ThemeMode; label: string; icon: string; gradient: [string, string] }[] = [
        { value: 'light', label: 'Modo Claro', icon: 'sunny', gradient: ['#FFD700', '#FFA500'] },
        { value: 'dark', label: 'Modo Oscuro', icon: 'moon', gradient: ['#4facfe', '#00f2fe'] },
        { value: 'auto', label: 'Auto (Sistema)', icon: 'phone-portrait', gradient: ['#f093fb', '#f5576c'] },
    ];

    const handleThemeChange = async (mode: ThemeMode) => {
        await setThemeMode(mode);
    };

    return (
        <LinearGradient colors={['#1a1a2e', '#16213e', '#0f3460']} style={styles.container}>
            <StatusBar style="light" />

            <ScrollView contentContainerStyle={styles.content}>
                {/* Header */}
                <View style={styles.header}>
                    <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
                        <Ionicons name="arrow-back" size={28} color="#FFD700" />
                    </TouchableOpacity>
                    <Text style={styles.title}>⚙️ AJUSTES</Text>
                    <View style={{ width: 28 }} />
                </View>

                {/* Theme Section */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Apariencia</Text>
                    <Text style={styles.sectionDescription}>
                        Elige tu tema preferido
                    </Text>

                    <View style={styles.optionsContainer}>
                        {themeOptions.map((option) => (
                            <TouchableOpacity
                                key={option.value}
                                style={styles.optionCard}
                                onPress={() => handleThemeChange(option.value)}
                                activeOpacity={0.7}
                            >
                                {themeMode === option.value ? (
                                    <LinearGradient
                                        colors={option.gradient}
                                        style={styles.optionGradient}
                                    >
                                        <View style={styles.optionContent}>
                                            <Ionicons name={option.icon as any} size={32} color="#FFFFFF" />
                                            <Text style={styles.optionLabelSelected}>{option.label}</Text>
                                        </View>
                                        <Ionicons name="checkmark-circle" size={28} color="#FFFFFF" />
                                    </LinearGradient>
                                ) : (
                                    <View style={styles.optionInactive}>
                                        <View style={styles.optionContent}>
                                            <Ionicons name={option.icon as any} size={32} color="rgba(255, 255, 255, 0.6)" />
                                            <Text style={styles.optionLabel}>{option.label}</Text>
                                        </View>
                                    </View>
                                )}
                            </TouchableOpacity>
                        ))}
                    </View>
                </View>

                {/* Info Section */}
                <View style={styles.infoCard}>
                    <Ionicons name="information-circle" size={24} color="#4facfe" />
                    <Text style={styles.infoText}>
                        El modo 'Auto' cambiará automáticamente entre los temas claro y oscuro según la configuración de tu dispositivo.
                    </Text>
                </View>

                {/* App Info */}
                <View style={styles.appInfo}>
                    <View style={styles.appInfoRow}>
                        <Ionicons name="calculator" size={40} color="#FFD700" />
                        <View style={styles.appInfoText}>
                            <Text style={styles.appName}>Pino Math</Text>
                            <Text style={styles.appTagline}>Sistema de Gamificación</Text>
                        </View>
                    </View>

                    <View style={styles.versionContainer}>
                        <Text style={styles.versionLabel}>Versión</Text>
                        <Text style={styles.versionNumber}>1.0.0</Text>
                    </View>
                </View>

                {/* Quick Actions */}
                <View style={styles.actionsGrid}>
                    <TouchableOpacity style={styles.actionCard} activeOpacity={0.7}>
                        <LinearGradient
                            colors={['rgba(79, 172, 254, 0.3)', 'rgba(0, 242, 254, 0.3)']}
                            style={styles.actionGradient}
                        >
                            <Ionicons name="help-circle" size={32} color="#4facfe" />
                            <Text style={styles.actionText}>Ayuda</Text>
                        </LinearGradient>
                    </TouchableOpacity>

                    <TouchableOpacity style={styles.actionCard} activeOpacity={0.7}>
                        <LinearGradient
                            colors={['rgba(245, 93, 251, 0.3)', 'rgba(245, 87, 108, 0.3)']}
                            style={styles.actionGradient}
                        >
                            <Ionicons name="document-text" size={32} color="#f093fb" />
                            <Text style={styles.actionText}>Términos</Text>
                        </LinearGradient>
                    </TouchableOpacity>

                    <TouchableOpacity style={styles.actionCard} activeOpacity={0.7}>
                        <LinearGradient
                            colors={['rgba(255, 215, 0, 0.3)', 'rgba(255, 165, 0, 0.3)']}
                            style={styles.actionGradient}
                        >
                            <Ionicons name="shield-checkmark" size={32} color="#FFD700" />
                            <Text style={styles.actionText}>Privacidad</Text>
                        </LinearGradient>
                    </TouchableOpacity>

                    <TouchableOpacity style={styles.actionCard} activeOpacity={0.7}>
                        <LinearGradient
                            colors={['rgba(67, 233, 123, 0.3)', 'rgba(56, 249, 215, 0.3)']}
                            style={styles.actionGradient}
                        >
                            <Ionicons name="mail" size={32} color="#43e97b" />
                            <Text style={styles.actionText}>Contacto</Text>
                        </LinearGradient>
                    </TouchableOpacity>
                </View>
            </ScrollView>
        </LinearGradient>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    content: {
        padding: 20,
        paddingTop: 20,
        paddingBottom: 40,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 32,
    },
    backButton: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        justifyContent: 'center',
        alignItems: 'center',
    },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        color: '#FFFFFF',
    },
    section: {
        marginBottom: 32,
    },
    sectionTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginBottom: 8,
    },
    sectionDescription: {
        fontSize: 14,
        color: 'rgba(255, 255, 255, 0.7)',
        marginBottom: 20,
    },
    optionsContainer: {
        gap: 12,
    },
    optionCard: {
        borderRadius: 16,
        overflow: 'hidden',
    },
    optionGradient: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: 20,
    },
    optionInactive: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: 20,
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: 16,
    },
    optionContent: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 16,
    },
    optionLabelSelected: {
        fontSize: 18,
        fontWeight: '600',
        color: '#FFFFFF',
    },
    optionLabel: {
        fontSize: 18,
        fontWeight: '600',
        color: 'rgba(255, 255, 255, 0.6)',
    },
    infoCard: {
        flexDirection: 'row',
        gap: 12,
        padding: 16,
        backgroundColor: 'rgba(79, 172, 254, 0.2)',
        borderRadius: 12,
        borderWidth: 1,
        borderColor: 'rgba(79, 172, 254, 0.4)',
        marginBottom: 32,
    },
    infoText: {
        flex: 1,
        fontSize: 13,
        color: 'rgba(255, 255, 255, 0.9)',
        lineHeight: 20,
    },
    appInfo: {
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        borderRadius: 16,
        padding: 20,
        marginBottom: 24,
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.1)',
    },
    appInfoRow: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 16,
        marginBottom: 16,
    },
    appInfoText: {
        flex: 1,
    },
    appName: {
        fontSize: 22,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginBottom: 4,
    },
    appTagline: {
        fontSize: 14,
        color: 'rgba(255, 255, 255, 0.7)',
    },
    versionContainer: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingTop: 16,
        borderTopWidth: 1,
        borderTopColor: 'rgba(255, 255, 255, 0.1)',
    },
    versionLabel: {
        fontSize: 14,
        color: 'rgba(255, 255, 255, 0.7)',
    },
    versionNumber: {
        fontSize: 16,
        fontWeight: '600',
        color: '#FFD700',
    },
    actionsGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 12,
    },
    actionCard: {
        width: '48%',
        borderRadius: 12,
        overflow: 'hidden',
    },
    actionGradient: {
        padding: 20,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.2)',
    },
    actionText: {
        fontSize: 14,
        fontWeight: '600',
        color: '#FFFFFF',
        marginTop: 8,
    },
});
