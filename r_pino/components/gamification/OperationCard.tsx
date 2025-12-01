import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import {
    Operation,
    OPERATION_NAMES,
    OPERATION_ICONS,
    OPERATION_COLORS,
    LEVEL_NAMES,
    calculateLevelProgress,
} from '../../services/gamification/types';
import ProgressBar from './ProgressBar';
import LevelBadge from './LevelBadge';

interface OperationCardProps {
    operation: Operation;
    onPress?: () => void;
    showProgress?: boolean;
}

export const OperationCard: React.FC<OperationCardProps> = ({
    operation,
    onPress,
    showProgress = true,
}) => {
    const isLocked = !operation.unlocked;
    const operationName = OPERATION_NAMES[operation.operacion];
    const operationIcon = OPERATION_ICONS[operation.operacion];
    const operationColor = OPERATION_COLORS[operation.operacion];
    const levelName = LEVEL_NAMES[operation.nivel_dominio];

    const progress = calculateLevelProgress(
        operation.pd_operacion,
        operation.nivel_dominio
    );

    const CardContent = () => (
        <>
            {isLocked && (
                <View style={styles.lockedOverlay}>
                    <Text style={styles.lockIcon}>🔒</Text>
                    <Text style={styles.lockedText}>Bloqueada</Text>
                </View>
            )}

            <LinearGradient
                colors={
                    isLocked
                        ? ['rgba(136, 136, 136, 0.3)', 'rgba(136, 136, 136, 0.3)']
                        : [`${operationColor}40`, `${operationColor}20`]
                }
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={styles.gradient}
            >
                <View style={styles.header}>
                    <View style={styles.titleContainer}>
                        <Text style={styles.operationIcon}>{operationIcon}</Text>
                        <View>
                            <Text style={[styles.operationName, isLocked && styles.lockedText]}>
                                {operationName}
                            </Text>
                            <Text style={[styles.levelName, isLocked && styles.lockedSubText]}>
                                {levelName}
                            </Text>
                        </View>
                    </View>

                    <LevelBadge
                        level={operation.nivel_dominio}
                        size="medium"
                        animated={false}
                    />
                </View>

                {showProgress && !isLocked && (
                    <View style={styles.progressSection}>
                        <View style={styles.statsRow}>
                            <Text style={styles.statLabel}>PD: {operation.pd_operacion}</Text>
                            <Text style={styles.statLabel}>
                                {operation.ejercicios_correctos}/{operation.ejercicios_totales} correctos
                            </Text>
                        </View>

                        <ProgressBar
                            progress={progress}
                            color={[operationColor, `${operationColor}CC`]}
                            height={10}
                            animated={true}
                            glowEffect={operation.nivel_dominio >= 4}
                        />

                        {operation.miniboss_completed && (
                            <View style={styles.minibossTag}>
                                <Text style={styles.minibossText}>
                                    🏆 Mini-jefe completado
                                </Text>
                            </View>
                        )}
                    </View>
                )}

                {isLocked && (
                    <View style={styles.lockedInfo}>
                        <Text style={styles.lockedHint}>
                            Completa requisitos para desbloquear
                        </Text>
                    </View>
                )}
            </LinearGradient>
        </>
    );

    if (onPress && !isLocked) {
        return (
            <TouchableOpacity
                style={styles.card}
                onPress={onPress}
                activeOpacity={0.8}
            >
                <CardContent />
            </TouchableOpacity>
        );
    }

    return (
        <View style={[styles.card, isLocked && styles.lockedCard]}>
            <CardContent />
        </View>
    );
};

const styles = StyleSheet.create({
    card: {
        marginBottom: 16,
        borderRadius: 16,
        overflow: 'hidden',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 6,
        elevation: 6,
    },
    lockedCard: {
        opacity: 0.6,
    },
    gradient: {
        padding: 16,
        borderWidth: 2,
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: 16,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 12,
    },
    titleContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        flex: 1,
    },
    operationIcon: {
        fontSize: 32,
        marginRight: 12,
    },
    operationName: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#FFFFFF',
    },
    levelName: {
        fontSize: 13,
        color: 'rgba(255, 255, 255, 0.8)',
        fontWeight: '500',
        marginTop: 2,
    },
    progressSection: {
        marginTop: 8,
    },
    statsRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 8,
    },
    statLabel: {
        fontSize: 12,
        color: 'rgba(255, 255, 255, 0.9)',
        fontWeight: '500',
    },
    minibossTag: {
        marginTop: 8,
        paddingVertical: 4,
        paddingHorizontal: 8,
        backgroundColor: 'rgba(255, 215, 0, 0.2)',
        borderRadius: 8,
        alignSelf: 'flex-start',
    },
    minibossText: {
        fontSize: 11,
        color: '#FFD700',
        fontWeight: '600',
    },
    lockedOverlay: {
        position: 'absolute',
        top: 12,
        right: 12,
        zIndex: 10,
        alignItems: 'center',
    },
    lockIcon: {
        fontSize: 24,
        marginBottom: 4,
    },
    lockedText: {
        color: 'rgba(255, 255, 255, 0.5)',
    },
    lockedSubText: {
        color: 'rgba(255, 255, 255, 0.4)',
    },
    lockedInfo: {
        marginTop: 12,
        padding: 8,
        backgroundColor: 'rgba(0, 0, 0, 0.2)',
        borderRadius: 8,
    },
    lockedHint: {
        fontSize: 12,
        color: 'rgba(255, 255, 255, 0.6)',
        textAlign: 'center',
    },
});

export default OperationCard;
