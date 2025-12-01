import React, { useState, useEffect, useCallback } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    TouchableOpacity,
    RefreshControl,
    ActivityIndicator,
    Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import {
    ProgressBar,
    StatCard,
    LevelBadge,
    OperationCard,
    StreakIndicator,
} from '../components/gamification';
import gamificationService from '../services/gamification/GamificationService';
import {
    GamificationProfile,
    calculateXPProgress,
    calculateXPRequired,
} from '../services/gamification/types';

export default function GamificationProfileScreen() {
    const router = useRouter();
    const [profile, setProfile] = useState<GamificationProfile | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    // TODO: Get user_ref from auth context
    const userRef = 'current_user'; // Replace with actual user_ref

    const loadProfile = useCallback(async () => {
        try {
            setLoading(true);
            const data = await gamificationService.getProfile(userRef);
            setProfile(data);
        } catch (error) {
            console.error('Error loading gamification profile:', error);
            Alert.alert(
                'Error',
                'No se pudo cargar el perfil de gamificación. Intenta de nuevo.'
            );
        } finally {
            setLoading(false);
        }
    }, [userRef]);

    const onRefresh = useCallback(async () => {
        setRefreshing(true);
        await loadProfile();
        setRefreshing(false);
    }, [loadProfile]);

    useEffect(() => {
        loadProfile();
    }, [loadProfile]);

    if (loading && !profile) {
        return (
            <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#4facfe" />
                <Text style={styles.loadingText}>Cargando perfil...</Text>
            </View>
        );
    }

    if (!profile) {
        return (
            <View style={styles.errorContainer}>
                <Text style={styles.errorText}>
                    No se pudo cargar el perfil de gamificación
                </Text>
                <TouchableOpacity style={styles.retryButton} onPress={loadProfile}>
                    <Text style={styles.retryText}>Reintentar</Text>
                </TouchableOpacity>
            </View>
        );
    }

    const { perfil, operaciones } = profile;

    // Calculate XP progress
    const xpProgress = calculateXPProgress(
        perfil.xp_total,
        perfil.nivel_jugador
    );
    const xpRequired = calculateXPRequired(perfil.nivel_jugador + 1);
    const xpCurrent = perfil.xp_total - calculateXPRequired(perfil.nivel_jugador);

    // Calculate weekly score
    const weeklyScore =
        perfil.pp_semana * 0.4 + perfil.pd_semana * 0.6;

    return (
        <LinearGradient
            colors={['#1a1a2e', '#16213e', '#0f3460']}
            style={styles.container}
        >
            <ScrollView
                style={styles.scrollView}
                contentContainerStyle={styles.scrollContent}
                refreshControl={
                    <RefreshControl
                        refreshing={refreshing}
                        onRefresh={onRefresh}
                        tintColor="#4facfe"
                    />
                }
            >
                {/* Header Section */}
                <View style={styles.header}>
                    <View style={styles.headerContent}>
                        <View style={styles.avatarContainer}>
                            <Text style={styles.avatar}>👤</Text>
                        </View>

                        <View style={styles.headerInfo}>
                            <Text style={styles.username}>Usuario</Text>
                            <View style={styles.levelContainer}>
                                <LevelBadge
                                    level={perfil.nivel_jugador}
                                    size="large"
                                    showName={false}
                                    animated={true}
                                />
                                <View style={styles.levelTextContainer}>
                                    <Text style={styles.levelTitle}>NIVEL {perfil.nivel_jugador}</Text>
                                    <Text style={styles.xpText}>
                                        {Math.round(xpCurrent)} / {xpRequired} XP
                                    </Text>
                                </View>
                            </View>
                        </View>
                    </View>

                    {/* XP Progress Bar */}
                    <View style={styles.xpBarContainer}>
                        <ProgressBar
                            progress={xpProgress}
                            color={['#4facfe', '#00f2fe']}
                            height={16}
                            showLabel={true}
                            label={`${Math.round(xpProgress)}%`}
                            glowEffect={xpProgress > 80}
                            animated={true}
                        />
                    </View>
                </View>

                {/* Stats Grid */}
                <View style={styles.statsSection}>
                    <Text style={styles.sectionTitle}>📊 Estadísticas Globales</Text>

                    <View style={styles.statsGrid}>
                        <View style={styles.statItem}>
                            <StatCard
                                icon="💎"
                                label="PP Total"
                                value={perfil.pp_total}
                                color={['#43e97b', '#38f9d7']}
                                size="medium"
                                gradient={true}
                            />
                        </View>

                        <View style={styles.statItem}>
                            <StatCard
                                icon="🏆"
                                label="PD Global"
                                value={perfil.pd_global}
                                color={['#fa709a', '#fee140']}
                                size="medium"
                                gradient={true}
                            />
                        </View>

                        <View style={styles.statItem}>
                            <StreakIndicator
                                streakDays={perfil.racha_dias}
                                size="large"
                                animated={true}
                                showLabel={true}
                            />
                        </View>

                        <View style={styles.statItem}>
                            <StatCard
                                icon="📈"
                                label="Score Semanal"
                                value={weeklyScore.toFixed(1)}
                                color={['#667eea', '#764ba2']}
                                size="medium"
                                gradient={true}
                            />
                        </View>
                    </View>

                    {/* Daily/Weekly Stats */}
                    <View style={styles.subStatsRow}>
                        <Text style={styles.subStat}>
                            💎 Hoy: {perfil.pp_dia} PP
                        </Text>
                        <Text style={styles.subStat}>
                            🏆 Esta semana: {perfil.pd_semana} PD
                        </Text>
                    </View>
                </View>

                {/* Operations Section */}
                <View style={styles.operationsSection}>
                    <Text style={styles.sectionTitle}>🎯 Operaciones</Text>

                    {operaciones
                        .sort((a, b) => {
                            // Sort: unlocked first, then by operation order
                            const order = ['suma', 'resta', 'mult', 'div'];
                            if (a.unlocked !== b.unlocked) {
                                return a.unlocked ? -1 : 1;
                            }
                            return order.indexOf(a.operacion) - order.indexOf(b.operacion);
                        })
                        .map((operation) => (
                            <OperationCard
                                key={operation.operacion}
                                operation={operation}
                                onPress={
                                    operation.unlocked
                                        ? () => {
                                            // TODO: Navigate to operation detail or practice
                                            Alert.alert(
                                                'Operación',
                                                `Ver detalles de ${operation.operacion}`
                                            );
                                        }
                                        : undefined
                                }
                                showProgress={true}
                            />
                        ))}
                </View>

                {/* Unlock Progress Section */}
                {profile.progreso_desbloqueos && (
                    <View style={styles.unlocksSection}>
                        <Text style={styles.sectionTitle}>🔓 Progreso de Desbloqueos</Text>

                        {Object.entries(profile.progreso_desbloqueos).map(
                            ([operacion, progress]) => {
                                if (progress.desbloqueada) return null;

                                return (
                                    <View key={operacion} style={styles.unlockCard}>
                                        <Text style={styles.unlockTitle}>
                                            {operacion.toUpperCase()}
                                        </Text>

                                        {progress.requisitos && (
                                            <View style={styles.requirementsList}>
                                                {Object.entries(progress.requisitos).map(
                                                    ([key, req]) => {
                                                        if (typeof req === 'object' && 'cumplido' in req) {
                                                            return (
                                                                <View key={key} style={styles.requirement}>
                                                                    <Text style={styles.requirementIcon}>
                                                                        {req.cumplido ? '✅' : '❌'}
                                                                    </Text>
                                                                    <Text style={styles.requirementText}>
                                                                        {key}: {req.actual} / {req.requerido}
                                                                    </Text>
                                                                </View>
                                                            );
                                                        } else if (
                                                            typeof req === 'object' &&
                                                            'completado' in req
                                                        ) {
                                                            return (
                                                                <View key={key} style={styles.requirement}>
                                                                    <Text style={styles.requirementIcon}>
                                                                        {req.completado ? '✅' : '❌'}
                                                                    </Text>
                                                                    <Text style={styles.requirementText}>
                                                                        {key.replace('minijefe_', 'Mini-jefe: ').toUpperCase()}
                                                                    </Text>
                                                                </View>
                                                            );
                                                        }
                                                        return null;
                                                    }
                                                )}
                                            </View>
                                        )}
                                    </View>
                                );
                            }
                        )}
                    </View>
                )}

                {/* Action Buttons */}
                <View style={styles.actionsSection}>
                    <TouchableOpacity
                        style={[styles.actionButton, styles.primaryButton]}
                        onPress={() => {
                            // TODO: Navigate to miniboss screen
                            router.push('/miniboss');
                        }}
                    >
                        <LinearGradient
                            colors={['#f093fb', '#f5576c']}
                            start={{ x: 0, y: 0 }}
                            end={{ x: 1, y: 0 }}
                            style={styles.actionButtonGradient}
                        >
                            <Text style={styles.actionButtonIcon}>🐉</Text>
                            <Text style={styles.actionButtonText}>Mini-jefes</Text>
                        </LinearGradient>
                    </TouchableOpacity>

                    <TouchableOpacity
                        style={[styles.actionButton, styles.secondaryButton]}
                        onPress={() => {
                            // TODO: Navigate to leaderboard
                            router.push('/leaderboard');
                        }}
                    >
                        <LinearGradient
                            colors={['#4facfe', '#00f2fe']}
                            start={{ x: 0, y: 0 }}
                            end={{ x: 1, y: 0 }}
                            style={styles.actionButtonGradient}
                        >
                            <Text style={styles.actionButtonIcon}>🏆</Text>
                            <Text style={styles.actionButtonText}>Ranking</Text>
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
    scrollView: {
        flex: 1,
    },
    scrollContent: {
        padding: 16,
        paddingBottom: 40,
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#1a1a2e',
    },
    loadingText: {
        marginTop: 12,
        color: '#FFFFFF',
        fontSize: 16,
    },
    errorContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#1a1a2e',
        padding: 20,
    },
    errorText: {
        color: '#FFFFFF',
        fontSize: 16,
        textAlign: 'center',
        marginBottom: 20,
    },
    retryButton: {
        paddingHorizontal: 24,
        paddingVertical: 12,
        backgroundColor: '#4facfe',
        borderRadius: 8,
    },
    retryText: {
        color: '#FFFFFF',
        fontSize: 16,
        fontWeight: '600',
    },
    header: {
        marginBottom: 24,
    },
    headerContent: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 16,
    },
    avatarContainer: {
        width: 60,
        height: 60,
        borderRadius: 30,
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        alignItems: 'center',
        justifyContent: 'center',
        marginRight: 16,
    },
    avatar: {
        fontSize: 32,
    },
    headerInfo: {
        flex: 1,
    },
    username: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginBottom: 8,
    },
    levelContainer: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    levelTextContainer: {
        marginLeft: 12,
    },
    levelTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#FFD700',
        marginBottom: 4,
    },
    xpText: {
        fontSize: 13,
        color: 'rgba(255, 255, 255, 0.8)',
    },
    xpBarContainer: {
        marginTop: 8,
    },
    statsSection: {
        marginBottom: 24,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginBottom: 16,
    },
    statsGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        marginHorizontal: -6,
    },
    statItem: {
        width: '50%',
        padding: 6,
    },
    subStatsRow: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        marginTop: 16,
        padding: 12,
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        borderRadius: 12,
    },
    subStat: {
        fontSize: 14,
        fontWeight: '600',
        color: 'rgba(255, 255, 255, 0.9)',
    },
    operationsSection: {
        marginBottom: 24,
    },
    unlocksSection: {
        marginBottom: 24,
    },
    unlockCard: {
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        borderRadius: 12,
        padding: 16,
        marginBottom: 12,
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.1)',
    },
    unlockTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#FFD700',
        marginBottom: 12,
    },
    requirementsList: {
        gap: 8,
    },
    requirement: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    requirementIcon: {
        fontSize: 16,
        marginRight: 8,
    },
    requirementText: {
        fontSize: 14,
        color: 'rgba(255, 255, 255, 0.8)',
    },
    actionsSection: {
        gap: 12,
    },
    actionButton: {
        borderRadius: 16,
        overflow: 'hidden',
        elevation: 6,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 6,
    },
    primaryButton: {},
    secondaryButton: {},
    actionButtonGradient: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 16,
    },
    actionButtonIcon: {
        fontSize: 24,
        marginRight: 12,
    },
    actionButtonText: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#FFFFFF',
    },
});
