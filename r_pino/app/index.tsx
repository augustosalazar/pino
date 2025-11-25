import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { useState, useEffect } from 'react';
import { PineServerAPI } from '../services/api';
import { StatsResponse } from '../services/types';
import { StatusBar } from 'expo-status-bar';
import { useAuth } from '../contexts/AuthContext';

export default function HomeScreen() {
    const router = useRouter();
    const { user, logout } = useAuth();
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
        // Router will automatically redirect to login via AuthContext
    };

    if (loading && !stats) {
        return (
            <View style={styles.container}>
                <ActivityIndicator size="large" color="#007AFF" />
            </View>
        );
    }

    if (error) {
        return (
            <View style={styles.container}>
                <Text style={styles.errorText}>{error}</Text>
                <TouchableOpacity style={styles.retryButton} onPress={loadUserStats}>
                    <Text style={styles.retryButtonText}>Retry</Text>
                </TouchableOpacity>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <StatusBar style="auto" />

            {/* Header */}
            <View style={styles.header}>
                <View style={styles.headerTop}>
                    <Text style={styles.title}>R_PINE</Text>
                    <TouchableOpacity onPress={handleLogout} style={styles.logoutButton}>
                        <Text style={styles.logoutText}>Logout</Text>
                    </TouchableOpacity>
                </View>
                <Text style={styles.subtitle}>Welcome, {user?.name}</Text>
            </View>

            {/* Score Card */}
            <View style={styles.scoreCard}>
                <Text style={styles.scoreLabel}>Current Score</Text>
                <Text style={styles.scoreValue}>{stats?.current_score || 0}</Text>

                {stats && (
                    <View style={styles.statsRow}>
                        <View style={styles.statItem}>
                            <Text style={styles.statValue}>{stats.total_sessions}</Text>
                            <Text style={styles.statLabel}>Sessions</Text>
                        </View>
                        <View style={styles.statDivider} />
                        <View style={styles.statItem}>
                            <Text style={styles.statValue}>{stats.accuracy.toFixed(1)}%</Text>
                            <Text style={styles.statLabel}>Accuracy</Text>
                        </View>
                        <View style={styles.statDivider} />
                        <View style={styles.statItem}>
                            <Text style={styles.statValue}>{stats.total_exercises}</Text>
                            <Text style={styles.statLabel}>Exercises</Text>
                        </View>
                    </View>
                )}
            </View>

            {/* Difficulty Preview */}
            {stats && (
                <View style={styles.difficultyCard}>
                    <Text style={styles.cardTitle}>Current Difficulty</Text>
                    <View style={styles.difficultyGrid}>
                        {Object.entries(stats.difficulty_by_operator).map(([op, diff]) => (
                            <View key={op} style={styles.difficultyItem}>
                                <Text style={styles.operatorIcon}>{op}</Text>
                                <Text style={styles.difficultyValue}>{diff.toFixed(1)}</Text>
                            </View>
                        ))}
                    </View>
                </View>
            )}

            {/* Action Buttons */}
            <TouchableOpacity style={styles.primaryButton} onPress={handleStartSession}>
                <Text style={styles.primaryButtonText}>Start New Session</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.secondaryButton} onPress={handleViewStats}>
                <Text style={styles.secondaryButtonText}>View Statistics</Text>
            </TouchableOpacity>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#F5F5F7',
        padding: 20,
        paddingTop: 60,
    },
    header: {
        marginBottom: 30,
    },
    headerTop: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 8,
    },
    title: {
        fontSize: 42,
        fontWeight: 'bold',
        color: '#007AFF',
    },
    subtitle: {
        fontSize: 16,
        color: '#666',
        textAlign: 'center',
    },
    logoutButton: {
        padding: 8,
    },
    logoutText: {
        color: '#FF3B30',
        fontSize: 16,
        fontWeight: '600',
    },
    scoreCard: {
        backgroundColor: 'white',
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
        color: '#666',
        marginBottom: 8,
    },
    scoreValue: {
        fontSize: 48,
        fontWeight: 'bold',
        color: '#007AFF',
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
        color: '#333',
    },
    statLabel: {
        fontSize: 12,
        color: '#999',
        marginTop: 4,
    },
    statDivider: {
        width: 1,
        height: 30,
        backgroundColor: '#E0E0E0',
    },
    difficultyCard: {
        backgroundColor: 'white',
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
        color: '#333',
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
        color: '#007AFF',
        marginBottom: 8,
    },
    difficultyValue: {
        fontSize: 16,
        color: '#666',
    },
    primaryButton: {
        backgroundColor: '#007AFF',
        borderRadius: 12,
        padding: 18,
        alignItems: 'center',
        marginBottom: 12,
    },
    primaryButtonText: {
        color: 'white',
        fontSize: 18,
        fontWeight: '600',
    },
    secondaryButton: {
        backgroundColor: 'white',
        borderRadius: 12,
        padding: 18,
        alignItems: 'center',
        borderWidth: 2,
        borderColor: '#007AFF',
    },
    secondaryButtonText: {
        color: '#007AFF',
        fontSize: 18,
        fontWeight: '600',
    },
    errorText: {
        fontSize: 16,
        color: '#FF3B30',
        textAlign: 'center',
        marginBottom: 20,
    },
    retryButton: {
        backgroundColor: '#007AFF',
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
});
