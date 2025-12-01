import React, { useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Animated, {
    useSharedValue,
    useAnimatedStyle,
    withSpring,
    withTiming,
    withDelay,
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';

interface RewardCardProps {
    icon: string;
    label: string;
    value: number | string;
    color: string[];
    delay?: number;
    showPlus?: boolean;
}

export const RewardCard: React.FC<RewardCardProps> = ({
    icon,
    label,
    value,
    color,
    delay = 0,
    showPlus = true,
}) => {
    const scale = useSharedValue(0);
    const opacity = useSharedValue(0);
    const translateY = useSharedValue(20);

    useEffect(() => {
        // Animación de entrada con delay
        scale.value = withDelay(
            delay,
            withSpring(1, {
                damping: 10,
                stiffness: 100,
            })
        );

        opacity.value = withDelay(delay, withTiming(1, { duration: 300 }));

        translateY.value = withDelay(
            delay,
            withSpring(0, {
                damping: 12,
                stiffness: 120,
            })
        );
    }, [delay]);

    const animatedStyle = useAnimatedStyle(() => {
        return {
            transform: [
                { scale: scale.value },
                { translateY: translateY.value },
            ],
            opacity: opacity.value,
        };
    });

    return (
        <Animated.View style={[styles.container, animatedStyle]}>
            <LinearGradient
                colors={color as [string, string, ...string[]]}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={styles.gradient}
            >
                <Text style={styles.icon}>{icon}</Text>
                <View style={styles.textContainer}>
                    <Text style={styles.value}>
                        {showPlus && typeof value === 'number' && value > 0 ? '+' : ''}
                        {value}
                    </Text>
                    <Text style={styles.label}>{label}</Text>
                </View>
            </LinearGradient>
        </Animated.View>
    );
};

const styles = StyleSheet.create({
    container: {
        marginVertical: 6,
    },
    gradient: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: 16,
        borderRadius: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 6,
        elevation: 6,
    },
    icon: {
        fontSize: 32,
        marginRight: 16,
    },
    textContainer: {
        flex: 1,
    },
    value: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginBottom: 2,
    },
    label: {
        fontSize: 14,
        color: 'rgba(255, 255, 255, 0.9)',
        fontWeight: '500',
    },
});

export default RewardCard;
