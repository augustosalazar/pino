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

                    <View style={styles.operationsGrid}>
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
                                <View key={operation.operacion} style={styles.operationItem}>
                                    <OperationCard
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
                                </View>
                            ))}
                    </View>
                </View>

                {/* Unlock Progress Section */}
                {profile.progreso_desbloqueos && (
                    <View style={styles.unlocksSection}>
                        <Text style={styles.sectionTitle}>🔓 Progreso de Desbloqueos</Text>

                        <View style={styles.unlocksGrid}>
                            {Object.entries(profile.progreso_desbloqueos).map(
                                ([operacion, progress]) => {
                                    if (progress.desbloqueada) return null;

                                    return (
                                        <View key={operacion} style={styles.unlockItem}>
                                            <View style={styles.unlockCard}>
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
                                        </View>
                                    );
                                }
                            )}
                        </View>
                    </View>
                )}

                {/*                 <View style={styles.actionsSection}>
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
                </View> */}
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
        padding: 12,
        paddingTop: 50,
        paddingBottom: 20,
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
        marginBottom: 16,
    },
    headerContent: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 12,
    },
    avatarContainer: {
        width: 48,
        height: 48,
        borderRadius: 24,
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        alignItems: 'center',
        justifyContent: 'center',
        marginRight: 12,
    },
    avatar: {
        fontSize: 24,
    },
    headerInfo: {
        flex: 1,
    },
    username: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginBottom: 6,
    },
    levelContainer: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    levelTextContainer: {
        marginLeft: 10,
    },
    levelTitle: {
        fontSize: 14,
        fontWeight: 'bold',
        color: '#FFD700',
        marginBottom: 2,
    },
    xpText: {
        fontSize: 11,
        color: 'rgba(255, 255, 255, 0.8)',
    },
    xpBarContainer: {
        marginTop: 6,
    },
    statsSection: {
        marginBottom: 16,
    },
    sectionTitle: {
        fontSize: 15,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginBottom: 12,
    },
    statsGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        marginHorizontal: -4,
    },
    statItem: {
        width: '50%',
        padding: 4,
    },
    subStatsRow: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        marginTop: 12,
        padding: 10,
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        borderRadius: 10,
    },
    subStat: {
        fontSize: 12,
        fontWeight: '600',
        color: 'rgba(255, 255, 255, 0.9)',
    },
    operationsSection: {
        marginBottom: 24,
    },
    operationsGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        marginHorizontal: -6,
    },
    operationItem: {
        width: '50%',
        padding: 6,
    },
    unlocksSection: {
        marginBottom: 24,
    },
    unlocksGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        marginHorizontal: -6,
    },
    unlockItem: {
        width: '50%',
        padding: 6,
    },
    unlockCard: {
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        borderRadius: 10,
        padding: 12,
        marginBottom: 10,
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.1)',
    },
    unlockTitle: {
        fontSize: 14,
        fontWeight: 'bold',
        color: '#FFD700',
        marginBottom: 10,
    },
    requirementsList: {
        gap: 6,
    },
    requirement: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    requirementIcon: {
        fontSize: 14,
        marginRight: 6,
    },
    requirementText: {
        fontSize: 12,
        color: 'rgba(255, 255, 255, 0.8)',
    },
    actionsSection: {
        gap: 10,
    },
    actionButton: {
        borderRadius: 12,
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
        padding: 14,
    },
    actionButtonIcon: {
        fontSize: 20,
        marginRight: 10,
    },
    actionButtonText: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#FFFFFF',
    },
});
