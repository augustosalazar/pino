import { View, Text, StyleSheet, ScrollView, ActivityIndicator, TouchableOpacity } from 'react-native';
import { useState, useEffect } from 'react';
import { PineServerAPI } from '../../services/api';
import { UserAnalyticsResponse } from '../../services/types';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';
import { useRouter } from 'expo-router';
import { LineChart } from 'react-native-gifted-charts';

export default function InstitutionAdminScreen() {
    const router = useRouter();
    const { user, logout } = useAuth();
    const [selectedUserRef, setSelectedUserRef] = useState<string | null>(null);
    const [analytics, setAnalytics] = useState<UserAnalyticsResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [users, setUsers] = useState<any[]>([]);
    const [showUserPicker, setShowUserPicker] = useState(false);

    useEffect(() => {
        if (user?.institution_ref) {
            loadInstitutionUsers();
        }
    }, [user]);

    const loadInstitutionUsers = async () => {
        if (!user?.institution_ref) return;

        try {
            // Note: Implement this endpoint on backend
            const institutionUsers = await PineServerAPI.getAllInstitutionUsers(user.institution_ref);
            setUsers(institutionUsers);
        } catch (error) {
            console.error('Failed to load users:', error);
        }
    };

    const loadUserAnalytics = async (userRef: string) => {
        setLoading(true);
        try {
            const data = await PineServerAPI.getUserAnalytics(userRef);
            setAnalytics(data);
            console.log('User analytics:', data);
            setSelectedUserRef(userRef);
        } catch (error) {
            console.error('Failed to load analytics:', error);
        } finally {
            setLoading(false);
        }
    };


    if (loading) {
        return (
            <View style={styles.centerContainer}>
                <ActivityIndicator size="large" color="#007AFF" />
            </View>
        );
    }

    return (
        <View style={styles.container}>

            {/* User Selector */}
            <TouchableOpacity
                style={styles.userSelector}
                onPress={() => setShowUserPicker(!showUserPicker)}
            >
                <Ionicons name="person" size={20} color="#007AFF" />
                <Text style={styles.selectorText}>
                    {selectedUserRef ? `User: ${selectedUserRef.substring(0, 8)}...` : 'Select a user'}
                </Text>
                <Ionicons name="chevron-down" size={20} color="#007AFF" />
            </TouchableOpacity>

            {/* User Picker */}
            {showUserPicker && (
                <ScrollView style={styles.userPicker}>
                    {users.map((u) => (
                        <TouchableOpacity
                            key={u.user_ref}
                            style={styles.userItem}
                            onPress={() => {
                                loadUserAnalytics(u.user_ref);
                                setShowUserPicker(false);
                            }}
                        >
                            <Text style={styles.userItemText}>{u.username || u.email}</Text>
                            <Text style={styles.userItemDetail}>
                                Grade {u.grade} • {u.age} years old
                            </Text>
                        </TouchableOpacity>
                    ))}
                </ScrollView>
            )}

            {/* Analytics Content */}
            {analytics && !showUserPicker && (
                <ScrollView style={styles.content}>
                    {/* Summary Cards */}
                    <View style={styles.summaryGrid}>
                        <View style={styles.summaryCard}>
                            <Text style={styles.summaryValue}>{analytics.total_sessions}</Text>
                            <Text style={styles.summaryLabel}>Sessions</Text>
                        </View>
                        <View style={styles.summaryCard}>
                            <Text style={[styles.summaryValue, { color: getAccuracyColor(analytics.overall_accuracy) }]}>
                                {analytics.overall_accuracy.toFixed(1)}%
                            </Text>
                            <Text style={styles.summaryLabel}>Accuracy</Text>
                        </View>
                        <View style={styles.summaryCard}>
                            <Text style={styles.summaryValue}>{analytics.current_score}</Text>
                            <Text style={styles.summaryLabel}>Score</Text>
                        </View>
                    </View>

                    {/* Difficulty by Operator */}
                    <View style={styles.section}>
                        <Text style={styles.sectionTitle}>Difficulty Progression</Text>

                        {Object.entries(analytics.operator_analytics).map(([operator, opAnalytics]) => (
                            <View key={operator} style={styles.operatorCard}>
                                <View style={styles.operatorHeader}>
                                    <View style={styles.operatorBadge}>
                                        <Text style={styles.operatorText}>{operator}</Text>
                                    </View>
                                    <Text style={styles.currentDifficulty}>
                                        Level {opAnalytics.current_difficulty.toFixed(1)}
                                    </Text>
                                </View>

                                <View style={styles.operatorStats}>
                                    <Text style={styles.statText}>
                                        {opAnalytics.total_correct}/{opAnalytics.total_attempts} correct
                                    </Text>
                                    <Text style={styles.statText}>
                                        {(opAnalytics.success_rate * 100).toFixed(0)}% success rate
                                    </Text>
                                </View>

                                {/* Difficulty History */}
                                {opAnalytics.difficulty_history.length > 0 && (
                                    <View style={styles.historySection}>
                                        <Text style={styles.historyTitle}>Recent Changes:</Text>
                                        {opAnalytics.difficulty_history.slice(-3).map((change, idx) => (
                                            <View key={idx} style={styles.historyItem}>
                                                <Text style={styles.historyChange}>
                                                    {change.previous_difficulty.toFixed(1)} → {change.new_difficulty.toFixed(1)}
                                                </Text>
                                                <Text style={styles.historyReason}>{change.reason}</Text>
                                            </View>
                                        ))}
                                    </View>
                                )}
                            </View>
                        ))}
                    </View>

                    {/* Recent Sessions */}
                    <View style={styles.section}>
                        <Text style={styles.sectionTitle}>Recent Sessions</Text>
                        {analytics.sessions_summary.slice(0, 5).map((session) => {
                            const startDate = new Date(session.started_at || session.created_at);
                            const endDate = new Date(session.completed_at || session.created_at);

                            // Format for Colombian time (UTC-5)
                            const colombianTime = startDate.toLocaleString('en-US', {
                                timeZone: 'America/Bogota',
                                month: 'short',
                                day: 'numeric',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit',
                                hour12: true
                            });

                            // Calculate duration in minutes
                            const durationMs = endDate.getTime() - startDate.getTime();
                            const durationMin = Math.round(durationMs / 1000 / 60);
                            const durationSec = Math.round((durationMs / 1000) % 60);

                            return (
                                <View key={session.session_id} style={styles.sessionCard}>
                                    <View style={styles.sessionHeader}>
                                        <Text style={styles.sessionDate}>
                                            {colombianTime}
                                        </Text>
                                        <View style={styles.durationBadge}>
                                            <Ionicons name="time-outline" size={14} color="#007AFF" />
                                            <Text style={styles.durationText}>
                                                {durationMin}m {durationSec}s
                                            </Text>
                                        </View>
                                    </View>
                                    <View style={styles.sessionStats}>
                                        <View style={styles.sessionStatItem}>
                                            <Ionicons name="checkmark-circle" size={16} color="#34C759" />
                                            <Text style={styles.sessionStat}>
                                                {session.correct_answers}/{session.total_exercises} correct
                                            </Text>
                                        </View>
                                        <View style={styles.sessionStatItem}>
                                            <Ionicons name="trophy" size={16} color="#FFB800" />
                                            <Text style={styles.sessionStat}>
                                                {session.score_earned} pts
                                            </Text>
                                        </View>
                                    </View>
                                    <View style={styles.sessionFooter}>
                                        <Text style={styles.sessionModel}>Model: {session.model_ref}</Text>
                                        <Text style={styles.sessionDifficulty}>
                                            Avg Difficulty: {session.avg_difficulty.toFixed(1)}
                                        </Text>
                                    </View>
                                </View>
                            );
                        })}
                    </View>
                </ScrollView>
            )}

            {/* Empty State */}
            {!analytics && !showUserPicker && (
                <View style={styles.emptyState}>
                    <Ionicons name="person-outline" size={64} color="#999" />
                    <Text style={styles.emptyText}>Select a user to view their progress</Text>
                </View>
            )}
        </View>
    );
}

