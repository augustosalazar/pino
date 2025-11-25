// API Service for PineServer
import { Exercise, ExerciseWithAnswer, SessionResponse, StatsResponse } from './types';

// Configure based on your testing environment:
// - iOS Simulator / Web: http://localhost:8000/api
// - Android Emulator: http://10.0.2.2:8000/api
// - Physical Device: http://YOUR_COMPUTER_IP:8000/api
const API_BASE_URL = 'http://localhost:8000/api';

export class PineServerAPI {

    /**
     * Ensure user exists in database (create if doesn't exist)
     */
    static async ensureUser(userRef: string, email: string, username?: string): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/users/ensure`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_ref: userRef,
                email: email,
                username: username,
            }),
        });

        if (!response.ok) {
            throw new Error(`Failed to ensure user: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Create user (alias for ensureUser)
     */
    static async createUser(userRef: string, email: string, username?: string): Promise<any> {
        return this.ensureUser(userRef, email, username);
    }

    /**
     * Start a new exercise session
     */
    static async startSession(userRef: string, numExercises: number = 10): Promise<SessionResponse> {
        const response = await fetch(`${API_BASE_URL}/sessions/start`, {
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
        const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/complete`, {
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
        const response = await fetch(`${API_BASE_URL}/users/${userRef}/stats`);

        if (!response.ok) {
            throw new Error(`Failed to get stats: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Get user difficulty profile
     */
    static async getUserProfile(userRef: string): Promise<any> {
        const response = await fetch(`${API_BASE_URL}/users/${userRef}/profile`);

        if (!response.ok) {
            throw new Error(`Failed to get profile: ${response.statusText}`);
        }

        return await response.json();
    }
}
