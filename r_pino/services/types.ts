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
