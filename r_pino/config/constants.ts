/**
 * App Constants
 * Centralized constants for the application
 */

import { config } from './index';

// Export BASE_URL for backward compatibility and easy access
export const BASE_URL = config.api.baseUrl;

// Roble configuration
export const ROBLE_PROJECT_ID = config.roble.projectId;
export const ROBLE_BASE_URL = config.roble.baseUrl;

// API Endpoints
export const API_ENDPOINTS = {
    // User endpoints
    USERS_ENSURE: '/users/ensure',
    USER_PROFILE: (userRef: string) => `/users/${userRef}/profile`,

    // Session endpoints
    SESSIONS_START: '/sessions/start',
    SESSION_COMPLETE: (sessionId: string) => `/sessions/${sessionId}/complete`,

    // Gamification endpoints
    USER_GAMIFICATION: (userRef: string) => `/users/${userRef}/gamification`,
    MINIBOSSES: '/minibosses',
    MINIBOSS_START: (userRef: string, operacion: string) =>
        `/users/${userRef}/miniboss/${operacion}/start`,
    MINIBOSS_COMPLETE: (userRef: string, operacion: string) =>
        `/users/${userRef}/miniboss/${operacion}/complete`,
    LEADERBOARD_WEEKLY: '/leaderboard/weekly',

    // Admin endpoints
    INSTITUTION_STATS: (institutionRef: string) => `/institutions/${institutionRef}/stats`,
};

// App settings
export const APP_SETTINGS = {
    // Session settings
    DEFAULT_EXERCISES_PER_SESSION: 10,
    MIN_EXERCISES_PER_SESSION: 5,
    MAX_EXERCISES_PER_SESSION: 20,

    // Gamification settings
    MAX_PP_PER_DAY: 30,

    // UI settings
    REFRESH_INTERVAL: 30000, // 30 seconds
    ANIMATION_DURATION: 300,
};

export default {
    BASE_URL,
    ROBLE_PROJECT_ID,
    ROBLE_BASE_URL,
    API_ENDPOINTS,
    APP_SETTINGS,
};
