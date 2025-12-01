import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { MinibossInfo } from '../../services/gamification/types';

interface MinibossCardProps {
    miniboss: MinibossInfo;
    canAttempt: boolean;
    reason?: string;
    onPress?: () => void;
    completed?: boolean;
}

export const MinibossCard: React.FC<MinibossCardProps> = ({
    miniboss,
    canAttempt,
    reason,
    onPress,
    completed = false,
}) => {
    const getGradientColors = (): [string, string] => {
        if (completed) return ['rgba(52, 199, 89, 0.3)', 'rgba(52, 199, 89, 0.1)'];
        if (!canAttempt) return ['rgba(136, 136, 136, 0.3)', 'rgba(136, 136, 136, 0.1)'];

        switch (miniboss.operacion) {
            case 'suma':
                return ['rgba(250, 112, 154, 0.3)', 'rgba(254, 225, 64, 0.3)'];
            case 'mult':
                return ['rgba(79, 172, 254, 0.3)', 'rgba(0, 242, 254, 0.3)'];
            case 'div':
                return ['rgba(245, 93, 251, 0.3)', 'rgba(245, 87, 108, 0.3)'];
            default:
                return ['rgba(102, 126, 234, 0.3)', 'rgba(118, 75, 162, 0.3)'];
        }
    };

    const getEmoji = () => {
        switch (miniboss.operacion) {
            case 'suma':
                return '🐉';
            case 'mult':
                return '⚔️';
            case 'div':
                return '🛡️';
            default:
                return '👾';
        }
    };

    const getBorderColor = () => {
        if (completed) return '#34C759';
        if (!canAttempt) return '#888888';
        return '#FFD700';
    };

    return (
        <TouchableOpacity
            onPress={canAttempt && !completed ? onPress : undefined}
            disabled={!canAttempt || completed}
            activeOpacity={0.8}
            style={[styles.container, !canAttempt && styles.disabledContainer]}
        >
            <LinearGradient
                colors={getGradientColors()}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={[styles.card, { borderColor: getBorderColor() }]}
            >
                {completed && (
                    <View style={styles.completedBadge}>
                        <Text style={styles.completedText}>✓ Completado</Text>
                    </View>
                )}

                {!canAttempt && !completed && (
                    <View style={styles.lockedBadge}>
                        <Text style={styles.lockedText}>🔒 Bloqueado</Text>
                    </View>
                )}

                <View style={styles.header}>
                    <Text style={styles.emoji}>{getEmoji()}</Text>
                    <View style={styles.headerInfo}>
                        <Text style={[styles.title, !canAttempt && styles.disabledText]}>
                            {miniboss.nombre}
                        </Text>
                        <Text style={[styles.description, !canAttempt && styles.disabledText]}>
                            {miniboss.descripcion}
                        </Text>
                    </View>
                </View>

                <View style={styles.requirements}>
                    <View style={styles.requirement}>
                        <Text style={styles.requirementIcon}>📝</Text>
                        <Text style={styles.requirementText}>
                            {miniboss.num_ejercicios} ejercicios
                        </Text>
                    </View>

                    {miniboss.tiempo_limite_segundos > 0 && (
                        <View style={styles.requirement}>
                            <Text style={styles.requirementIcon}>⏱️</Text>
                            <Text style={styles.requirementText}>
                                {miniboss.tiempo_limite_segundos}s límite
                            </Text>
                        </View>
                    )}

                    <View style={styles.requirement}>
                        <Text style={styles.requirementIcon}>🎯</Text>
                        <Text style={styles.requirementText}>
                            ≥{miniboss.acierto_minimo_porcentaje}% acierto
                        </Text>
                    </View>

                    {!miniboss.permite_reintentos && (
                        <View style={styles.requirement}>
                            <Text style={styles.requirementIcon}>⚠️</Text>
                            <Text style={styles.requirementText}>0 reintentos</Text>
                        </View>
                    )}
                </View>

                {miniboss.desbloquea && (
                    <View style={styles.rewardContainer}>
                        <Text style={styles.rewardLabel}>Desbloquea:</Text>
                        <Text style={styles.rewardValue}>
                            {miniboss.desbloquea.toUpperCase()}
                        </Text>
                    </View>
                )}

                {!canAttempt && reason && !completed && (
                    <View style={styles.reasonContainer}>
                        <Text style={styles.reasonText}>{reason}</Text>
                    </View>
                )}

                {canAttempt && !completed && onPress && (
                    <View style={styles.actionButton}>
                        <LinearGradient
                            colors={['#FFD700', '#FFA500']}
                            start={{ x: 0, y: 0 }}
                            end={{ x: 1, y: 0 }}
                            style={styles.buttonGradient}
                        >
                            <Text style={styles.buttonText}>INTENTAR</Text>
                        </LinearGradient>
                    </View>
                )}

                {completed && (
                    <View style={styles.completedButton}>
                        <Text style={styles.completedButtonText}>YA COMPLETADO ✓</Text>
                    </View>
                )}
            </LinearGradient>
        </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    container: {
        marginBottom: 16,
    },
    disabledContainer: {
        opacity: 0.7,
    },
    card: {
        borderRadius: 20,
        padding: 20,
        borderWidth: 2,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 8,
        elevation: 6,
    },
    completedBadge: {
        position: 'absolute',
        top: 12,
        right: 12,
        backgroundColor: '#34C759',
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 12,
    },
    completedText: {
        fontSize: 12,
        fontWeight: 'bold',
        color: '#FFFFFF',
    },
    lockedBadge: {
        position: 'absolute',
        top: 12,
        right: 12,
        backgroundColor: '#888888',
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 12,
    },
    lockedText: {
        fontSize: 12,
        fontWeight: 'bold',
        color: '#FFFFFF',
    },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 16,
    },
    emoji: {
        fontSize: 48,
        marginRight: 16,
    },
    headerInfo: {
        flex: 1,
    },
    title: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginBottom: 4,
    },
    description: {
        fontSize: 14,
        color: 'rgba(255, 255, 255, 0.8)',
    },
    disabledText: {
        color: 'rgba(255, 255, 255, 0.5)',
    },
    requirements: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 12,
        marginBottom: 16,
    },
    requirement: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 8,
    },
    requirementIcon: {
        fontSize: 14,
        marginRight: 6,
    },
    requirementText: {
        fontSize: 13,
        color: '#FFFFFF',
        fontWeight: '500',
    },
    rewardContainer: {
        backgroundColor: 'rgba(255, 215, 0, 0.2)',
        borderRadius: 12,
        padding: 12,
        marginBottom: 12,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
    },
    rewardLabel: {
        fontSize: 14,
        color: 'rgba(255, 255, 255, 0.9)',
        marginRight: 8,
    },
    rewardValue: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#FFD700',
    },
    reasonContainer: {
        backgroundColor: 'rgba(0, 0, 0, 0.3)',
        borderRadius: 8,
        padding: 12,
        marginBottom: 12,
    },
    reasonText: {
        fontSize: 13,
        color: 'rgba(255, 255, 255, 0.7)',
        textAlign: 'center',
    },
    actionButton: {
        borderRadius: 12,
        overflow: 'hidden',
    },
    buttonGradient: {
        paddingVertical: 14,
        alignItems: 'center',
    },
    buttonText: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#FFFFFF',
    },
    completedButton: {
        backgroundColor: 'rgba(52, 199, 89, 0.3)',
        paddingVertical: 14,
        borderRadius: 12,
        alignItems: 'center',
    },
    completedButtonText: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#34C759',
    },
});

export default MinibossCard;
