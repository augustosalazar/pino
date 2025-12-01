import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, ScrollView } from 'react-native';
import { useRouter, Redirect } from 'expo-router';
import { useState, useEffect } from 'react';
import { PineServerAPI } from '../services/api';
import { StatsResponse } from '../services/types';
import { StatusBar } from 'expo-status-bar';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { AdaptiveContainer } from '../components/AdaptiveContainer';
import { useResponsive } from '../hooks/useResponsive';
import { Ionicons } from '@expo/vector-icons';
import { GamificationWidget } from '../components/GamificationWidget';

export default function HomeScreen() {
    const router = useRouter();
    const { user, logout } = useAuth();
    const { theme, isDark } = useTheme();
    const { isTabletOrDesktop, isDesktop } = useResponsive();
    const [stats, setStats] = useState<StatsResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (user) {
            loadUserStats();
        } else {
            setLoading(false);
        }
    }, [user]);

    const loadUserStats = async () => {
        if (!user) return;

        try {
            setError(null);
            // Ensure user exists in pine_users (double check)
            await PineServerAPI.ensureUser(user.id, user.email, user.name);

            // Load stats
            const userStats = await PineServerAPI.getUserStats(user.id);
            setStats(userStats);
        } catch (error) {
            console.error('Failed to load stats:', error);
            setError('Failed to load statistics. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleStartSession = () => {
        if (!user) return;
        router.push({
            pathname: '/session',
            params: { userRef: user.id }
        });
    };

    const handleViewStats = () => {
        router.push('/stats');
    };

    const handleLogout = async () => {
        await logout();
    };

    // Redirect admin users directly to admin tabs
    if (!loading && user?.user_type === 2) {
        return <Redirect href="/(admin)/stats" />;
    }

    if (loading && !stats) {
        return (
            <View style={[styles.container, { backgroundColor: theme.background }]}>
                <ActivityIndicator size="large" color={theme.primary} />
            </View>
        );
    }

    if (error) {
        return (
            <View style={[styles.container, { backgroundColor: theme.background }]}>
                <Text style={[styles.errorText, { color: theme.error }]}>{error}</Text>
                <TouchableOpacity style={[styles.retryButton, { backgroundColor: theme.primary }]} onPress={loadUserStats}>
                    <Text style={styles.retryButtonText}>Retry</Text>
                </TouchableOpacity>
            </View>
        );
    }

    return (
        <AdaptiveContainer centerOnDesktop={true} maxWidth={1000}>
            <ScrollView style={[styles.container, { backgroundColor: theme.background }]} contentContainerStyle={styles.contentContainer}>
                <StatusBar style={theme.statusBarStyle} />

                {/* Modern App Bar */}
                <View style={[styles.appBar, { backgroundColor: theme.primary }]}>
                    <View style={styles.appBarContent}>
                        <View style={styles.brandContainer}>
                            <View style={styles.logoContainer}>
                                <Ionicons name="calculator" size={28} color="#FFFFFF" />
                            </View>
                            <View>
                                <Text style={styles.appName}>Pino</Text>
                                <Text style={styles.appTagline}>{user?.institution_name || 'Math Training'}</Text>
                            </View>
                        </View>

                        <View style={styles.userSection}>
                            <TouchableOpacity onPress={() => router.push('/settings')} style={styles.iconButton}>
                                <Ionicons name="settings-outline" size={20} color="#FFFFFF" />
                            </TouchableOpacity>
                            <View style={styles.welcomeContainer}>
                                <Ionicons name="person-circle-outline" size={20} color="#FFFFFF" />
                                <Text style={styles.welcomeText}>Hi, {user?.name?.split(' ')[0] || 'User'}!</Text>
                            </View>
                            <TouchableOpacity onPress={handleLogout} style={styles.logoutButton}>
                                <Ionicons name="log-out-outline" size={20} color="#FFFFFF" />
                            </TouchableOpacity>
                        </View>
                    </View>
                </View>

                {/* Gamification Widget */}
                {user && (
                    <GamificationWidget
                        userRef={user.id}
                        compact={!isTabletOrDesktop}
                    />
                )}

                {/* Main Content */}
                <View style={styles.mainContentWrapper}>
                    {/* Main content grid for desktop */}
                    <View style={[styles.mainContent, isDesktop && styles.mainContentDesktop]}>
                        {/* Score Card */}
                        <View style={[styles.scoreCard, { backgroundColor: theme.cardBackground }, isDesktop && styles.scoreCardDesktop]}>
                            <Text style={[styles.scoreLabel, { color: theme.textSecondary }]}>Current Score</Text>
                            <Text style={[styles.scoreValue, { color: theme.primary }]}>{stats?.current_score || 0}</Text>

                            {stats && (
                                <View style={styles.statsRow}>
                                    <View style={styles.statItem}>
                                        <Text style={[styles.statValue, { color: theme.text }]}>{stats.total_sessions}</Text>
                                        <Text style={[styles.statLabel, { color: theme.textTertiary }]}>Sessions</Text>
                                    </View>
                                    <View style={[styles.statDivider, { backgroundColor: theme.divider }]} />
                                    <View style={styles.statItem}>
                                        <Text style={[styles.statValue, { color: theme.text }]}>{stats.accuracy.toFixed(1)}%</Text>
                                        <Text style={[styles.statLabel, { color: theme.textTertiary }]}>Accuracy</Text>
                                    </View>
                                    <View style={[styles.statDivider, { backgroundColor: theme.divider }]} />
                                    <View style={styles.statItem}>
                                        <Text style={[styles.statValue, { color: theme.text }]}>{stats.total_exercises}</Text>
                                        <Text style={[styles.statLabel, { color: theme.textTertiary }]}>Exercises</Text>
                                    </View>
                                </View>
                            )}
                        </View>

                        {/* Difficulty Preview */}
                        {stats && (
                            <View style={[styles.difficultyCard, { backgroundColor: theme.cardBackground }, isDesktop && styles.difficultyCardDesktop]}>
                                <Text style={[styles.cardTitle, { color: theme.text }]}>Current Difficulty</Text>
                                <View style={styles.difficultyGrid}>
                                    {Object.entries(stats.difficulty_by_operator).map(([op, diff]) => (
                                        <View key={op} style={styles.difficultyItem}>
                                            <Text style={[styles.operatorIcon, { color: theme.primary }]}>{op}</Text>
                                            <Text style={[styles.difficultyValue, { color: theme.textSecondary }]}>{diff.toFixed(1)}</Text>
                                        </View>
                                    ))}
                                </View>
                            </View>
                        )}
                    </View>

                    {/* Action Buttons */}
                    <View style={[styles.buttonContainer, isDesktop && styles.buttonContainerDesktop]}>
                        <TouchableOpacity
                            style={[styles.primaryButton, { backgroundColor: theme.primary }, isDesktop && styles.buttonDesktop]}
                            onPress={handleStartSession}
                        >
                            <Text style={styles.primaryButtonText}>Start New Session</Text>
                        </TouchableOpacity>

                        <TouchableOpacity
                            style={[styles.secondaryButton, { backgroundColor: theme.cardBackground, borderColor: theme.primary }, isDesktop && styles.buttonDesktop]}
                            onPress={handleViewStats}
                        >
                            <Text style={[styles.secondaryButtonText, { color: theme.primary }]}>View Statistics</Text>
                        </TouchableOpacity>

                        <TouchableOpacity
                            style={[styles.tertiaryButton, { backgroundColor: theme.cardBackground, borderColor: theme.border }, isDesktop && styles.buttonDesktop]}
                            onPress={() => router.push('/profile')}
                        >
                            <Ionicons name="person-outline" size={20} color={theme.primary} style={{ marginRight: 8 }} />
                            <Text style={[styles.tertiaryButtonText, { color: theme.primary }]}>Edit Profile</Text>
                        </TouchableOpacity>
                    </View>
                </View>
            </ScrollView>
        </AdaptiveContainer>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    contentContainer: {
        paddingBottom: 20,
    },
    // Modern App Bar Styles
    appBar: {
        paddingTop: 50,
        paddingBottom: 20,
        paddingHorizontal: 20,
        marginBottom: 24,
        borderBottomLeftRadius: 24,
        borderBottomRightRadius: 24,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.15,
        shadowRadius: 12,
        elevation: 8,
    },
    appBarContent: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    brandContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 12,
    },
    logoContainer: {
        width: 48,
        height: 48,
        borderRadius: 12,
        backgroundColor: 'rgba(255, 255, 255, 0.2)',
        alignItems: 'center',
        justifyContent: 'center',
    },
    appName: {
        fontSize: 28,
        fontWeight: 'bold',
        color: '#FFFFFF',
        letterSpacing: 0.5,
    },
    appTagline: {
        fontSize: 12,
        color: 'rgba(255, 255, 255, 0.8)',
        marginTop: -2,
    },
    userSection: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 12,
    },
    iconButton: {
        width: 36,
        height: 36,
        borderRadius: 18,
        backgroundColor: 'rgba(255, 255, 255, 0.2)',
        alignItems: 'center',
        justifyContent: 'center',
    },
    welcomeContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 6,
        backgroundColor: 'rgba(255, 255, 255, 0.15)',
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 20,
    },
    welcomeText: {
        fontSize: 14,
        fontWeight: '600',
        color: '#FFFFFF',
    },
    logoutButton: {
        width: 36,
        height: 36,
        borderRadius: 18,
        backgroundColor: 'rgba(255, 255, 255, 0.2)',
        alignItems: 'center',
        justifyContent: 'center',
    },
    mainContentWrapper: {
        paddingHorizontal: 20,
    },
    scoreCard: {
        borderRadius: 16,
        padding: 24,
        marginBottom: 16,
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 3,
    },
    scoreLabel: {
        fontSize: 14,
        marginBottom: 8,
    },
    scoreValue: {
        fontSize: 48,
        fontWeight: 'bold',
        marginBottom: 20,
    },
    statsRow: {
        flexDirection: 'row',
        alignItems: 'center',
        width: '100%',
        justifyContent: 'space-around',
    },
    statItem: {
        alignItems: 'center',
        flex: 1,
    },
    statValue: {
        fontSize: 20,
        fontWeight: '600',
    },
    statLabel: {
        fontSize: 12,
        marginTop: 4,
    },
    statDivider: {
        width: 1,
        height: 30,
    },
    difficultyCard: {
        borderRadius: 16,
        padding: 20,
        marginBottom: 24,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 3,
    },
    cardTitle: {
        fontSize: 16,
        fontWeight: '600',
        marginBottom: 16,
    },
    difficultyGrid: {
        flexDirection: 'row',
        justifyContent: 'space-around',
    },
    difficultyItem: {
        alignItems: 'center',
    },
    operatorIcon: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 8,
    },
    difficultyValue: {
        fontSize: 16,
    },
    primaryButton: {
        borderRadius: 12,
        padding: 18,
        alignItems: 'center',
        marginBottom: 12,
        flexDirection: 'row',
        justifyContent: 'center',
    },
    primaryButtonText: {
        color: 'white',
        fontSize: 18,
        fontWeight: '600',
    },
    secondaryButton: {
        borderRadius: 12,
        padding: 18,
        alignItems: 'center',
        borderWidth: 2,
        marginBottom: 12,
    },
    secondaryButtonText: {
        fontSize: 18,
        fontWeight: '600',
    },
    tertiaryButton: {
        borderRadius: 12,
        padding: 18,
        alignItems: 'center',
        borderWidth: 1,
        flexDirection: 'row',
        justifyContent: 'center',
    },
    tertiaryButtonText: {
        fontSize: 16,
        fontWeight: '600',
    },
    errorText: {
        fontSize: 16,
        textAlign: 'center',
        marginBottom: 20,
    },
    retryButton: {
        borderRadius: 12,
        padding: 16,
        alignItems: 'center',
        marginHorizontal: 40,
    },
    retryButtonText: {
        color: 'white',
        fontSize: 16,
        fontWeight: '600',
    },
    // Desktop responsive styles
    mainContent: {
        marginBottom: 24,
    },
    mainContentDesktop: {
        flexDirection: 'row',
        gap: 16,
        alignItems: 'flex-start',
    },
    scoreCardDesktop: {
        flex: 1,
        minHeight: 250,
    },
    difficultyCardDesktop: {
        flex: 1,
    },
    buttonContainer: {
        gap: 12,
    },
    buttonContainerDesktop: {
        flexDirection: 'row',
        gap: 16,
        maxWidth: 800,
    },
    buttonDesktop: {
        flex: 1,
        minWidth: 200,
    },
    // Admin Dashboard Styles
    adminDashboard: {
        flex: 1,
        padding: 24,
        alignItems: 'center',
        justifyContent: 'center',
    },
    adminWelcome: {
        alignItems: 'center',
        marginBottom: 32,
        paddingHorizontal: 20,
    },
    adminTitle: {
        fontSize: 28,
        fontWeight: 'bold',
        color: '#000',
        marginTop: 16,
        marginBottom: 8,
    },
    adminSubtitle: {
        fontSize: 16,
        color: '#666',
        textAlign: 'center',
        maxWidth: 400,
    },
    adminMainButton: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#007AFF',
        paddingVertical: 18,
        paddingHorizontal: 32,
        borderRadius: 16,
        gap: 12,
        width: '100%',
        maxWidth: 400,
        marginBottom: 12,
        shadowColor: '#007AFF',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 8,
        elevation: 5,
    },
    adminMainButtonText: {
        color: 'white',
        fontSize: 18,
        fontWeight: '600',
        flex: 1,
        textAlign: 'center',
    },
    adminSecondaryButton: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'white',
        paddingVertical: 16,
        paddingHorizontal: 28,
        borderRadius: 12,
        gap: 8,
        width: '100%',
        maxWidth: 400,
        borderWidth: 2,
        borderColor: '#007AFF',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 2,
    },
    adminSecondaryButtonText: {
        color: '#007AFF',
        fontSize: 16,
        fontWeight: '600',
    },
});
