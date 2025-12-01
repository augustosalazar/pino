import React, { useEffect } from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import Animated, {
    useSharedValue,
    useAnimatedStyle,
    withSpring,
    withSequence,
    withTiming,
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';
import { LEVEL_COLORS, LEVEL_NAMES } from '../../services/gamification/types';

interface LevelBadgeProps {
    level: number; // 0-5
    size?: 'small' | 'medium' | 'large';
    showName?: boolean;
    animated?: boolean;
    celebrateOnMount?: boolean;
    style?: ViewStyle;
}

export const LevelBadge: React.FC<LevelBadgeProps> = ({
    level,
    size = 'medium',
    showName = false,
    animated = true,
    celebrateOnMount = false,
    style,
}) => {
    const scale = useSharedValue(0);
    const rotate = useSharedValue(0);

    useEffect(() => {
        if (animated) {
            if (celebrateOnMount) {
                // Animación de celebración
                scale.value = withSequence(
                    withSpring(1.3, { damping: 8 }),
                    withSpring(1, { damping: 10 })
                );
                rotate.value = withSequence(
                    withTiming(-10, { duration: 100 }),
                    withTiming(10, { duration: 100 }),
                    withTiming(-10, { duration: 100 }),
                    withTiming(0, { duration: 100 })
                );
            } else {
                scale.value = withSpring(1, {
                    damping: 12,
                    stiffness: 100,
                });
            }
        } else {
            scale.value = 1;
        }
    }, [animated, celebrateOnMount]);

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
            badgeSize: 40,
            fontSize: 16,
            borderWidth: 2,
            nameSize: 10,
        },
        medium: {
            badgeSize: 60,
            fontSize: 24,
            borderWidth: 3,
            nameSize: 12,
        },
        large: {
            badgeSize: 80,
            fontSize: 32,
            borderWidth: 4,
            nameSize: 14,
        },
    };

    const currentSize = sizeStyles[size];
    const levelColor = LEVEL_COLORS[level] || LEVEL_COLORS[0];
    const levelName = LEVEL_NAMES[level] || 'Desconocido';

    // Efecto dorado para nivel 5
    const isMaxLevel = level === 5;
    const badgeColors = isMaxLevel
        ? ['#FFD700', '#FFA500', '#FFD700'] // Gradiente dorado
        : [levelColor, levelColor];

    return (
        <Animated.View style={[styles.container, animatedStyle, style]}>
            <LinearGradient
                colors={badgeColors}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={[
                    styles.badge,
                    {
                        width: currentSize.badgeSize,
                        height: currentSize.badgeSize,
                        borderRadius: currentSize.badgeSize / 2,
                        borderWidth: currentSize.borderWidth,
                    },
                    isMaxLevel && styles.maxLevelBadge,
                ]}
            >
                <Text
                    style={[
                        styles.levelText,
                        {
                            fontSize: currentSize.fontSize,
                        },
                    ]}
                >
                    {level}
                </Text>
            </LinearGradient>

            {showName && (
                <Text
                    style={[
                        styles.nameText,
                        {
                            fontSize: currentSize.nameSize,
                            color: levelColor,
                        },
                    ]}
                >
                    {levelName}
                </Text>
            )}

            {isMaxLevel && (
                <View style={styles.crownContainer}>
                    <Text style={styles.crown}>👑</Text>
                </View>
            )}
        </Animated.View>
    );
};

const styles = StyleSheet.create({
    container: {
        alignItems: 'center',
        justifyContent: 'center',
    },
    badge: {
        alignItems: 'center',
        justifyContent: 'center',
        borderColor: 'rgba(255, 255, 255, 0.5)',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.4,
        shadowRadius: 6,
        elevation: 8,
    },
    maxLevelBadge: {
        borderColor: '#FFD700',
        shadowColor: '#FFD700',
        shadowOpacity: 0.8,
        shadowRadius: 12,
    },
    levelText: {
        fontWeight: 'bold',
        color: '#FFFFFF',
        textShadowColor: 'rgba(0, 0, 0, 0.5)',
        textShadowOffset: { width: 0, height: 2 },
        textShadowRadius: 4,
    },
    nameText: {
        marginTop: 6,
        fontWeight: '600',
        textAlign: 'center',
    },
    crownContainer: {
        position: 'absolute',
        top: -10,
        right: -5,
    },
    crown: {
        fontSize: 20,
        textShadowColor: 'rgba(0, 0, 0, 0.3)',
        textShadowOffset: { width: 0, height: 2 },
        textShadowRadius: 3,
    },
});

export default LevelBadge;
