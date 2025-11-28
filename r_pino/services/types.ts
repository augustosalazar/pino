// TypeScript types for R_PINE app

export enum Operator {
    ADD = '+',
    SUBTRACT = '-',
    MULTIPLY = '*',
    DIVIDE = '/',
}

export enum ExerciseType {
    MULTIPLE_CHOICE = 1,
    TEXT_INPUT = 2,
}

export interface Exercise {
    exercise_type: ExerciseType;
    operator: Operator;
    operand_1: number;
    operand_2: number;
    correct_answer: number;
    options?: number[];
    difficulty_level: number;
}

export interface ExerciseWithAnswer extends Exercise {
    user_answer: number;
    is_correct: boolean;
    time_taken_ms: number;
}

export interface SessionResponse {
    session_id: string;
    exercises: Exercise[];
    user_profile: Record<string, number>;
}

export interface CompleteSessionResponse {
    session_id: string;
    total_exercises: number;
    correct_answers: number;
    score_earned: number;
    difficulty_adjustments: Record<string, { old: number; new: number }>;
}

export interface StatsResponse {
    user_id: string;
    total_sessions: number;
    total_exercises: number;
    total_correct: number;
    accuracy: number;
    current_score: number;
    difficulty_by_operator: Record<string, number>;
}

export interface UserState {
    userRef: string;
    currentScore: number;
    stats?: StatsResponse;
}

// Analytics Types

export interface DifficultyChange {
    timestamp: string;
    operator: string;
    previous_difficulty: number;
    new_difficulty: number;
    reason: string;
    session_ref: string;
}

export interface OperatorAnalytics {
    operator: string;
    current_difficulty: number;
    difficulty_history: DifficultyChange[];
    total_attempts: number;
    total_correct: number;
    success_rate: number;
}

export interface SessionSummary {
    session_id: string;
    created_at: string;
    model_ref: string;
    total_exercises: number;
    correct_answers: number;
    score_earned: number;
    avg_difficulty: number;
    total_time_ms: number;
}

export interface UserAnalyticsResponse {
    user_ref: string;
    age?: number;
    grade?: string | number;
    institution_ref?: string;
    total_sessions: number;
    total_exercises: number;
    overall_accuracy: number;
    current_score: number;
    operator_analytics: Record<string, OperatorAnalytics>;
    sessions_summary: SessionSummary[];
}

export interface CohortStats {
    operator: string;
    avg_difficulty: number;
    min_difficulty: number;
    max_difficulty: number;
    stddev?: number;
    avg_success_rate: number;
}

export interface CohortAnalyticsResponse {
    cohort_description: string;
    user_count: number;
    age_group?: string;
    grade?: string | number;
    institution_ref?: string;
    model_ref?: string;
    difficulty_stats: Record<string, CohortStats>;
    overall_success_rate: number;
    avg_session_score: number;
    total_sessions: number;
}

export interface ModelPerformanceResponse {
    model_ref: string;
    total_users: number;
    total_sessions: number;
    total_exercises: number;
    avg_success_rate: number;
    difficulty_distribution: Record<string, { avg: number; min: number; max: number }>;
    sessions_over_time: Array<{ date: string; count: number }>;
}
