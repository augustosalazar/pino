import React, { useEffect } from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import Animated, {
    useSharedValue,
    useAnimatedStyle,
    withRepeat,
    withSequence,
    withTiming,
} from 'react-native-reanimated';

interface StreakIndicatorProps {
    streakDays: number;
    size?: 'small' | 'medium' | 'large';
    animated?: boolean;
    showLabel?: boolean;
    style?: ViewStyle;
}

export const StreakIndicator: React.FC<StreakIndicatorProps> = ({
    streakDays,
    size = 'medium',
    animated = true,
    showLabel = true,
    style,
}) => {
    const scale = useSharedValue(1);
    const rotate = useSharedValue(0);

    useEffect(() => {
        if (animated && streakDays > 0) {
            // Animación de "fuego parpadeante"
            scale.value = withRepeat(
                withSequence(
                    withTiming(1.1, { duration: 500 }),
                    withTiming(1, { duration: 500 })
                ),
                -1, // Infinito
                true
            );

            // Pequeña rotación
            rotate.value = withRepeat(
                withSequence(
                    withTiming(-5, { duration: 400 }),
                    withTiming(5, { duration: 400 }),
                    withTiming(0, { duration: 400 })
                ),
                -1,
                true
            );
        }
    }, [animated, streakDays]);

    const animatedStyle = useAnimatedStyle(() => {
        return {
            transform: [
                { scale: scale.value },
                { rotate: `${rotate.value}deg` },
            ],
        };
    });

    const sizeStyles = {
        small: {
            emojiSize: 20,
            numberSize: 14,
            labelSize: 10,
            containerPadding: 8,
        },
        medium: {
            emojiSize: 28,
            numberSize: 18,
            labelSize: 12,
            containerPadding: 12,
        },
        large: {
            emojiSize: 36,
            numberSize: 24,
            labelSize: 14,
            containerPadding: 16,
        },
    };

    const currentSize = sizeStyles[size];

    // Color basado en la racha
    const getStreakColor = () => {
        if (streakDays === 0) return '#888888';
        if (streakDays < 3) return '#FFA500'; // Naranja
        if (streakDays < 7) return '#FF6347'; // Rojo brillante
        if (streakDays < 14) return '#FF4500'; // Rojo oscuro
        return '#FFD700'; // Dorado para rachas largas
    };

    const getStreakEmoji = () => {
        if (streakDays === 0) return '💨'; // Sin racha
        if (streakDays < 3) return '🔥';
        if (streakDays < 7) return '🔥🔥';
        if (streakDays < 14) return '🔥🔥🔥';
        return '🔥🔥🔥🔥'; // Racha épica
    };

    const streakColor = getStreakColor();
    const streakEmoji = getStreakEmoji();

    return (
        <View style={[styles.container, style]}>
            <View
                style={[
                    styles.badge,
                    {
                        padding: currentSize.containerPadding,
                        borderColor: streakColor,
                    },
                    streakDays === 0 && styles.inactiveBadge,
                ]}
            >
                <Animated.Text
                    style={[
                        styles.emoji,
                        animatedStyle,
                        { fontSize: currentSize.emojiSize },
                    ]}
                >
                    {streakEmoji}
                </Animated.Text>

                <Text
                    style={[
                        styles.number,
                        {
                            fontSize: currentSize.numberSize,
                            color: streakColor,
                        },
                    ]}
                >
                    {streakDays}
                </Text>
            </View>

            {showLabel && (
                <Text
                    style={[
                        styles.label,
                        {
                            fontSize: currentSize.labelSize,
                            color: streakColor,
                        },
                    ]}
                >
                    {streakDays === 0
                        ? 'Sin racha'
                        : streakDays === 1
                            ? '1 día'
                            : `${streakDays} días`}
                </Text>
            )}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        alignItems: 'center',
    },
    badge: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: 'rgba(30, 30, 50, 0.8)',
        borderRadius: 20,
        borderWidth: 2,
        shadowColor: '#FF6347',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.5,
        shadowRadius: 6,
        elevation: 4,
    },
    inactiveBadge: {
        shadowOpacity: 0.2,
        borderColor: '#888888',
    },
    emoji: {
        marginRight: 6,
    },
    number: {
        fontWeight: 'bold',
        textShadowColor: 'rgba(0, 0, 0, 0.3)',
        textShadowOffset: { width: 0, height: 1 },
        textShadowRadius: 2,
    },
    label: {
        marginTop: 6,
        fontWeight: '600',
    },
});

export default StreakIndicator;
