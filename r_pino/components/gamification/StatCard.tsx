import React, { useEffect } from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import Animated, {
    useSharedValue,
    useAnimatedStyle,
    withSpring,
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';

interface StatCardProps {
    icon: string; // Emoji or icon
    label: string;
    value: number | string;
    color?: string | string[]; // Single color or gradient
    gradient?: boolean;
    size?: 'small' | 'medium' | 'large';
    animated?: boolean;
    style?: ViewStyle;
}

export const StatCard: React.FC<StatCardProps> = ({
    icon,
    label,
    value,
    color = ['#4facfe', '#00f2fe'],
    gradient = true,
    size = 'medium',
    animated = true,
    style,
}) => {
    const scale = useSharedValue(0);
    const opacity = useSharedValue(0);

    useEffect(() => {
        if (animated) {
            scale.value = withSpring(1, {
                damping: 12,
                stiffness: 100,
            });
            opacity.value = withSpring(1);
        } else {
            scale.value = 1;
            opacity.value = 1;
        }
    }, [animated]);

    const animatedStyle = useAnimatedStyle(() => {
        return {
            transform: [{ scale: scale.value }],
            opacity: opacity.value,
        };
    });

    const colors = Array.isArray(color) ? color : [color, color];

    const sizeStyles = {
        small: {
            padding: 12,
            iconSize: 24,
            valueSize: 18,
            labelSize: 11,
        },
        medium: {
            padding: 16,
            iconSize: 32,
            valueSize: 24,
            labelSize: 13,
        },
        large: {
            padding: 20,
            iconSize: 40,
            valueSize: 28,
            labelSize: 14,
        },
    };

    const currentSize = sizeStyles[size];

    return (
        <Animated.View style={[animatedStyle, style]}>
            {gradient ? (
                <LinearGradient
                    colors={colors}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 1 }}
                    style={[
                        styles.card,
                        {
                            padding: currentSize.padding,
                        },
                    ]}
                >
                    <View style={styles.content}>
                        <Text style={[styles.icon, { fontSize: currentSize.iconSize }]}>
                            {icon}
                        </Text>
                        <View style={styles.textContainer}>
                            <Text
                                style={[styles.value, { fontSize: currentSize.valueSize }]}
                                numberOfLines={1}
                            >
                                {value}
                            </Text>
                            <Text
                                style={[styles.label, { fontSize: currentSize.labelSize }]}
                                numberOfLines={1}
                            >
                                {label}
                            </Text>
                        </View>
                    </View>
                </LinearGradient>
            ) : (
                <View
                    style={[
                        styles.card,
                        styles.solidCard,
                        {
                            padding: currentSize.padding,
                            backgroundColor: colors[0],
                        },
                    ]}
                >
                    <View style={styles.content}>
                        <Text style={[styles.icon, { fontSize: currentSize.iconSize }]}>
                            {icon}
                        </Text>
                        <View style={styles.textContainer}>
                            <Text
                                style={[styles.value, { fontSize: currentSize.valueSize }]}
                                numberOfLines={1}
                            >
                                {value}
                            </Text>
                            <Text
                                style={[styles.label, { fontSize: currentSize.labelSize }]}
                                numberOfLines={1}
                            >
                                {label}
                            </Text>
                        </View>
                    </View>
                </View>
            )}
        </Animated.View>
    );
};

const styles = StyleSheet.create({
    card: {
        borderRadius: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 6,
        elevation: 8,
    },
    solidCard: {
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.2)',
    },
    content: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    icon: {
        marginRight: 12,
    },
    textContainer: {
        flex: 1,
        alignItems: 'flex-end',
    },
    value: {
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginBottom: 2,
    },
    label: {
        color: 'rgba(255, 255, 255, 0.85)',
        fontWeight: '500',
    },
});

export default StatCard;
