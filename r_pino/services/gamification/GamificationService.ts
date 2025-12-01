// Gamification Service
import { BASE_URL } from '../../config/constants';
import {
    GamificationProfile,
    GamificationRewards,
    LeaderboardResponse,
    MinibossInfo,
    MinibossResult,
} from './types';

class GamificationService {
    private baseUrl: string;

    constructor() {
        this.baseUrl = BASE_URL;
    }

    /**
     * Get user's complete gamification profile
     */
    async getProfile(userRef: string): Promise<GamificationProfile> {
        try {
            const response = await fetch(
                `${this.baseUrl}/users/${userRef}/gamification`
            );

            if (!response.ok) {
                throw new Error(`Failed to get gamification profile: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('[GamificationService] Error getting profile:', error);
            throw error;
        }
    }

    /**
     * Get weekly leaderboard
     */
    async getWeeklyLeaderboard(
        institutionRef?: string,
        limit: number = 100
    ): Promise<LeaderboardResponse> {
        try {
            const params = new URLSearchParams();
            if (institutionRef) {
                params.append('institution_ref', institutionRef);
            }
            params.append('limit', limit.toString());

            const response = await fetch(
                `${this.baseUrl}/leaderboard/weekly?${params.toString()}`
            );

            if (!response.ok) {
                throw new Error(`Failed to get leaderboard: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('[GamificationService] Error getting leaderboard:', error);
            throw error;
        }
    }

    /**
     * Get list of all minibosses
     */
    async getMinibosses(): Promise<{ minibosses: MinibossInfo[] }> {
        try {
            const response = await fetch(`${this.baseUrl}/minibosses`);

            if (!response.ok) {
                throw new Error(`Failed to get minibosses: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('[GamificationService] Error getting minibosses:', error);
            throw error;
        }
    }

    /**
     * Start a miniboss challenge
     */
    async startMiniboss(
        userRef: string,
        operacion: 'suma' | 'mult' | 'div'
    ): Promise<{
        session_id: string;
        miniboss_info: MinibossInfo;
        exercises: any[];
        operacion: string;
    }> {
        try {
            const response = await fetch(
                `${this.baseUrl}/users/${userRef}/miniboss/${operacion}/start`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                }
            );

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `Failed to start miniboss: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('[GamificationService] Error starting miniboss:', error);
            throw error;
        }
    }

    /**
     * Complete a miniboss challenge
     */
    async completeMiniboss(
        userRef: string,
        operacion: 'suma' | 'mult' | 'div',
        exercises: any[]
    ): Promise<MinibossResult> {
        try {
            const response = await fetch(
                `${this.baseUrl}/users/${userRef}/miniboss/${operacion}/complete`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ exercises }),
                }
            );

            if (!response.ok) {
                throw new Error(`Failed to complete miniboss: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('[GamificationService] Error completing miniboss:', error);
            throw error;
        }
    }

    /**
     * Extract gamification rewards from session complete response
     */
    extractRewards(sessionResponse: any): GamificationRewards | null {
        if (!sessionResponse || !sessionResponse.gamification) {
            return null;
        }

        return sessionResponse.gamification;
    }

    /**
     * Check if user has unlocked an operation
     */
    hasUnlockedOperation(
        profile: GamificationProfile,
        operacion: 'suma' | 'resta' | 'mult' | 'div'
    ): boolean {
        const op = profile.operaciones.find((o) => o.operacion === operacion);
        return op ? op.unlocked : false;
    }

    /**
     * Get progress towards unlocking an operation
     */
    getUnlockProgress(
        profile: GamificationProfile,
        operacion: 'resta' | 'mult' | 'div'
    ) {
        return profile.progreso_desbloqueos[operacion];
    }

    /**
     * Check if miniboss is available for user
     */
    canAttemptMiniboss(
        profile: GamificationProfile,
        operacion: 'suma' | 'mult' | 'div'
    ): { canAttempt: boolean; reason?: string } {
        // SUMA: always available if unlocked
        if (operacion === 'suma') {
            return { canAttempt: this.hasUnlockedOperation(profile, 'suma') };
        }

        // MULT: requires RESTA unlocked
        if (operacion === 'mult') {
            if (!this.hasUnlockedOperation(profile, 'resta')) {
                return { canAttempt: false, reason: 'Requiere RESTA desbloqueada' };
            }
            return { canAttempt: true };
        }

        // DIV: requires MULT unlocked
        if (operacion === 'div') {
            if (!this.hasUnlockedOperation(profile, 'mult')) {
                return { canAttempt: false, reason: 'Requiere MULTIPLICACIÓN desbloqueada' };
            }
            return { canAttempt: true };
        }

        return { canAttempt: false, reason: 'Operación desconocida' };
    }

    /**
     * Format score for display
     */
    formatScore(score: number): string {
        return score.toFixed(1);
    }

    /**
     * Get user's rank from leaderboard
     */
    getUserRank(leaderboard: LeaderboardResponse, userRef: string): number | null {
        const entry = leaderboard.leaderboard.find((e) => e.user_ref === userRef);
        return entry ? entry.rank : null;
    }
}

// Export singleton instance
export const gamificationService = new GamificationService();
export default gamificationService;
