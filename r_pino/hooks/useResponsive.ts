import { useState, useEffect } from 'react';
import { Dimensions, ScaledSize } from 'react-native';
import { getBreakpoint, isWeb, isTabletOrDesktop } from '../utils/responsive';

type Breakpoint = 'mobile' | 'tablet' | 'desktop' | 'largeDesktop';

/**
 * Hook to get current screen dimensions and breakpoint
 * Updates automatically when window is resized (important for web)
 */
export const useResponsive = () => {
    const [dimensions, setDimensions] = useState(() => Dimensions.get('window'));
    const [breakpoint, setBreakpoint] = useState<Breakpoint>(getBreakpoint);

    useEffect(() => {
        const subscription = Dimensions.addEventListener('change', ({ window }: { window: ScaledSize }) => {
            setDimensions(window);
            setBreakpoint(getBreakpoint());
        });

        return () => subscription?.remove();
    }, []);

    return {
        width: dimensions.width,
        height: dimensions.height,
        breakpoint,
        isWeb,
        isTabletOrDesktop: dimensions.width >= 768,
        isDesktop: dimensions.width >= 1024,
        isMobile: dimensions.width < 768,
    };
};
