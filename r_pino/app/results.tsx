import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { LinearGradient } from 'expo-linear-gradient';
import {
    RewardCard,
    LevelUpModal,
    UnlockAnimation,
    ProgressBar,
} from '../components/gamification';
import { GamificationRewards } from '../services/gamification/types';

export default function ResultsScreen() {
    const router = useRouter();
    const params = useLocalSearchParams<{
        totalExercises: string;
        correctAnswers: string;
        scoreEarned: string;
        accuracy: string;
        gamificationData?: string; // JSON string
    }>();

    const [showLevelUpModal, setShowLevelUpModal] = useState(false);
    const [showUnlockModal, setShowUnlockModal] = useState(false);
    const [gamificationRewards, setGamificationRewards] = useState<GamificationRewards | null>(null);

    const totalExercises = parseInt(params.totalExercises);
    const correctAnswers = parseInt(params.correctAnswers);
    const scoreEarned = parseInt(params.scoreEarned);
    const accuracy = parseFloat(params.accuracy);
    const incorrectAnswers = totalExercises - correctAnswers;

    useEffect(() => {
        // Parse gamification data if available
        if (params.gamificationData) {
            try {
                const data = JSON.parse(params.gamificationData);
                setGamificationRewards(data);

                // Show level up modal if applicable
                if (data.progreso?.hubo_levelup) {
                    setTimeout(() => setShowLevelUpModal(true), 1000);
                }
            } catch (error) {
                console.error('Error parsing gamification data:', error);
            }
        }
    }, [params.gamificationData]);

    const handleLevelUpClose = () => {
        setShowLevelUpModal(false);

        // Show unlock modal if there were unlocks
        if (gamificationRewards?.desbloqueos?.hubo_desbloqueos) {
            setTimeout(() => setShowUnlockModal(true), 300);
        }
    };

    const getMessage = () => {
        if (accuracy >= 90) return { emoji: '🎉', text: '¡EXCELENTE!', color: '#34C759' };
        if (accuracy >= 70) return { emoji: '👏', text: '¡MUY BIEN!', color: '#007AFF' };
        if (accuracy >= 50) return { emoji: '👍', text: '¡BUEN TRABAJO!', color: '#FF9500' };
        return { emoji: '💪', text: '¡SIGUE PRACTICANDO!', color: '#FF3B30' };
    };

    const message = getMessage();
    const hasGamification = !!gamificationRewards;

    // Get unlocked operations
    const unlockedOperations = hasGamification && gamificationRewards.desbloqueos.hubo_desbloqueos
        ? Object.entries(gamificationRewards.desbloqueos.operaciones)
            .filter(([_, unlocked]) => unlocked)
            .map(([op, _]) => op)
        : [];

    return (
        <View style={styles.container}>
            <StatusBar style="light" />

            <LinearGradient
                colors={['#1a1a2e', '#16213e', '#0f3460']}
                style={styles.gradient}
            >
                <ScrollView contentContainerStyle={styles.content}>
                    {/* Header */}
                    <View style={styles.header}>
                        <Text style={styles.emoji}>{message.emoji}</Text>
                        <Text style={[styles.title, { color: message.color }]}>
                            {message.text}
                        </Text>
                        <Text style={styles.subtitle}>
                            {correctAnswers}/{totalExercises} correctas
                        </Text>
                    </View>

                    {/* Gamification Rewards */}
                    {hasGamification && (
                        <View style={styles.rewardsSection}>
                            <Text style={styles.sectionTitle}>🎁 Recompensas Ganadas</Text>

                            {/* PP Reward */}
                            {gamificationRewards.recompensas.pp_ganados > 0 && (
                                <RewardCard
                                    icon="💎"
                                    label="Puntos de Práctica"
                                    value={gamificationRewards.recompensas.pp_ganados}
                                    color={['#43e97b', '#38f9d7']}
                                    delay={0}
                                    showPlus={true}
                                />
                            )}

                            {/* PD Reward */}
                            {gamificationRewards.recompensas.pd.total_pd_global > 0 && (
                                <RewardCard
                                    icon="🏆"
                                    label="Puntos de Dominio"
                                    value={gamificationRewards.recompensas.pd.total_pd_global}
                                    color={['#fa709a', '#fee140']}
                                    delay={100}
                                    showPlus={true}
                                />
                            )}

                            {/* XP Reward */}
                            {gamificationRewards.recompensas.xp_ganada > 0 && (
                                <RewardCard
                                    icon="✨"
                                    label="Experiencia"
                                    value={gamificationRewards.recompensas.xp_ganada}
                                    color={['#4facfe', '#00f2fe']}
                                    delay={200}
                                    showPlus={true}
                                />
                            )}

                            {/* Streak Bonus */}
                            {gamificationRewards.recompensas.pd.bonus_racha > 0 && (
                                <RewardCard
                                    icon="🔥"
                                    label="Bonus Racha Diaria"
                                    value={gamificationRewards.recompensas.pd.bonus_racha}
                                    color={['#f093fb', '#f5576c']}
                                    delay={300}
                                    showPlus={true}
                                />
                            )}

                            {/* Batch Bonus */}
                            {gamificationRewards.recompensas.pd.bonus_batch > 0 && (
                                <RewardCard
                                    icon="🎯"
                                    label="Bonus de Rendimiento"
                                    value={gamificationRewards.recompensas.pd.bonus_batch}
                                    color={['#667eea', '#764ba2']}
                                    delay={400}
                                    showPlus={true}
                                />
                            )}
                        </View>
                    )}

                    {/* Progress Section */}
                    {hasGamification && (
                        <View style={styles.progressSection}>
                            <Text style={styles.sectionTitle}>📊 Tu Progreso</Text>

                            {/* Level Info */}
                            <View style={styles.progressCard}>
                                <View style={styles.progressRow}>
                                    <Text style={styles.progressLabel}>Nivel de Jugador</Text>
                                    <Text style={styles.progressValue}>
                                        {gamificationRewards.progreso.nivel_jugador}
                                        {gamificationRewards.progreso.hubo_levelup && ' 🎉'}
                                    </Text>
                                </View>

                                {gamificationRewards.progreso.hubo_levelup && (
                                    <Text style={styles.levelUpHint}>
                                        ¡Subiste de nivel! Toca para ver detalles →
                                    </Text>
                                )}
                            </View>

                            {/* Stats */}
                            <View style={styles.statsRow}>
                                <View style={styles.statMini}>
                                    <Text style={styles.statMiniValue}>{gamificationRewards.progreso.pd_global}</Text>
                                    <Text style={styles.statMiniLabel}>PD Total</Text>
                                </View>
                                <View style={styles.statMini}>
                                    <Text style={styles.statMiniValue}>{gamificationRewards.progreso.xp_total}</Text>
                                    <Text style={styles.statMiniLabel}>XP Total</Text>
                                </View>
                                <View style={styles.statMini}>
                                    <Text style={styles.statMiniValue}>{gamificationRewards.progreso.racha_dias}</Text>
                                    <Text style={styles.statMiniLabel}>Racha 🔥</Text>
                                </View>
                            </View>

                            {/* Pending Items */}
                            {gamificationRewards.items_pendientes.total > 0 && (
                                <View style={styles.pendingItemsCard}>
                                    <Text style={styles.pendingTitle}>
                                        📝 Items para Repasar: {gamificationRewards.items_pendientes.total}
                                    </Text>
                                    <Text style={styles.pendingText}>
                                        {gamificationRewards.items_pendientes.mensaje}
                                    </Text>
                                </View>
                            )}
                        </View>
                    )}

                    {/* Standard Stats (fallback if no gamification) */}
                    {!hasGamification && (
                        <>
                            <View style={styles.scoreCard}>
                                <Text style={styles.scoreLabel}>Puntuación</Text>
                                <Text style={styles.scoreValue}>+{scoreEarned}</Text>
                            </View>

                            <View style={styles.statsGrid}>
                                <View style={styles.statCard}>
                                    <Text style={styles.statValue}>{accuracy.toFixed(1)}%</Text>
                                    <Text style={styles.statLabel}>Precisión</Text>
                                </View>
                                <View style={styles.statCard}>
                                    <Text style={[styles.statValue, { color: '#34C759' }]}>
                                        {correctAnswers}
                                    </Text>
                                    <Text style={styles.statLabel}>Correctas</Text>
                                </View>
                                <View style={styles.statCard}>
                                    <Text style={[styles.statValue, { color: '#FF3B30' }]}>
                                        {incorrectAnswers}
                                    </Text>
                                    <Text style={styles.statLabel}>Incorrectas</Text>
                                </View>
                            </View>
                        </>
                    )}

                    {/* Action Buttons */}
                    <View style={styles.actionsSection}>
                        <TouchableOpacity
                            style={styles.primaryButton}
                            onPress={() => router.replace('/')}
                        >
                            <LinearGradient
                                colors={['#4facfe', '#00f2fe']}
                                start={{ x: 0, y: 0 }}
                                end={{ x: 1, y: 0 }}
                                style={styles.buttonGradient}
                            >
                                <Text style={styles.primaryButtonText}>Continuar</Text>
                            </LinearGradient>
                        </TouchableOpacity>

                        {hasGamification && (
                            <TouchableOpacity
                                style={styles.secondaryButton}
                                onPress={() => router.push('/gamification-profile')}
                            >
                                <Text style={styles.secondaryButtonText}>Ver Perfil Completo</Text>
                            </TouchableOpacity>
                        )}

                        <TouchableOpacity
                            style={styles.tertiaryButton}
                            onPress={() => router.push('/stats')}
                        >
                            <Text style={styles.tertiaryButtonText}>Estadísticas</Text>
                        </TouchableOpacity>
                    </View>
                </ScrollView>
            </LinearGradient>

            {/* Modals */}
            {hasGamification && gamificationRewards.progreso.hubo_levelup && (
                <LevelUpModal
                    visible={showLevelUpModal}
                    oldLevel={gamificationRewards.progreso.nivel_jugador - 1}
                    newLevel={gamificationRewards.progreso.nivel_jugador}
                    pdReward={gamificationRewards.recompensas.pd.bonus_levelup}
                    onClose={handleLevelUpClose}
                />
            )}

            {hasGamification && unlockedOperations.length > 0 && (
                <UnlockAnimation
                    visible={showUnlockModal}
                    operationsUnlocked={unlockedOperations}
                    onClose={() => setShowUnlockModal(false)}
                />
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    gradient: {
        flex: 1,
    },
    content: {
        padding: 16,
        paddingTop: 50,
        paddingBottom: 20,
    },
    header: {
        alignItems: 'center',
        marginBottom: 20,
    },
    emoji: {
        fontSize: 48,
        marginBottom: 8,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 4,
    },
    subtitle: {
        fontSize: 14,
        color: 'rgba(255, 255, 255, 0.8)',
        fontWeight: '500',
    },
    rewardsSection: {
        marginBottom: 16,
    },
    sectionTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginBottom: 12,
    },
    progressSection: {
        marginBottom: 16,
    },
    progressCard: {
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: 12,
        padding: 12,
        marginBottom: 8,
    },
    progressRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    progressLabel: {
        fontSize: 13,
        color: 'rgba(255, 255, 255, 0.8)',
    },
    progressValue: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#FFD700',
    },
    levelUpHint: {
        fontSize: 11,
        color: '#4facfe',
        marginTop: 6,
        fontStyle: 'italic',
    },
    statsRow: {
        flexDirection: 'row',
        gap: 8,
        marginBottom: 12,
    },
    statMini: {
        flex: 1,
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: 10,
        padding: 10,
        alignItems: 'center',
    },
    statMiniValue: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginBottom: 2,
    },
    statMiniLabel: {
        fontSize: 10,
        color: 'rgba(255, 255, 255, 0.7)',
    },
    pendingItemsCard: {
        backgroundColor: 'rgba(255, 149, 0, 0.2)',
        borderRadius: 10,
        padding: 12,
        borderWidth: 1,
        borderColor: 'rgba(255, 149, 0, 0.4)',
    },
    pendingTitle: {
        fontSize: 13,
        fontWeight: '600',
        color: '#FFA500',
        marginBottom: 4,
    },
    pendingText: {
        fontSize: 11,
        color: 'rgba(255, 255, 255, 0.8)',
        lineHeight: 16,
    },
    scoreCard: {
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: 12,
        padding: 20,
        alignItems: 'center',
        marginBottom: 16,
    },
    scoreLabel: {
        fontSize: 13,
        color: 'rgba(255, 255, 255, 0.7)',
        marginBottom: 6,
    },
    scoreValue: {
        fontSize: 36,
        fontWeight: 'bold',
        color: '#4facfe',
    },
    statsGrid: {
        flexDirection: 'row',
        gap: 10,
        marginBottom: 16,
    },
    statCard: {
        flex: 1,
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: 10,
        padding: 14,
        alignItems: 'center',
    },
    statValue: {
        fontSize: 22,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginBottom: 2,
    },
    statLabel: {
        fontSize: 11,
        color: 'rgba(255, 255, 255, 0.7)',
    },
    actionsSection: {
        gap: 10,
    },
    primaryButton: {
        borderRadius: 12,
        overflow: 'hidden',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 6,
        elevation: 6,
    },
    buttonGradient: {
        paddingVertical: 14,
        alignItems: 'center',
    },
    primaryButtonText: {
        color: '#FFFFFF',
        fontSize: 16,
        fontWeight: 'bold',
    },
    secondaryButton: {
        backgroundColor: 'rgba(255, 255, 255, 0.15)',
        borderRadius: 12,
        paddingVertical: 14,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.3)',
    },
    secondaryButtonText: {
        color: '#FFFFFF',
        fontSize: 14,
        fontWeight: '600',
    },
    tertiaryButton: {
        backgroundColor: 'transparent',
        borderRadius: 12,
        paddingVertical: 12,
        alignItems: 'center',
    },
    tertiaryButtonText: {
        color: 'rgba(255, 255, 255, 0.8)',
        fontSize: 14,
        fontWeight: '500',
    },
});
