import React, { useEffect, useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    ScrollView,
    Dimensions,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import Animated, {
    useSharedValue,
    useAnimatedStyle,
    withSpring,
    withSequence,
    withDelay,
    withRepeat,
} from 'react-native-reanimated';
import { MinibossResult } from '../services/gamification/types';
import { OPERATION_NAMES } from '../services/gamification/types';

const { width } = Dimensions.get('window');

export default function MinibossResultScreen() {
    const router = useRouter();
    const { operacion, resultData } = useLocalSearchParams<{
        operacion: string;
        resultData: string;
    }>();

    const [result, setResult] = useState<MinibossResult | null>(null);
    const scale = useSharedValue(0);
    const rotate = useSharedValue(0);
    const glowOpacity = useSharedValue(0);

    useEffect(() => {
        if (resultData) {
            try {
                const parsed = JSON.parse(resultData);
                setResult(parsed);

                // Start animations
                if (parsed.exito) {
                    // Victory animation
                    scale.value = withSequence(
                        withDelay(300, withSpring(1.3, { damping: 6 })),
                        withSpring(1, { damping: 8 })
                    );
                    rotate.value = withSequence(
                        withDelay(300, withSpring(360, { damping: 10 }))
                    );
                    glowOpacity.value = withDelay(
                        500,
                        withRepeat(
                            withSequence(
                                withSpring(0.8),
                                withSpring(0.3)
                            ),
                            -1,
                            true
                        )
                    );
                } else {
                    // Defeat animation
                    scale.value = withDelay(300, withSpring(1, { damping: 12 }));
                }
            } catch (error) {
                console.error('Error parsing result data:', error);
            }
        }
    }, [resultData]);

    const animatedStyle = useAnimatedStyle(() => ({
        transform: [
            { scale: scale.value },
            { rotate: `${rotate.value}deg` },
        ],
    }));

    const glowStyle = useAnimatedStyle(() => ({
        opacity: glowOpacity.value,
    }));

    if (!result) {
        return (
            <View style={styles.loadingContainer}>
                <Text style={styles.loadingText}>Cargando resultados...</Text>
            </View>
        );
    }

    const isVictory = result.exito;
    const operacionName = OPERATION_NAMES[operacion as keyof typeof OPERATION_NAMES] || operacion;

    return (
        <LinearGradient
            colors={
                isVictory
                    ? ['#1a1a2e', '#2d4a2b', '#1f6e1f']
                    : ['#1a1a2e', '#4a2d2d', '#6e1f1f']
            }
            style={styles.container}
        >
            <StatusBar style="light" />

            <ScrollView
                contentContainerStyle={styles.scrollContent}
                showsVerticalScrollIndicator={false}
            >
                {/* Victory/Defeat Icon */}
                <View style={styles.iconContainer}>
                    {isVictory && (
                        <Animated.View style={[styles.glowCircle, glowStyle]} />
                    )}

                    <Animated.View style={animatedStyle}>
                        <Text style={styles.resultIcon}>
                            {isVictory ? '🏆' : '💀'}
                        </Text>
                    </Animated.View>
                </View>

                {/* Title */}
                <Text style={[styles.title, isVictory ? styles.victoryTitle : styles.defeatTitle]}>
                    {isVictory ? '¡VICTORIA!' : 'DERROTA'}
                </Text>

                <Text style={styles.subtitle}>
                    {result.detalles.nombre}
                </Text>

                {/* Main Stats Card */}
                <View style={[
                    styles.mainStatsCard,
                    isVictory ? styles.victoryCard : styles.defeatCard
                ]}>
                    <View style={styles.statsRow}>
                        <View style={styles.statBox}>
                            <Text style={styles.statValue}>
                                {result.detalles.correctos}/{result.detalles.total}
                            </Text>
                            <Text style={styles.statLabel}>Correctas</Text>
                        </View>

                        <View style={styles.divider} />

                        <View style={styles.statBox}>
                            <Text style={[
                                styles.statValue,
                                result.detalles.cumple_acierto ? styles.successText : styles.failText
                            ]}>
                                {result.detalles.porcentaje_acierto}%
                            </Text>
                            <Text style={styles.statLabel}>Acierto</Text>
                        </View>

                        <View style={styles.divider} />

                        <View style={styles.statBox}>
                            <Text style={[
                                styles.statValue,
                                result.detalles.cumple_tiempo ? styles.successText : styles.failText
                            ]}>
                                {result.detalles.tiempo_segundos}s
                            </Text>
                            <Text style={styles.statLabel}>Tiempo</Text>
                        </View>
                    </View>
                </View>

                {/* Requirements Check */}
                <View style={styles.requirementsCard}>
                    <Text style={styles.requirementsTitle}>Requisitos</Text>

                    <View style={styles.requirement}>
                        <Text style={styles.requirementIcon}>
                            {result.detalles.cumple_acierto ? '✅' : '❌'}
                        </Text>
                        <Text style={styles.requirementText}>
                            Acierto mínimo: {result.detalles.acierto_requerido}%
                        </Text>
                    </View>

                    <View style={styles.requirement}>
                        <Text style={styles.requirementIcon}>
                            {result.detalles.cumple_tiempo ? '✅' : '❌'}
                        </Text>
                        <Text style={styles.requirementText}>
                            Tiempo límite: {result.detalles.tiempo_limite}s
                        </Text>
                    </View>

                    <View style={styles.requirement}>
                        <Text style={styles.requirementIcon}>
                            {result.detalles.cumple_reintentos ? '✅' : '❌'}
                        </Text>
                        <Text style={styles.requirementText}>
                            Sin reintentos
                        </Text>
                    </View>
                </View>

                {/* Unlock Info (if victory and unlocks something) */}
                {isVictory && result.desbloqueo?.hubo_desbloqueo && (
                    <View style={styles.unlockCard}>
                        <Text style={styles.unlockIcon}>🔓</Text>
                        <Text style={styles.unlockTitle}>¡Operación Desbloqueada!</Text>
                        <Text style={styles.unlockText}>
                            {result.desbloqueo.operaciones_desbloqueadas?.map(op =>
                                op.toUpperCase()
                            ).join(', ')}
                        </Text>
                    </View>
                )}

                {/* Message */}
                <View style={styles.messageCard}>
                    {isVictory ? (
                        <>
                            <Text style={styles.messageTitle}>¡Increíble!</Text>
                            <Text style={styles.messageText}>
                                Has demostrado tu dominio en {operacionName}.
                                {result.detalles.desbloquea
                                    ? ` Has desbloqueado ${result.detalles.desbloquea.toUpperCase()}.`
                                    : ' ¡Sigue así!'
                                }
                            </Text>
                        </>
                    ) : (
                        <>
                            <Text style={styles.messageTitle}>No te rindas</Text>
                            <Text style={styles.messageText}>
                                Practica más {operacionName} y vuelve a intentarlo cuando estés listo.
                                {!result.detalles.cumple_acierto && ' Necesitas mejorar tu precisión.'}
                                {!result.detalles.cumple_tiempo && ' Necesitas ser más rápido.'}
                            </Text>
                        </>
                    )}
                </View>

                {/* Action Buttons */}
                <View style={styles.actionsContainer}>
                    {isVictory ? (
                        <>
                            <TouchableOpacity
                                style={styles.primaryButton}
                                onPress={() => router.replace('/gamification-profile')}
                            >
                                <LinearGradient
                                    colors={['#34C759', '#28A745']}
                                    style={styles.buttonGradient}
                                >
                                    <Text style={styles.buttonText}>Ver Perfil</Text>
                                </LinearGradient>
                            </TouchableOpacity>

                            <TouchableOpacity
                                style={styles.secondaryButton}
                                onPress={() => router.replace('/')}
                            >
                                <Text style={styles.secondaryButtonText}>Ir a Inicio</Text>
                            </TouchableOpacity>
                        </>
                    ) : (
                        <>
                            <TouchableOpacity
                                style={styles.primaryButton}
                                onPress={() => router.replace('/miniboss')}
                            >
                                <LinearGradient
                                    colors={['#FF9500', '#FF6347']}
                                    style={styles.buttonGradient}
                                >
                                    <Text style={styles.buttonText}>Volver a Mini-jefes</Text>
                                </LinearGradient>
                            </TouchableOpacity>

                            <TouchableOpacity
                                style={styles.secondaryButton}
                                onPress={() => router.replace('/')}
                            >
                                <Text style={styles.secondaryButtonText}>Ir a Inicio</Text>
                            </TouchableOpacity>
                        </>
                    )}
                </View>
            </ScrollView>
        </LinearGradient>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    scrollContent: {
        padding: 20,
        paddingTop: 80,
        paddingBottom: 40,
        alignItems: 'center',
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#1a1a2e',
    },
    loadingText: {
        fontSize: 18,
        color: '#FFFFFF',
    },
    iconContainer: {
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 24,
        position: 'relative',
    },
    glowCircle: {
        position: 'absolute',
        width: 150,
        height: 150,
        borderRadius: 75,
        backgroundColor: 'rgba(255, 215, 0, 0.3)',
        shadowColor: '#FFD700',
        shadowOffset: { width: 0, height: 0 },
        shadowOpacity: 0.8,
        shadowRadius: 40,
    },
    resultIcon: {
        fontSize: 100,
    },
    title: {
        fontSize: 48,
        fontWeight: 'bold',
        marginBottom: 8,
        textShadowColor: 'rgba(0, 0, 0, 0.5)',
        textShadowOffset: { width: 0, height: 2 },
        textShadowRadius: 4,
    },
    victoryTitle: {
        color: '#FFD700',
    },
    defeatTitle: {
        color: '#FF3B30',
    },
    subtitle: {
        fontSize: 18,
        color: 'rgba(255, 255, 255, 0.8)',
        marginBottom: 32,
    },
    mainStatsCard: {
        width: '100%',
        borderRadius: 20,
        padding: 24,
        marginBottom: 20,
        borderWidth: 2,
    },
    victoryCard: {
        backgroundColor: 'rgba(52, 199, 89, 0.2)',
        borderColor: '#34C759',
    },
    defeatCard: {
        backgroundColor: 'rgba(255, 59, 48, 0.2)',
        borderColor: '#FF3B30',
    },
    statsRow: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        alignItems: 'center',
    },
    statBox: {
        alignItems: 'center',
        flex: 1,
    },
    statValue: {
        fontSize: 32,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginBottom: 4,
    },
    successText: {
        color: '#34C759',
    },
    failText: {
        color: '#FF3B30',
    },
    statLabel: {
        fontSize: 12,
        color: 'rgba(255, 255, 255, 0.7)',
    },
    divider: {
        width: 1,
        height: 40,
        backgroundColor: 'rgba(255, 255, 255, 0.2)',
    },
    requirementsCard: {
        width: '100%',
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: 16,
        padding: 20,
        marginBottom: 20,
    },
    requirementsTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginBottom: 16,
    },
    requirement: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 12,
    },
    requirementIcon: {
        fontSize: 20,
        marginRight: 12,
    },
    requirementText: {
        fontSize: 15,
        color: 'rgba(255, 255, 255, 0.9)',
    },
    unlockCard: {
        width: '100%',
        backgroundColor: 'rgba(255, 215, 0, 0.2)',
        borderRadius: 16,
        padding: 20,
        marginBottom: 20,
        borderWidth: 2,
        borderColor: '#FFD700',
        alignItems: 'center',
    },
    unlockIcon: {
        fontSize: 48,
        marginBottom: 12,
    },
    unlockTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#FFD700',
        marginBottom: 8,
    },
    unlockText: {
        fontSize: 16,
        color: '#FFFFFF',
        textAlign: 'center',
    },
    messageCard: {
        width: '100%',
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        borderRadius: 16,
        padding: 20,
        marginBottom: 32,
    },
    messageTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginBottom: 8,
    },
    messageText: {
        fontSize: 15,
        color: 'rgba(255, 255, 255, 0.8)',
        lineHeight: 22,
    },
    actionsContainer: {
        width: '100%',
        gap: 12,
    },
    primaryButton: {
        borderRadius: 16,
        overflow: 'hidden',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 6,
        elevation: 8,
    },
    buttonGradient: {
        paddingVertical: 16,
        alignItems: 'center',
    },
    buttonText: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#FFFFFF',
    },
    secondaryButton: {
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: 16,
        paddingVertical: 16,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.3)',
    },
    secondaryButtonText: {
        fontSize: 16,
        fontWeight: '600',
        color: '#FFFFFF',
    },
});
