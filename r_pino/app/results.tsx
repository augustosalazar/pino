import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Modal } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { LinearGradient } from 'expo-linear-gradient';
import { LevelUpModal, UnlockAnimation } from '../components/gamification';
import { GamificationRewards } from '../services/gamification/types';
import { BlurView } from 'expo-blur';

export default function ResultsScreen() {
    const router = useRouter();
    const params = useLocalSearchParams<{
        totalExercises: string;
        correctAnswers: string;
        scoreEarned: string;
        accuracy: string;
        gamificationData?: string;
    }>();

    const [showLevelUpModal, setShowLevelUpModal] = useState(false);
    const [showUnlockModal, setShowUnlockModal] = useState(false);
    const [gamificationRewards, setGamificationRewards] = useState<GamificationRewards | null>(null);

    const totalExercises = parseInt(params.totalExercises);
    const correctAnswers = parseInt(params.correctAnswers);
    const accuracy = parseFloat(params.accuracy);

    useEffect(() => {
        // Parse gamification data if available
        if (params.gamificationData) {
            try {
                const data = JSON.parse(params.gamificationData);
                setGamificationRewards(data);

                // Show level up modal if applicable
                if (data.progreso?.hubo_levelup) {
                    setTimeout(() => setShowLevelUpModal(true), 800);
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

    const handleGoHome = () => {
        router.replace('/');
    };

    return (
        <View style={styles.container}>
            <StatusBar style="light" />

            <Modal
                visible={true}
                transparent
                animationType="fade"
            >
                <BlurView intensity={80} style={styles.blurContainer}>
                    <View style={styles.modalContent}>
                        <LinearGradient
                            colors={['#1a1a2e', '#16213e']}
                            style={styles.gradient}
                        >
                            <View style={styles.card}>
                                {/* Emoji */}
                                <Text style={styles.emoji}>{message.emoji}</Text>

                                {/* Message */}
                                <Text style={[styles.title, { color: message.color }]}>
                                    {message.text}
                                </Text>

                                {/* Score */}
                                <Text style={styles.score}>
                                    {correctAnswers}/{totalExercises} correctas
                                </Text>

                                {/* Home Button */}
                                <TouchableOpacity
                                    style={styles.homeButton}
                                    onPress={handleGoHome}
                                    activeOpacity={0.8}
                                >
                                    <LinearGradient
                                        colors={['#4facfe', '#00f2fe']}
                                        start={{ x: 0, y: 0 }}
                                        end={{ x: 1, y: 0 }}
                                        style={styles.buttonGradient}
                                    >
                                        <Text style={styles.buttonText}>Volver al Inicio</Text>
                                    </LinearGradient>
                                </TouchableOpacity>
                            </View>
                        </LinearGradient>
                    </View>
                </BlurView>
            </Modal>

            {/* Gamification Modals */}
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
        backgroundColor: 'transparent',
    },
    blurContainer: {
        flex: 1,
        justifyContent: 'center' as const,
        alignItems: 'center' as const,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
    },
    modalContent: {
        width: '85%',
        maxWidth: 400,
        borderRadius: 24,
        overflow: 'hidden',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 10 },
        shadowOpacity: 0.5,
        shadowRadius: 20,
        elevation: 20,
    },
    gradient: {
        padding: 32,
    },
    card: {
        alignItems: 'center' as const,
    },
    emoji: {
        fontSize: 72,
        marginBottom: 16,
    },
    title: {
        fontSize: 32,
        fontWeight: 'bold' as const,
        marginBottom: 16,
        textAlign: 'center' as const,
    },
    score: {
        fontSize: 20,
        color: 'rgba(255, 255, 255, 0.9)',
        marginBottom: 32,
        fontWeight: '600',
    },
    homeButton: {
        width: '100%',
        borderRadius: 16,
        overflow: 'hidden',
        shadowColor: '#00f2fe',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.4,
        shadowRadius: 8,
        elevation: 8,
    },
    buttonGradient: {
        paddingVertical: 16,
        alignItems: 'center' as const,
    },
    buttonText: {
        color: '#FFFFFF',
        fontSize: 18,
        fontWeight: 'bold' as const,
    },
});
