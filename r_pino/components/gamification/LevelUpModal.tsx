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
    withRepeat,
    Easing,
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';
import { LevelBadge } from './LevelBadge';

const { width, height } = Dimensions.get('window');

interface LevelUpModalProps {
    visible: boolean;
    oldLevel: number;
    newLevel: number;
    pdReward: number;
    onClose: () => void;
}

export const LevelUpModal: React.FC<LevelUpModalProps> = ({
    visible,
    oldLevel,
    newLevel,
    pdReward,
    onClose,
}) => {
    const scale = useSharedValue(0);
    const opacity = useSharedValue(0);
    const badgeScale = useSharedValue(0);
    const badgeRotate = useSharedValue(0);
    const glowOpacity = useSharedValue(0);

    useEffect(() => {
        if (visible) {
            // Background fade in
            opacity.value = withTiming(1, { duration: 300 });

            // Modal scale in
            scale.value = withSpring(1, {
                damping: 12,
                stiffness: 100,
            });

            // Badge epic entrance
            badgeScale.value = withSequence(
                withSpring(1.5, { damping: 6 }),
                withSpring(1, { damping: 10 })
            );

            badgeRotate.value = withSequence(
                withTiming(-15, { duration: 100 }),
                withTiming(15, { duration: 100 }),
                withTiming(-10, { duration: 100 }),
                withTiming(10, { duration: 100 }),
                withTiming(0, { duration: 100 })
            );

            // Pulsating glow
            glowOpacity.value = withRepeat(
                withSequence(
                    withTiming(0.8, { duration: 800, easing: Easing.inOut(Easing.ease) }),
                    withTiming(0.3, { duration: 800, easing: Easing.inOut(Easing.ease) })
                ),
                -1,
                true
            );
        } else {
            opacity.value = 0;
            scale.value = 0;
            badgeScale.value = 0;
            glowOpacity.value = 0;
        }
    }, [visible]);

    const overlayStyle = useAnimatedStyle(() => {
        return {
            opacity: opacity.value,
        };
    });

    const modalStyle = useAnimatedStyle(() => {
        return {
            transform: [{ scale: scale.value }],
        };
    });

    const badgeStyle = useAnimatedStyle(() => {
        return {
            transform: [
                { scale: badgeScale.value },
                { rotate: `${badgeRotate.value}deg` },
            ],
        };
    });

    const glowStyle = useAnimatedStyle(() => {
        return {
            opacity: glowOpacity.value,
        };
    });

    if (!visible) return null;

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
                        colors={['#667eea', '#764ba2', '#f093fb']}
                        start={{ x: 0, y: 0 }}
                        end={{ x: 1, y: 1 }}
                        style={styles.modalContent}
                    >
                        {/* Animated glow background */}
                        <Animated.View style={[styles.glow, glowStyle]} />

                        {/* Stars decoration */}
                        <View style={styles.starsContainer}>
                            <Text style={styles.star}>✨</Text>
                            <Text style={[styles.star, styles.starRight]}>✨</Text>
                        </View>

                        {/* Title */}
                        <Text style={styles.title}>¡NIVEL MEJORADO!</Text>

                        {/* Level badges */}
                        <View style={styles.levelsContainer}>
                            <View style={styles.levelItem}>
                                <LevelBadge
                                    level={oldLevel}
                                    size="large"
                                    showName={false}
                                    animated={false}
                                />
                                <Text style={styles.levelLabel}>Nivel {oldLevel}</Text>
                            </View>

                            <Text style={styles.arrow}>→</Text>

                            <Animated.View style={[styles.levelItem, badgeStyle]}>
                                <LevelBadge
                                    level={newLevel}
                                    size="large"
                                    showName={false}
                                    celebrateOnMount={true}
                                    animated={true}
                                />
                                <Text style={styles.levelLabel}>Nivel {newLevel}</Text>
                            </Animated.View>
                        </View>

                        {/* Reward */}
                        <View style={styles.rewardContainer}>
                            <Text style={styles.rewardTitle}>Recompensa de Nivel</Text>
                            <View style={styles.rewardCard}>
                                <Text style={styles.rewardIcon}>🏆</Text>
                                <Text style={styles.rewardValue}>+{pdReward} PD</Text>
                            </View>
                            <Text style={styles.rewardDescription}>
                                Puntos de Dominio añadidos a tu progreso
                            </Text>
                        </View>

                        {/* Motivational message */}
                        <Text style={styles.message}>
                            ¡Sigue así! Cada nivel te acerca a desbloquear nuevas operaciones.
                        </Text>

                        {/* Close button */}
                        <TouchableOpacity
                            style={styles.closeButton}
                            onPress={onClose}
                            activeOpacity={0.8}
                        >
                            <LinearGradient
                                colors={['#FFD700', '#FFA500']}
                                start={{ x: 0, y: 0 }}
                                end={{ x: 1, y: 0 }}
                                style={styles.closeButtonGradient}
                            >
                                <Text style={styles.closeButtonText}>¡Continuar!</Text>
                            </LinearGradient>
                        </TouchableOpacity>
                    </LinearGradient>
                </Animated.View>
            </Animated.View>
        </Modal>
    );
};

const styles = StyleSheet.create({
    overlay: {
        flex: 1,
        backgroundColor: 'rgba(0, 0, 0, 0.85)',
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
    glow: {
        position: 'absolute',
        top: -100,
        left: -100,
        right: -100,
        bottom: -100,
        backgroundColor: 'rgba(255, 215, 0, 0.3)',
        borderRadius: 200,
        shadowColor: '#FFD700',
        shadowOffset: { width: 0, height: 0 },
        shadowOpacity: 0.8,
        shadowRadius: 50,
    },
    starsContainer: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        width: '100%',
        marginBottom: 16,
        position: 'relative',
    },
    star: {
        fontSize: 32,
    },
    starRight: {
        alignSelf: 'flex-end',
    },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        color: '#FFFFFF',
        textAlign: 'center',
        marginBottom: 24,
        textShadowColor: 'rgba(0, 0, 0, 0.3)',
        textShadowOffset: { width: 0, height: 2 },
        textShadowRadius: 4,
    },
    levelsContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 24,
        gap: 20,
    },
    levelItem: {
        alignItems: 'center',
    },
    levelLabel: {
        fontSize: 14,
        fontWeight: '600',
        color: '#FFFFFF',
        marginTop: 8,
    },
    arrow: {
        fontSize: 32,
        color: '#FFD700',
        fontWeight: 'bold',
    },
    rewardContainer: {
        alignItems: 'center',
        marginBottom: 20,
        width: '100%',
    },
    rewardTitle: {
        fontSize: 16,
        fontWeight: '600',
        color: 'rgba(255, 255, 255, 0.9)',
        marginBottom: 12,
    },
    rewardCard: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: 'rgba(255, 255, 255, 0.15)',
        paddingVertical: 12,
        paddingHorizontal: 24,
        borderRadius: 16,
        marginBottom: 8,
    },
    rewardIcon: {
        fontSize: 28,
        marginRight: 12,
    },
    rewardValue: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#FFD700',
    },
    rewardDescription: {
        fontSize: 12,
        color: 'rgba(255, 255, 255, 0.7)',
        textAlign: 'center',
    },
    message: {
        fontSize: 14,
        color: 'rgba(255, 255, 255, 0.9)',
        textAlign: 'center',
        marginBottom: 24,
        paddingHorizontal: 16,
        lineHeight: 20,
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

export default LevelUpModal;
