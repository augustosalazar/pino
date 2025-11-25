// API Service for PineServer
import { Exercise, ExerciseWithAnswer, SessionResponse, StatsResponse } from './types';
import { config } from '../config';

export class PineServerAPI {

    /**
     * Get all available institutions
     */
    static async getInstitutions(): Promise<any[]> {
        const response = await fetch(`${config.api.baseUrl}/institutions`);

        if (!response.ok) {
            throw new Error(`Failed to fetch institutions: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Ensure user exists in database (create if doesn't exist)
     */
    static async ensureUser(userRef: string, email: string, username?: string, institutionRef?: string): Promise<any> {
        const response = await fetch(`${config.api.baseUrl}/users/ensure`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_ref: userRef,
                email: email,
                username: username,
                institution_ref: institutionRef,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Failed to ensure user: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Create user (alias for ensureUser)
     */
    static async createUser(userRef: string, email: string, username?: string, institutionRef?: string): Promise<any> {
        return this.ensureUser(userRef, email, username, institutionRef);
    }

    /**
     * Start a new exercise session
     */
    static async startSession(userRef: string, numExercises: number = 10): Promise<SessionResponse> {
        const response = await fetch(`${config.api.baseUrl}/sessions/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_ref: userRef,
                num_exercises: numExercises,
            }),
        });

        if (!response.ok) {
            throw new Error(`Failed to start session: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Complete a session with exercise results
     */
    static async completeSession(
        sessionId: string,
        exercises: ExerciseWithAnswer[]
    ): Promise<any> {
        const response = await fetch(`${config.api.baseUrl}/sessions/${sessionId}/complete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                exercises: exercises,
            }),
        });

        if (!response.ok) {
            throw new Error(`Failed to complete session: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Get user statistics
     */
    static async getUserStats(userRef: string): Promise<StatsResponse> {
        const response = await fetch(`${config.api.baseUrl}/users/${userRef}/stats`);

        if (!response.ok) {
            throw new Error(`Failed to get stats: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Get user difficulty profile
     */
    static async getUserProfile(userRef: string): Promise<any> {
        const response = await fetch(`${config.api.baseUrl}/users/${userRef}/profile`);

        if (!response.ok) {
            throw new Error(`Failed to get profile: ${response.statusText}`);
        }

        return await response.json();
    }
}
