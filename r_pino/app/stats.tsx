import { View, Text, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { useState, useEffect } from 'react';
import { PineServerAPI } from '../services/api';
import { StatsResponse } from '../services/types';
import { StatusBar } from 'expo-status-bar';
import { useAuth } from '../contexts/AuthContext';

export default function StatsScreen() {
    const { user } = useAuth();
    const [stats, setStats] = useState<StatsResponse | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (user) {
            loadStats();
        }
    }, [user]);

    const loadStats = async () => {
        if (!user) return;

        try {
            const userStats = await PineServerAPI.getUserStats(user.id);
            setStats(userStats);
        } catch (error) {
            console.error('Failed to load stats:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <View style={styles.container}>
                <ActivityIndicator size="large" color="#007AFF" />
            </View>
        );
    }

    if (!stats) {
        return (
            <View style={styles.container}>
                <Text style={styles.errorText}>Failed to load statistics</Text>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <StatusBar style="auto" />

            <ScrollView contentContainerStyle={styles.content}>
                {/* Header */}
                <View style={styles.header}>
                    <Text style={styles.title}>Your Statistics</Text>
                    <Text style={styles.subtitle}>Track your progress</Text>
                </View>

                {/* Overall Stats */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Overall Performance</Text>

                    <View style={styles.statsGrid}>
                        <View style={styles.statCard}>
                            <Text style={styles.statValue}>{stats.current_score}</Text>
                            <Text style={styles.statLabel}>Total Score</Text>
                        </View>

                        <View style={styles.statCard}>
                            <Text style={styles.statValue}>{stats.total_sessions}</Text>
                            <Text style={styles.statLabel}>Sessions</Text>
                        </View>
                    </View>

                    <View style={styles.statsGrid}>
                        <View style={styles.statCard}>
                            <Text style={styles.statValue}>{stats.total_exercises}</Text>
                            <Text style={styles.statLabel}>Exercises</Text>
                        </View>

                        <View style={styles.statCard}>
                            <Text style={[styles.statValue, { color: getAccuracyColor(stats.accuracy) }]}>
                                {stats.accuracy.toFixed(1)}%
                            </Text>
                            <Text style={styles.statLabel}>Accuracy</Text>
                        </View>
                    </View>
                </View>

                {/* Difficulty by Operator */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Difficulty by Operator</Text>

                    {Object.entries(stats.difficulty_by_operator).map(([operator, difficulty]) => (
                        <View key={operator} style={styles.difficultyRow}>
                            <View style={styles.operatorBadge}>
                                <Text style={styles.operatorText}>{operator}</Text>
                            </View>

                            <View style={styles.difficultyBarContainer}>
                                <View
                                    style={[
                                        styles.difficultyBarFill,
                                        {
                                            width: `${Math.min((difficulty / 10) * 100, 100)}%`,
                                            backgroundColor: getDifficultyColor(difficulty)
                                        }
                                    ]}
                                />
                            </View>

                            <Text style={styles.difficultyValue}>{difficulty.toFixed(1)}</Text>
                        </View>
                    ))}
                </View>

                {/* Insights */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Insights</Text>

                    <View style={styles.insightCard}>
                        <Text style={styles.insightTitle}>🎯 Average Performance</Text>
                        <Text style={styles.insightText}>
                            You've completed {stats.total_sessions} session{stats.total_sessions !== 1 ? 's' : ''} with {stats.accuracy.toFixed(1)}% accuracy.
                        </Text>
                    </View>

                    <View style={styles.insightCard}>
                        <Text style={styles.insightTitle}>📈 Progress</Text>
                        <Text style={styles.insightText}>
                            {stats.accuracy >= 80
                                ? "Excellent work! You're mastering these exercises."
                                : stats.accuracy >= 60
                                    ? "Good progress! Keep practicing to improve further."
                                    : "Keep going! Consistent practice will help you improve."}
                        </Text>
                    </View>

                    <View style={styles.insightCard}>
                        <Text style={styles.insightTitle}>🏆 Total Score</Text>
                        <Text style={styles.insightText}>
                            You've earned {stats.current_score} points so far. Complete more sessions to increase your score!
                        </Text>
                    </View>
                </View>
            </ScrollView>
        </View>
    );
}

function getAccuracyColor(accuracy: number): string {
    if (accuracy >= 80) return '#34C759';
    if (accuracy >= 60) return '#007AFF';
    if (accuracy >= 40) return '#FF9500';
    return '#FF3B30';
}

function getDifficultyColor(difficulty: number): string {
    if (difficulty >= 7) return '#FF3B30';
    if (difficulty >= 5) return '#FF9500';
    if (difficulty >= 3) return '#007AFF';
    return '#34C759';
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#F5F5F7',
    },
    content: {
        padding: 20,
    },
    header: {
        marginTop: 20,
        marginBottom: 24,
    },
    title: {
        fontSize: 32,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 8,
    },
    subtitle: {
        fontSize: 16,
        color: '#666',
    },
    section: {
        marginBottom: 32,
    },
    sectionTitle: {
        fontSize: 20,
        fontWeight: '600',
        color: '#333',
        marginBottom: 16,
    },
    statsGrid: {
        flexDirection: 'row',
        gap: 12,
        marginBottom: 12,
    },
    statCard: {
        flex: 1,
        backgroundColor: 'white',
        borderRadius: 12,
        padding: 20,
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 2,
    },
    statValue: {
        fontSize: 32,
        fontWeight: 'bold',
        color: '#007AFF',
        marginBottom: 4,
    },
    statLabel: {
        fontSize: 14,
        color: '#999',
    },
    difficultyRow: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: 'white',
        borderRadius: 12,
        padding: 16,
        marginBottom: 12,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 2,
    },
    operatorBadge: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: '#007AFF',
        alignItems: 'center',
        justifyContent: 'center',
        marginRight: 16,
    },
    operatorText: {
        fontSize: 20,
        fontWeight: 'bold',
        color: 'white',
    },
    difficultyBarContainer: {
        flex: 1,
        height: 8,
        backgroundColor: '#E0E0E0',
        borderRadius: 4,
        overflow: 'hidden',
        marginRight: 16,
    },
    difficultyBarFill: {
        height: '100%',
    },
    difficultyValue: {
        fontSize: 16,
        fontWeight: '600',
        color: '#333',
        width: 40,
        textAlign: 'right',
    },
    insightCard: {
        backgroundColor: 'white',
        borderRadius: 12,
        padding: 20,
        marginBottom: 12,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 2,
    },
    insightTitle: {
        fontSize: 16,
        fontWeight: '600',
        color: '#333',
        marginBottom: 8,
    },
    insightText: {
        fontSize: 14,
        color: '#666',
        lineHeight: 20,
    },
    errorText: {
        fontSize: 16,
        color: '#999',
        textAlign: 'center',
    },
});
