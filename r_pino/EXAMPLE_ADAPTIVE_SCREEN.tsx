/**
 * Example: How to Create a New Adaptive Screen
 * 
 * This file shows the pattern for creating new screens that adapt
 * to different screen sizes for optimal web experience.
 */

import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { AdaptiveContainer } from '../components/AdaptiveContainer';
import { useResponsive } from '../hooks/useResponsive';
import { responsiveValue, spacing } from '../utils/responsive';

export default function ExampleAdaptiveScreen() {
    // 1. Use the responsive hook to get screen size info
    const { isDesktop, isTabletOrDesktop, isMobile } = useResponsive();

    return (
        // 2. Wrap your content in AdaptiveContainer
        //    - centerOnDesktop: centers content on large screens
        //    - maxWidth: maximum width of content (prevents over-stretching)
        <AdaptiveContainer centerOnDesktop={true} maxWidth={900}>
            <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>

                {/* Header Section - Same on all devices */}
                <View style={styles.header}>
                    <Text style={styles.title}>My Adaptive Screen</Text>
                    <Text style={styles.subtitle}>Looks great everywhere!</Text>
                </View>

                {/* 3. Use conditional styles for different layouts */}
                {/* On desktop: 2-column grid, On mobile: stacked */}
                <View style={[
                    styles.cardsContainer,
                    isDesktop && styles.cardsContainerDesktop
                ]}>
                    {/* Card 1 */}
                    <View style={[
                        styles.card,
                        isDesktop && styles.cardDesktop
                    ]}>
                        <Text style={styles.cardTitle}>Card 1</Text>
                        <Text style={styles.cardContent}>
                            This card will appear next to Card 2 on desktop,
                            but stacked on mobile.
                        </Text>
                    </View>

                    {/* Card 2 */}
                    <View style={[
                        styles.card,
                        isDesktop && styles.cardDesktop
                    ]}>
                        <Text style={styles.cardTitle}>Card 2</Text>
                        <Text style={styles.cardContent}>
                            Responsive layouts make your app feel native
                            on every platform.
                        </Text>
                    </View>
                </View>

                {/* 4. Conditional rendering based on screen size */}
                {isDesktop ? (
                    <DesktopOnlyFeature />
                ) : (
                    <MobileOptimizedFeature />
                )}

                {/* 5. Buttons with responsive layout */}
                <View style={[
                    styles.buttonContainer,
                    isDesktop && styles.buttonContainerDesktop
                ]}>
                    <TouchableOpacity style={[
                        styles.button,
                        isDesktop && styles.buttonDesktop
                    ]}>
                        <Text style={styles.buttonText}>Action 1</Text>
                    </TouchableOpacity>

                    <TouchableOpacity style={[
                        styles.button,
                        isDesktop && styles.buttonDesktop
                    ]}>
                        <Text style={styles.buttonText}>Action 2</Text>
                    </TouchableOpacity>
                </View>
            </ScrollView>
        </AdaptiveContainer>
    );
}

// Example of desktop-only component
function DesktopOnlyFeature() {
    return (
        <View style={styles.desktopFeature}>
            <Text style={styles.featureTitle}>Desktop-Specific Feature</Text>
            <Text style={styles.featureText}>
                This shows extra information on desktop where there's more space
            </Text>
        </View>
    );
}

// Example of mobile-optimized component
function MobileOptimizedFeature() {
    return (
        <View style={styles.mobileFeature}>
            <Text style={styles.featureTitle}>Mobile-Optimized View</Text>
            <Text style={styles.featureText}>
                This shows a simpler version on mobile for better touch interaction
            </Text>
        </View>
    );
}

