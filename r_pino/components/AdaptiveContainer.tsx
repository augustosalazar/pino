import React, { ReactNode } from 'react';
import { View, ViewStyle, ScrollView } from 'react-native';
import { useResponsive } from '../hooks/useResponsive';

interface AdaptiveContainerProps {
    children: ReactNode;
    style?: ViewStyle;
    centerOnDesktop?: boolean;
    maxWidth?: number;
    scrollable?: boolean;
}

/**
 * Adaptive container that centers content on larger screens
 * and provides optimal widths for different screen sizes
 */
export const AdaptiveContainer: React.FC<AdaptiveContainerProps> = ({
    children,
    style,
    centerOnDesktop = true,
    maxWidth,
    scrollable = false,
}) => {
    const { isTabletOrDesktop, width } = useResponsive();

    const containerStyle: ViewStyle = {
        flex: 1,
        width: '100%',
        ...(isTabletOrDesktop && centerOnDesktop
            ? {
                alignItems: 'center',
                backgroundColor: '#E8E8EA', // Slightly different background for desktop
            }
            : {}),
        ...style,
    };

    const contentStyle: ViewStyle = {
        flex: 1,
        width: '100%',
        ...(isTabletOrDesktop && centerOnDesktop
            ? {
                maxWidth: maxWidth || 900,
                width: '100%',
                backgroundColor: '#F5F5F7', // Original background for content
                shadowColor: '#000',
                shadowOffset: { width: 0, height: 0 },
                shadowOpacity: 0.1,
                shadowRadius: 20,
                elevation: 5,
            }
            : {}),
    };

    const Container = scrollable ? ScrollView : View;

    return (
        <View style={containerStyle}>
            <Container
                style={contentStyle}
                contentContainerStyle={scrollable ? { flexGrow: 1 } : undefined}
            >
                {children}
            </Container>
        </View>
    );
};
