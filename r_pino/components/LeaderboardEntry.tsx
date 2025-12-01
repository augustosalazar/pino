import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { LeaderboardEntry as LeaderboardEntryType } from '../services/gamification/types';
import { LevelBadge, StreakIndicator } from './gamification';

interface LeaderboardEntryProps {
    entry: LeaderboardEntryType;
    isCurrentUser?: boolean;
    index: number;
}

export const LeaderboardEntry: React.FC<LeaderboardEntryProps> = ({
    entry,
    isCurrentUser = false,
    index,
}) => {
    const getRankColor = () => {
        switch (entry.rank) {
            case 1:
                return ['#FFD700', '#FFA500']; // Gold
            case 2:
                return ['#C0C0C0', '#A8A8A8']; // Silver
            case 3:
                return ['#CD7F32', '#A0522D']; // Bronze
            default:
                return ['rgba(79, 172, 254, 0.3)', 'rgba(0, 242, 254, 0.3)']; // Normal
        }
    };

    const getRankEmoji = () => {
        switch (entry.rank) {
            case 1:
                return '🥇';
            case 2:
                return '🥈';
            case 3:
                return '🥉';
            default:
                return '';
        }
    };

    const rankColors = getRankColor();
    const rankEmoji = getRankEmoji();

    return (
        <LinearGradient
            colors={isCurrentUser ? ['rgba(79, 172, 254, 0.4)', 'rgba(0, 242, 254, 0.4)'] : rankColors}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={[
                styles.container,
                isCurrentUser && styles.currentUserContainer,
            ]}
        >
            {/* Rank */}
            <View style={styles.rankContainer}>
                {rankEmoji ? (
                    <Text style={styles.rankEmoji}>{rankEmoji}</Text>
                ) : (
                    <Text style={styles.rankNumber}>#{entry.rank}</Text>
                )}
            </View>

            {/* User Info */}
            <View style={styles.userInfo}>
                <Text style={[styles.username, isCurrentUser && styles.currentUserText]} numberOfLines={1}>
                    {entry.username}
                    {isCurrentUser && ' (Tú)'}
                </Text>
                <View style={styles.stats}>
                    <View style={styles.statItem}>
                        <Text style={styles.statIcon}>💎</Text>
                        <Text style={styles.statValue}>{entry.pp_semana}</Text>
                    </View>
                    <View style={styles.statItem}>
                        <Text style={styles.statIcon}>🏆</Text>
                        <Text style={styles.statValue}>{entry.pd_semana}</Text>
                    </View>
                    {entry.racha_dias > 0 && (
                        <View style={styles.statItem}>
                            <Text style={styles.statIcon}>🔥</Text>
                            <Text style={styles.statValue}>{entry.racha_dias}</Text>
                        </View>
                    )}
                </View>
            </View>

            {/* Level & Score */}
            <View style={styles.rightSection}>
                <LevelBadge level={entry.nivel_jugador} size="small" />
                <Text style={styles.scoreValue}>{entry.score_semanal.toFixed(1)}</Text>
                <Text style={styles.scoreLabel}>Score</Text>
            </View>
        </LinearGradient>
    );
};

const styles = StyleSheet.create({
    container: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: 12,
        marginBottom: 8,
        borderRadius: 12,
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.2)',
    },
    currentUserContainer: {
        borderWidth: 2,
        borderColor: '#4facfe',
        shadowColor: '#4facfe',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.5,
        shadowRadius: 4,
        elevation: 4,
    },
    rankContainer: {
        width: 50,
        alignItems: 'center',
    },
    rankEmoji: {
        fontSize: 32,
    },
    rankNumber: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#FFFFFF',
    },
    userInfo: {
        flex: 1,
        marginLeft: 12,
    },
    username: {
        fontSize: 16,
        fontWeight: '600',
        color: '#FFFFFF',
        marginBottom: 4,
    },
    currentUserText: {
        color: '#FFD700',
        fontWeight: 'bold',
    },
    stats: {
        flexDirection: 'row',
        gap: 12,
    },
    statItem: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    statIcon: {
        fontSize: 12,
        marginRight: 4,
    },
    statValue: {
        fontSize: 12,
        color: 'rgba(255, 255, 255, 0.9)',
        fontWeight: '500',
    },
    rightSection: {
        alignItems: 'center',
        marginLeft: 12,
    },
    scoreValue: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#FFD700',
        marginTop: 4,
    },
    scoreLabel: {
        fontSize: 10,
        color: 'rgba(255, 255, 255, 0.7)',
    },
});

export default LeaderboardEntry;