const styles = StyleSheet.create({
    // ===== Container Styles =====
    container: {
        flex: 1,
        backgroundColor: '#F5F5F7',
    },
    contentContainer: {
        padding: 20,
        paddingTop: 60,
    },

    // ===== Header Styles =====
    header: {
        marginBottom: 30,
        alignItems: 'center',
    },
    title: {
        fontSize: 32,
        fontWeight: 'bold',
        color: '#007AFF',
        marginBottom: 8,
    },
    subtitle: {
        fontSize: 16,
        color: '#666',
    },

    // ===== Cards Container =====
    // Mobile: Vertical stack
    cardsContainer: {
        gap: 16,
        marginBottom: 24,
    },
    // Desktop: Horizontal grid
    cardsContainerDesktop: {
        flexDirection: 'row',
        alignItems: 'stretch', // Equal height cards
    },

    // ===== Individual Card =====
    // Mobile: Full width
    card: {
        backgroundColor: 'white',
        borderRadius: 16,
        padding: 24,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 3,
    },
    // Desktop: Equal flex distribution
    cardDesktop: {
        flex: 1,
    },

    cardTitle: {
        fontSize: 20,
        fontWeight: '600',
        color: '#333',
        marginBottom: 12,
    },
    cardContent: {
        fontSize: 14,
        color: '#666',
        lineHeight: 20,
    },

    // ===== Button Container =====
    // Mobile: Vertical stack
    buttonContainer: {
        gap: 12,
        marginTop: 24,
    },
    // Desktop: Horizontal layout
    buttonContainerDesktop: {
        flexDirection: 'row',
        gap: 16,
    },

    // ===== Buttons =====
    // Mobile: Full width
    button: {
        backgroundColor: '#007AFF',
        borderRadius: 12,
        padding: 18,
        alignItems: 'center',
    },
    // Desktop: Equal flex distribution
    buttonDesktop: {
        flex: 1,
    },
    buttonText: {
        color: 'white',
        fontSize: 16,
        fontWeight: '600',
    },

    // ===== Conditional Features =====
    desktopFeature: {
        backgroundColor: '#E3F2FD',
        borderRadius: 12,
        padding: 20,
        marginBottom: 24,
        borderLeftWidth: 4,
        borderLeftColor: '#2196F3',
    },
    mobileFeature: {
        backgroundColor: '#FFF3E0',
        borderRadius: 12,
        padding: 16,
        marginBottom: 24,
        borderLeftWidth: 4,
        borderLeftColor: '#FF9800',
    },
    featureTitle: {
        fontSize: 18,
        fontWeight: '600',
        color: '#333',
        marginBottom: 8,
    },
    featureText: {
        fontSize: 14,
        color: '#666',
        lineHeight: 20,
    },
});

// ===== Alternative Pattern: Using responsive utility directly in styles =====

// You can also calculate responsive values directly:
const alternativeStyles = StyleSheet.create({
    dynamicPadding: {
        // Mobile: 16px, Tablet: 24px, Desktop: 32px
        padding: responsiveValue({
            mobile: spacing.md,
            tablet: spacing.lg,
            desktop: spacing.xl,
        }),
    },

    dynamicFontSize: {
        fontSize: responsiveValue({
            mobile: 14,
            tablet: 16,
            desktop: 18,
        }),
    },
});

// ===== Best Practices Summary =====

/**
 * 1. ALWAYS wrap main content in AdaptiveContainer
 * 2. Use useResponsive hook for conditional logic
 * 3. Define base styles for mobile first
 * 4. Add desktop variants with descriptive names (e.g., styleDesktop)
 * 5. Use flexDirection: 'row' for desktop grids
 * 6. Use gap for spacing (cleaner than margins)
 * 7. Test at breakpoints: 768px and 1024px
 * 8. Verify mobile experience unchanged
 */

/**
 * Common Patterns:
 * 
 * Cards Side-by-Side on Desktop:
 *   container: { gap: 16 }
 *   containerDesktop: { flexDirection: 'row' }
 *   card: { flex: 1 }
 * 
 * Buttons Horizontal on Desktop:
 *   buttonContainer: { gap: 12 }
 *   buttonContainerDesktop: { flexDirection: 'row', gap: 16 }
 *   button: { flex: 1 }
 * 
 * Centered Content:
 *   Use AdaptiveContainer with maxWidth prop
 * 
 * Conditional Rendering:
 *   {isDesktop ? <DesktopUI /> : <MobileUI />}
 * 
 * Conditional Styles:
 *   style={[baseStyle, isDesktop && desktopStyle]}
 */
