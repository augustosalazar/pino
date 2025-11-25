import { Platform, Dimensions } from 'react-native';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

// Breakpoints for responsive design
export const BREAKPOINTS = {
    mobile: 0,
    tablet: 768,
    desktop: 1024,
    largeDesktop: 1440,
};

/**
 * Determines if the current platform is web
 */
export const isWeb = Platform.OS === 'web';

/**
 * Determines if the current platform is mobile web
 */
export const isMobileWeb = isWeb && SCREEN_WIDTH < BREAKPOINTS.tablet;

/**
 * Determines if the current platform is tablet or desktop web
 */
export const isTabletOrDesktop = isWeb && SCREEN_WIDTH >= BREAKPOINTS.tablet;

/**
 * Determines if the current screen is desktop size
 */
export const isDesktop = SCREEN_WIDTH >= BREAKPOINTS.desktop;

/**
 * Get the current breakpoint category
 */
export const getBreakpoint = (): 'mobile' | 'tablet' | 'desktop' | 'largeDesktop' => {
    if (SCREEN_WIDTH >= BREAKPOINTS.largeDesktop) return 'largeDesktop';
    if (SCREEN_WIDTH >= BREAKPOINTS.desktop) return 'desktop';
    if (SCREEN_WIDTH >= BREAKPOINTS.tablet) return 'tablet';
    return 'mobile';
};

/**
 * Get responsive value based on screen size
 */
export const responsiveValue = <T,>(values: {
    mobile: T;
    tablet?: T;
    desktop?: T;
    largeDesktop?: T;
}): T => {
    const breakpoint = getBreakpoint();
    
    if (breakpoint === 'largeDesktop' && values.largeDesktop !== undefined) {
        return values.largeDesktop;
    }
    if ((breakpoint === 'desktop' || breakpoint === 'largeDesktop') && values.desktop !== undefined) {
        return values.desktop;
    }
    if ((breakpoint === 'tablet' || breakpoint === 'desktop' || breakpoint === 'largeDesktop') && values.tablet !== undefined) {
        return values.tablet;
    }
    return values.mobile;
};

/**
 * Calculate responsive padding/margin
 */
export const spacing = {
    xs: responsiveValue({ mobile: 4, tablet: 6, desktop: 8 }),
    sm: responsiveValue({ mobile: 8, tablet: 12, desktop: 16 }),
    md: responsiveValue({ mobile: 16, tablet: 20, desktop: 24 }),
    lg: responsiveValue({ mobile: 24, tablet: 32, desktop: 40 }),
    xl: responsiveValue({ mobile: 32, tablet: 48, desktop: 64 }),
};

/**
 * Get maximum content width for web
 */
export const getMaxContentWidth = (): number => {
    return responsiveValue({
        mobile: SCREEN_WIDTH,
        tablet: 700,
        desktop: 900,
        largeDesktop: 1100,
    });
};
