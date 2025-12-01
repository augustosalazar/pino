import React, { useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Animated, {
    useSharedValue,
    useAnimatedStyle,
    withSpring,
    withTiming,
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';

interface ProgressBarProps {
    progress: number; // 0-100
    color?: string | string[]; // Single color or gradient
    height?: number;
    showLabel?: boolean;
    label?: string;
    animated?: boolean;
    glowEffect?: boolean;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
    progress,
    color = ['#4facfe', '#00f2fe'],
    height = 12,
    showLabel = false,
    label,
    animated = true,
    glowEffect = false,
}) => {
    const animatedProgress = useSharedValue(0);

    useEffect(() => {
        if (animated) {
            animatedProgress.value = withSpring(progress, {
                damping: 15,
                stiffness: 100,
            });
        } else {
            animatedProgress.value = progress;
        }
    }, [progress, animated]);

    const animatedStyle = useAnimatedStyle(() => {
        return {
            width: `${animatedProgress.value}%`,
        };
    });

    const colors = Array.isArray(color) ? color : [color, color];

    return (
        <View style={styles.container}>
            {showLabel && (
                <Text style={styles.label}>
                    {label || `${Math.round(progress)}%`}
                </Text>
            )}
            <View
                style={[
                    styles.track,
                    { height },
                    glowEffect && styles.glowContainer,
                ]}
            >
                <Animated.View style={[styles.fill, animatedStyle, { height }]}>
                    <LinearGradient
                        colors={colors}
                        start={{ x: 0, y: 0 }}
                        end={{ x: 1, y: 0 }}
                        style={styles.gradient}
                    />
                    {glowEffect && (
                        <View
                            style={[
                                styles.glow,
                                {
                                    shadowColor: colors[0],
                                    height: height + 4,
                                },
                            ]}
                        />
                    )}
                </Animated.View>
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        width: '100%',
    },
    label: {
        fontSize: 12,
        fontWeight: '600',
        color: '#FFFFFF',
        marginBottom: 4,
        textAlign: 'right',
    },
    track: {
        width: '100%',
        backgroundColor: 'rgba(255, 255, 255, 0.15)',
        borderRadius: 100,
        overflow: 'hidden',
        position: 'relative',
    },
    fill: {
        borderRadius: 100,
        overflow: 'hidden',
    },
    gradient: {
        flex: 1,
        width: '100%',
        height: '100%',
    },
    glowContainer: {
        shadowColor: '#FFD700',
        shadowOffset: { width: 0, height: 0 },
        shadowOpacity: 0.5,
        shadowRadius: 8,
    },
    glow: {
        position: 'absolute',
        top: -2,
        left: 0,
        right: 0,
        shadowOpacity: 0.8,
        shadowRadius: 6,
        shadowOffset: { width: 0, height: 0 },
    },
});

export default ProgressBar;
