import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { LevelBadge, ProgressBar, StreakIndicator } from './gamification';
import gamificationService from '../services/gamification/GamificationService';
import { GamificationProfile, calculateXPProgress } from '../services/gamification/types';

interface GamificationWidgetProps {
    userRef: string;
    compact?: boolean;
}

export const GamificationWidget: React.FC<GamificationWidgetProps> = ({
    userRef,
    compact = false,
}) => {
    const router = useRouter();
    const [profile, setProfile] = useState<GamificationProfile | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadProfile();
    }, [userRef]);

    const loadProfile = async () => {
        try {
            const data = await gamificationService.getProfile(userRef);
            setProfile(data);
        } catch (error) {
            console.error('[GamificationWidget] Error loading profile:', error);
        } finally {
            setLoading(false);
        }
    };

    const handlePress = () => {
        router.push('/gamification-profile');
    };

    if (loading) {
        return (
            <View style={[styles.container, styles.loadingContainer]}>
                <ActivityIndicator size="small" color="#4facfe" />
            </View>
        );
    }

    if (!profile) {
        return null;
    }

    const { perfil } = profile;
    const xpProgress = calculateXPProgress(perfil.xp_total, perfil.nivel_jugador);

    if (compact) {
        // Compact version - single row
        return (
            <TouchableOpacity onPress={handlePress} activeOpacity={0.9}>
                <LinearGradient
                    colors={['rgba(79, 172, 254, 0.15)', 'rgba(0, 242, 254, 0.15)']}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 0 }}
                    style={styles.compactContainer}
                >
                    <View style={styles.compactLeft}>
                        <LevelBadge level={perfil.nivel_jugador} size="small" />
                        <View style={styles.compactInfo}>
                            <Text style={styles.compactLevel}>Nivel {perfil.nivel_jugador}</Text>
                            <View style={styles.compactXPBar}>
                                <ProgressBar
                                    progress={xpProgress}
                                    color={['#4facfe', '#00f2fe']}
                                    height={6}
                                    animated={false}
                                />
                            </View>
                        </View>
                    </View>

                    <View style={styles.compactStats}>
                        <View style={styles.compactStat}>
                            <Text style={styles.compactStatValue}>{perfil.pp_dia}</Text>
                            <Text style={styles.compactStatLabel}>💎</Text>
                        </View>
                        <View style={styles.compactStat}>
                            <Text style={styles.compactStatValue}>{perfil.pd_global}</Text>
                            <Text style={styles.compactStatLabel}>🏆</Text>
                        </View>
                        {perfil.racha_dias > 0 && (
                            <View style={styles.compactStat}>
                                <Text style={styles.compactStatValue}>{perfil.racha_dias}</Text>
                                <Text style={styles.compactStatLabel}>🔥</Text>
                            </View>
                        )}
                    </View>
                </LinearGradient>
            </TouchableOpacity>
        );
    }

    // Full version - multi-row
    return (
        <TouchableOpacity onPress={handlePress} activeOpacity={0.9}>
            <LinearGradient
                colors={['rgba(79, 172, 254, 0.2)', 'rgba(0, 242, 254, 0.2)']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={styles.fullContainer}
            >
                <View style={styles.fullHeader}>
                    <View style={styles.fullLeft}>
                        <LevelBadge level={perfil.nivel_jugador} size="medium" />
                        <View style={styles.fullInfo}>
                            <Text style={styles.fullLevel}>Nivel {perfil.nivel_jugador}</Text>
                            <Text style={styles.fullXP}>
                                XP: {perfil.xp_total} ({Math.round(xpProgress)}%)
                            </Text>
                        </View>
                    </View>

                    {perfil.racha_dias > 0 && (
                        <StreakIndicator
                            streakDays={perfil.racha_dias}
                            size="small"
                            animated={true}
                            showLabel={false}
                        />
                    )}
                </View>

                <View style={styles.fullProgress}>
                    <ProgressBar
                        progress={xpProgress}
                        color={['#4facfe', '#00f2fe']}
                        height={12}
                        animated={true}
                        glowEffect={xpProgress > 80}
                    />
                </View>

                <View style={styles.fullStats}>
                    <View style={styles.fullStat}>
                        <Text style={styles.fullStatLabel}>PP Hoy</Text>
                        <Text style={styles.fullStatValue}>💎 {perfil.pp_dia}</Text>
                    </View>
                    <View style={styles.fullStatDivider} />
                    <View style={styles.fullStat}>
                        <Text style={styles.fullStatLabel}>PD Global</Text>
                        <Text style={styles.fullStatValue}>🏆 {perfil.pd_global}</Text>
                    </View>
                    <View style={styles.fullStatDivider} />
                    <View style={styles.fullStat}>
                        <Text style={styles.fullStatLabel}>Racha</Text>
                        <Text style={styles.fullStatValue}>
                            🔥 {perfil.racha_dias} {perfil.racha_dias === 1 ? 'día' : 'días'}
                        </Text>
                    </View>
                </View>

                <View style={styles.fullAction}>
                    <Text style={styles.actionText}>Ver Perfil Completo →</Text>
                </View>
            </LinearGradient>
        </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    container: {
        marginHorizontal: 16,
        marginVertical: 8,
    },
    loadingContainer: {
        padding: 20,
        alignItems: 'center',
    },

    // Compact styles
    compactContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: 12,
        marginHorizontal: 16,
        marginVertical: 8,
        borderRadius: 12,
        borderWidth: 1,
        borderColor: 'rgba(79, 172, 254, 0.3)',
    },
    compactLeft: {
        flexDirection: 'row',
        alignItems: 'center',
        flex: 1,
    },
    compactInfo: {
        marginLeft: 12,
        flex: 1,
    },
    compactLevel: {
        fontSize: 14,
        fontWeight: '600',
        color: '#FFFFFF',
        marginBottom: 4,
    },
    compactXPBar: {
        width: '100%',
    },
    compactStats: {
        flexDirection: 'row',
        gap: 12,
    },
    compactStat: {
        alignItems: 'center',
    },
    compactStatValue: {
        fontSize: 14,
        fontWeight: 'bold',
        color: '#FFFFFF',
    },
    compactStatLabel: {
        fontSize: 12,
        marginTop: 2,
    },

    // Full styles
    fullContainer: {
        padding: 16,
        marginHorizontal: 16,
        marginVertical: 8,
        borderRadius: 16,
        borderWidth: 1,
        borderColor: 'rgba(79, 172, 254, 0.3)',
    },
    fullHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 12,
    },
    fullLeft: {
        flexDirection: 'row',
        alignItems: 'center',
        flex: 1,
    },
    fullInfo: {
        marginLeft: 12,
    },
    fullLevel: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginBottom: 2,
    },
    fullXP: {
        fontSize: 13,
        color: 'rgba(255, 255, 255, 0.8)',
    },
    fullProgress: {
        marginBottom: 12,
    },
    fullStats: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        marginBottom: 12,
    },
    fullStat: {
        alignItems: 'center',
        flex: 1,
    },
    fullStatLabel: {
        fontSize: 11,
        color: 'rgba(255, 255, 255, 0.7)',
        marginBottom: 4,
    },
    fullStatValue: {
        fontSize: 14,
        fontWeight: '600',
        color: '#FFFFFF',
    },
    fullStatDivider: {
        width: 1,
        backgroundColor: 'rgba(255, 255, 255, 0.2)',
        marginVertical: 4,
    },
    fullAction: {
        alignItems: 'center',
        paddingTop: 8,
        borderTopWidth: 1,
        borderTopColor: 'rgba(255, 255, 255, 0.1)',
    },
    actionText: {
        fontSize: 13,
        fontWeight: '600',
        color: '#4facfe',
    },
});

export default GamificationWidget;