function getAccuracyColor(accuracy: number): string {
    if (accuracy >= 80) return '#34C759';
    if (accuracy >= 60) return '#007AFF';
    if (accuracy >= 40) return '#FF9500';
    return '#FF3B30';
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#F5F5F7',
    },
    centerContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    header: {
        padding: 20,
        paddingTop: 60,
        backgroundColor: 'white',
        borderBottomWidth: 1,
        borderBottomColor: '#E5E5EA',
    },
    headerContent: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 12,
    },
    greetingSection: {
        flex: 1,
    },
    greeting: {
        fontSize: 20,
        fontWeight: '600',
        color: '#000',
    },
    institutionName: {
        fontSize: 14,
        color: '#8E8E93',
        marginTop: 2,
    },
    logoutButton: {
        padding: 8,
    },
    pageTitle: {
        fontSize: 28,
        fontWeight: 'bold',
        color: '#000',
    },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        color: '#000',
    },
    subtitle: {
        fontSize: 14,
        color: '#8E8E93',
        marginTop: 4,
    },
    userSelector: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: 16,
        margin: 16,
        backgroundColor: 'white',
        borderRadius: 12,
        gap: 12,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 2,
    },
    selectorText: {
        flex: 1,
        fontSize: 16,
        color: '#000',
    },
    userPicker: {
        maxHeight: 300,
        margin: 16,
        marginTop: 0,
        backgroundColor: 'white',
        borderRadius: 12,
    },
    userItem: {
        padding: 16,
        borderBottomWidth: 1,
        borderBottomColor: '#E5E5EA',
    },
    userItemText: {
        fontSize: 16,
        fontWeight: '600',
        color: '#000',
    },
    userItemDetail: {
        fontSize: 14,
        color: '#8E8E93',
        marginTop: 4,
    },
    content: {
        flex: 1,
        padding: 16,
    },
    summaryGrid: {
        flexDirection: 'row',
        gap: 12,
        marginBottom: 24,
    },
    summaryCard: {
        flex: 1,
        backgroundColor: 'white',
        borderRadius: 12,
        padding: 16,
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 2,
    },
    summaryValue: {
        fontSize: 28,
        fontWeight: 'bold',
        color: '#007AFF',
    },
    summaryLabel: {
        fontSize: 12,
        color: '#8E8E93',
        marginTop: 4,
    },
    section: {
        marginBottom: 24,
    },
    sectionTitle: {
        fontSize: 20,
        fontWeight: '600',
        color: '#000',
        marginBottom: 12,
    },
    operatorCard: {
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
    operatorHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 12,
    },
    operatorBadge: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: '#007AFF',
        alignItems: 'center',
        justifyContent: 'center',
    },
    operatorText: {
        fontSize: 20,
        fontWeight: 'bold',
        color: 'white',
    },
    currentDifficulty: {
        fontSize: 18,
        fontWeight: '600',
        color: '#000',
    },
    operatorStats: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        paddingVertical: 8,
        borderTopWidth: 1,
        borderTopColor: '#E5E5EA',
    },
    statText: {
        fontSize: 14,
        color: '#8E8E93',
    },
    historySection: {
        marginTop: 12,
        paddingTop: 12,
        borderTopWidth: 1,
        borderTopColor: '#E5E5EA',
    },
    historyTitle: {
        fontSize: 14,
        fontWeight: '600',
        color: '#000',
        marginBottom: 8,
    },
    historyItem: {
        marginBottom: 8,
    },
    historyChange: {
        fontSize: 14,
        fontWeight: '600',
        color: '#007AFF',
    },
    historyReason: {
        fontSize: 12,
        color: '#8E8E93',
        marginTop: 2,
    },
    sessionCard: {
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
    sessionHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 12,
        paddingBottom: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#E5E5EA',
    },
    sessionDate: {
        fontSize: 15,
        fontWeight: '600',
        color: '#000',
        flex: 1,
    },
    durationBadge: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#F0F8FF',
        paddingHorizontal: 10,
        paddingVertical: 6,
        borderRadius: 12,
        gap: 4,
    },
    durationText: {
        fontSize: 13,
        fontWeight: '600',
        color: '#007AFF',
    },
    sessionStats: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 12,
    },
    sessionStatItem: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 6,
    },
    sessionStat: {
        fontSize: 14,
        color: '#333',
        fontWeight: '500',
    },
    sessionFooter: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        paddingTop: 12,
        borderTopWidth: 1,
        borderTopColor: '#E5E5EA',
    },
    sessionModel: {
        fontSize: 12,
        color: '#8E8E93',
        fontWeight: '500',
    },
    sessionDifficulty: {
        fontSize: 12,
        color: '#8E8E93',
        fontWeight: '500',
    },
    sessionDuration: {
        fontSize: 12,
        color: '#8E8E93',
        marginTop: 8,
        fontStyle: 'italic',
    },
    emptyState: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    emptyText: {
        fontSize: 16,
        color: '#999',
        marginTop: 16,
    },
});
