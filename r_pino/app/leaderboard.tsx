import React, { useState, useEffect, useCallback } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    RefreshControl,
    ActivityIndicator,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { LeaderboardEntry } from '../components/LeaderboardEntry';
import gamificationService from '../services/gamification/GamificationService';
import { LeaderboardResponse } from '../services/gamification/types';

export default function LeaderboardScreen() {
    const [leaderboard, setLeaderboard] = useState<LeaderboardResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    // TODO: Get from auth context
    const userRef = 'current_user';

    const loadLeaderboard = useCallback(async () => {
        try {
            setLoading(true);
            const data = await gamificationService.getWeeklyLeaderboard(undefined, 50);
            setLeaderboard(data);
        } catch (error) {
            console.error('Error loading leaderboard:', error);
        } finally {
            setLoading(false);
        }
    }, []);

    const onRefresh = useCallback(async () => {
        setRefreshing(true);
        await loadLeaderboard();
        setRefreshing(false);
    }, [loadLeaderboard]);

    useEffect(() => {
        loadLeaderboard();
    }, [loadLeaderboard]);

    const userRank = leaderboard ? gamificationService.getUserRank(leaderboard, userRef) : null;

    if (loading && !leaderboard) {
        return (
            <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#FFD700" />
                <Text style={styles.loadingText}>Cargando ranking...</Text>
            </View>
        );
    }

    return (
        <LinearGradient colors={['#1a1a2e', '#16213e', '#0f3460']} style={styles.container}>
            <StatusBar style="light" />

            <ScrollView
                contentContainerStyle={styles.scrollContent}
                refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#FFD700" />}
            >
                {/* Header */}
                <View style={styles.header}>
                    <Text style={styles.title}>🏆 RANKING SEMANAL</Text>
                    <Text style={styles.subtitle}>
                        Top {leaderboard?.top_count || 50} jugadores esta semana
                    </Text>
                </View>

                {/* User Position Card (if not in top) */}
                {userRank && userRank > 10 && (
                    <View style={styles.userPositionCard}>
                        <Text style={styles.userPositionTitle}>Tu Posición</Text>
                        <Text style={styles.userPositionRank}>#{userRank}</Text>
                    </View>
                )}

                {/* Podium (Top 3) */}
                {leaderboard && leaderboard.leaderboard.length >= 3 && (
                    <View style={styles.podium}>
                        {/* 2nd Place */}
                        <View style={styles.podiumItem}>
                            <View style={[styles.podiumRank, styles.silverRank]}>
                                <Text style={styles.podiumNumber}>2</Text>
                            </View>
                            <Text style={styles.podiumName} numberOfLines={1}>
                                {leaderboard.leaderboard[1].username}
                            </Text>
                            <Text style={styles.podiumScore}>
                                {leaderboard.leaderboard[1].score_semanal.toFixed(1)}
                            </Text>
                        </View>

                        {/* 1st Place (Center, Larger) */}
                        <View style={[styles.podiumItem, styles.goldItem]}>
                            <Text style={styles.crownIcon}>👑</Text>
                            <View style={[styles.podiumRank, styles.goldRank]}>
                                <Text style={styles.podiumNumber}>1</Text>
                            </View>
                            <Text style={[styles.podiumName, styles.goldName]} numberOfLines={1}>
                                {leaderboard.leaderboard[0].username}
                            </Text>
                            <Text style={[styles.podiumScore, styles.goldScore]}>
                                {leaderboard.leaderboard[0].score_semanal.toFixed(1)}
                            </Text>
                        </View>

                        {/* 3rd Place */}
                        <View style={styles.podiumItem}>
                            <View style={[styles.podiumRank, styles.bronzeRank]}>
                                <Text style={styles.podiumNumber}>3</Text>
                            </View>
                            <Text style={styles.podiumName} numberOfLines={1}>
                                {leaderboard.leaderboard[2].username}
                            </Text>
                            <Text style={styles.podiumScore}>
                                {leaderboard.leaderboard[2].score_semanal.toFixed(1)}
                            </Text>
                        </View>
                    </View>
                )}

                {/* Full List */}
                <View style={styles.listSection}>
                    <Text style={styles.listTitle}>Clasificación Completa</Text>
                    {leaderboard?.leaderboard.map((entry, index) => (
                        <LeaderboardEntry
                            key={entry.user_ref}
                            entry={entry}
                            index={index}
                            isCurrentUser={entry.user_ref === userRef}
                        />
                    ))}
                </View>

                {/* Info Footer */}
                <View style={styles.infoFooter}>
                    <Text style={styles.infoText}>
                        Score = (40% × PP) + (60% × PD)
                    </Text>
                    <Text style={styles.infoText}>
                        Se reinicia cada semana
                    </Text>
                </View>
            </ScrollView>
        </LinearGradient>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1 },
    scrollContent: { padding: 20, paddingTop: 20, paddingBottom: 40 },
    loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#1a1a2e' },
    loadingText: { marginTop: 12, fontSize: 16, color: '#FFFFFF' },
    header: { alignItems: 'center', marginBottom: 24 },
    title: { fontSize: 32, fontWeight: 'bold', color: '#FFD700', marginBottom: 8 },
    subtitle: { fontSize: 16, color: 'rgba(255, 255, 255, 0.8)' },
    userPositionCard: { backgroundColor: 'rgba(79, 172, 254, 0.3)', borderRadius: 16, padding: 16, marginBottom: 24, alignItems: 'center', borderWidth: 2, borderColor: '#4facfe' },
    userPositionTitle: { fontSize: 14, color: 'rgba(255, 255, 255, 0.8)', marginBottom: 4 },
    userPositionRank: { fontSize: 32, fontWeight: 'bold', color: '#FFD700' },
    podium: { flexDirection: 'row', justifyContent: 'center', alignItems: 'flex-end', marginBottom: 32, gap: 12 },
    podiumItem: { alignItems: 'center', flex: 1 },
    goldItem: { marginBottom: 20 },
    podiumRank: { width: 60, height: 60, borderRadius: 30, justifyContent: 'center', alignItems: 'center', marginBottom: 8, borderWidth: 3 },
    goldRank: { backgroundColor: '#FFD700', borderColor: '#FFA500', width: 70, height: 70, borderRadius: 35 },
    silverRank: { backgroundColor: '#C0C0C0', borderColor: '#A8A8A8' },
    bronzeRank: { backgroundColor: '#CD7F32', borderColor: '#A0522D' },
    crownIcon: { fontSize: 24, marginBottom: 4 },
    podiumNumber: { fontSize: 24, fontWeight: 'bold', color: '#FFFFFF' },
    podiumName: { fontSize: 14, fontWeight: '600', color: '#FFFFFF', marginBottom: 4, textAlign: 'center' },
    goldName: { fontSize: 16, fontWeight: 'bold' },
    podiumScore: { fontSize: 18, fontWeight: 'bold', color: '#FFD700' },
    goldScore: { fontSize: 20 },
    listSection: { marginBottom: 24 },
    listTitle: { fontSize: 18, fontWeight: 'bold', color: '#FFFFFF', marginBottom: 16 },
    infoFooter: { backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 12, padding: 16, alignItems: 'center' },
    infoText: { fontSize: 13, color: 'rgba(255, 255, 255, 0.7)', marginBottom: 4 },
});
