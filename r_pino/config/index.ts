/**
 * App Configuration
 * Centralized configuration using Expo environment variables
 */

import Constants from 'expo-constants';

// Get environment variables from expo-constants
// These are set in .env file with EXPO_PUBLIC_ prefix
const expoConfig = Constants.expoConfig?.extra || {};

export const config = {
    // Roble Auth API
    roble: {
        projectId: process.env.EXPO_PUBLIC_ROBLE_PROJECT_ID || 'tracking_7d2ad2db74',
        baseUrl: process.env.EXPO_PUBLIC_ROBLE_BASE_URL || 'https://roble-api.openlab.uninorte.edu.co',
    },

    // Pine Server API
    api: {
        baseUrl: process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8000/api',
    },
};

// Helper to log configuration (useful for debugging)
export const logConfig = () => {
    console.log('🔧 App Configuration:');
    console.log('  Roble Project ID:', config.roble.projectId);
    console.log('  Roble Base URL:', config.roble.baseUrl);
    console.log('  API Base URL:', config.api.baseUrl);
};
