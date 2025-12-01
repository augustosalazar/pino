import React, { useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    Modal,
    TouchableOpacity,
    Dimensions,
} from 'react-native';
import Animated, {
    useSharedValue,
    useAnimatedStyle,
    withSpring,
    withSequence,
    withTiming,
    withDelay,
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';
import { OPERATION_NAMES, OPERATION_ICONS, OPERATION_COLORS } from '../../services/gamification/types';

const { width, height } = Dimensions.get('window');

interface UnlockAnimationProps {
    visible: boolean;
    operationsUnlocked: string[]; // ['resta', 'mult', etc.]
    onClose: () => void;
}

export const UnlockAnimation: React.FC<UnlockAnimationProps> = ({
    visible,
    operationsUnlocked,
    onClose,
}) => {
    const opacity = useSharedValue(0);
    const scale = useSharedValue(0);
    const lockScale = useSharedValue(1);
    const lockOpacity = useSharedValue(1);
    const contentOpacity = useSharedValue(0);

    useEffect(() => {
        if (visible && operationsUnlocked.length > 0) {
            // Fade in overlay
            opacity.value = withTiming(1, { duration: 300 });

            // Scale in modal
            scale.value = withSpring(1, { damping: 10 });

            // Lock breaking animation
            lockScale.value = withSequence(
                withDelay(300, withSpring(1.2, { damping: 8 })),
                withDelay(100, withSpring(0, { damping: 6 }))
            );

            lockOpacity.value = withSequence(
                withDelay(300, withTiming(1, { duration: 200 })),
                withDelay(200, withTiming(0, { duration: 300 }))
            );

            // Content reveal
            contentOpacity.value = withDelay(
                800,
                withSpring(1, { damping: 12 })
            );
        } else {
            opacity.value = 0;
            scale.value = 0;
            lockScale.value = 1;
            lockOpacity.value = 1;
            contentOpacity.value = 0;
        }
    }, [visible, operationsUnlocked]);

    const overlayStyle = useAnimatedStyle(() => ({
        opacity: opacity.value,
    }));

    const modalStyle = useAnimatedStyle(() => ({
        transform: [{ scale: scale.value }],
    }));

    const lockStyle = useAnimatedStyle(() => ({
        transform: [{ scale: lockScale.value }],
        opacity: lockOpacity.value,
    }));

    const contentStyle = useAnimatedStyle(() => ({
        opacity: contentOpacity.value,
    }));

    if (!visible || operationsUnlocked.length === 0) return null;

    return (
        <Modal
            transparent
            visible={visible}
            animationType="none"
            onRequestClose={onClose}
        >
            <Animated.View style={[styles.overlay, overlayStyle]}>
                <Animated.View style={[styles.modalContainer, modalStyle]}>
                    <LinearGradient
                        colors={['#f093fb', '#f5576c', '#ffd200']}
                        start={{ x: 0, y: 0 }}
                        end={{ x: 1, y: 1 }}
                        style={styles.modalContent}
                    >
                        {/* Lock breaking animation */}
                        <Animated.View style={[styles.lockContainer, lockStyle]}>
                            <Text style={styles.lock}>🔓</Text>
                        </Animated.View>

                        {/* Content */}
                        <Animated.View style={[styles.content, contentStyle]}>
                            <Text style={styles.title}>¡DESBLOQUEADO!</Text>

                            <Text style={styles.subtitle}>
                                {operationsUnlocked.length === 1
                                    ? 'Nueva operación disponible'
                                    : 'Nuevas operaciones disponibles'}
                            </Text>

                            {/* Unlocked operations */}
                            <View style={styles.operationsContainer}>
                                {operationsUnlocked.map((operation, index) => {
                                    const operationKey = operation as 'suma' | 'resta' | 'mult' | 'div';
                                    const name = OPERATION_NAMES[operationKey];
                                    const icon = OPERATION_ICONS[operationKey];
                                    const color = OPERATION_COLORS[operationKey];

                                    return (
                                        <View
                                            key={operation}
                                            style={[
                                                styles.operationCard,
                                                { borderColor: color },
                                            ]}
                                        >
                                            <Text style={styles.operationIcon}>{icon}</Text>
                                            <Text style={styles.operationName}>{name}</Text>
                                        </View>
                                    );
                                })}
                            </View>

                            {/* Congratulations message */}
                            <View style={styles.messageContainer}>
                                <Text style={styles.message}>
                                    ¡Enhorabuena! Has cumplido todos los requisitos.
                                </Text>
                                <Text style={styles.submessage}>
                                    Ahora puedes practicar {operationsUnlocked.map(op =>
                                        OPERATION_NAMES[op as keyof typeof OPERATION_NAMES]
                                    ).join(' y ')}.
                                </Text>
                            </View>

                            {/* Close button */}
                            <TouchableOpacity
                                style={styles.closeButton}
                                onPress={onClose}
                                activeOpacity={0.8}
                            >
                                <LinearGradient
                                    colors={['#4facfe', '#00f2fe']}
                                    start={{ x: 0, y: 0 }}
                                    end={{ x: 1, y: 0 }}
                                    style={styles.closeButtonGradient}
                                >
                                    <Text style={styles.closeButtonText}>¡Empezar a Practicar!</Text>
                                </LinearGradient>
                            </TouchableOpacity>
                        </Animated.View>
                    </LinearGradient>
                </Animated.View>
            </Animated.View>
        </Modal>
    );
};

const styles = StyleSheet.create({
    overlay: {
        flex: 1,
        backgroundColor: 'rgba(0, 0, 0, 0.9)',
        justifyContent: 'center',
        alignItems: 'center',
    },
    modalContainer: {
        width: Math.min(width - 40, 400),
        maxHeight: height * 0.9,
    },
    modalContent: {
        borderRadius: 24,
        padding: 24,
        alignItems: 'center',
        position: 'relative',
        overflow: 'hidden',
    },
    lockContainer: {
        position: 'absolute',
        top: '40%',
        alignItems: 'center',
        justifyContent: 'center',
    },
    lock: {
        fontSize: 80,
    },
    content: {
        width: '100%',
        alignItems: 'center',
    },
    title: {
        fontSize: 32,
        fontWeight: 'bold',
        color: '#FFFFFF',
        textAlign: 'center',
        marginBottom: 8,
        textShadowColor: 'rgba(0, 0, 0, 0.5)',
        textShadowOffset: { width: 0, height: 2 },
        textShadowRadius: 4,
    },
    subtitle: {
        fontSize: 16,
        color: 'rgba(255, 255, 255, 0.9)',
        textAlign: 'center',
        marginBottom: 24,
    },
    operationsContainer: {
        width: '100%',
        gap: 12,
        marginBottom: 24,
    },
    operationCard: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: 'rgba(255, 255, 255, 0.15)',
        padding: 16,
        borderRadius: 16,
        borderWidth: 2,
    },
    operationIcon: {
        fontSize: 32,
        marginRight: 16,
    },
    operationName: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#FFFFFF',
        flex: 1,
    },
    messageContainer: {
        alignItems: 'center',
        marginBottom: 24,
    },
    message: {
        fontSize: 15,
        color: '#FFFFFF',
        textAlign: 'center',
        marginBottom: 8,
        fontWeight: '600',
    },
    submessage: {
        fontSize: 13,
        color: 'rgba(255, 255, 255, 0.8)',
        textAlign: 'center',
        lineHeight: 18,
    },
    closeButton: {
        width: '100%',
        borderRadius: 12,
        overflow: 'hidden',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 6,
        elevation: 8,
    },
    closeButtonGradient: {
        paddingVertical: 16,
        alignItems: 'center',
    },
    closeButtonText: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#FFFFFF',
    },
});

export default UnlockAnimation;
