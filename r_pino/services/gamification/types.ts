// Gamification TypeScript Types

export interface GamificationProfile {
    perfil: UserProfile;
    operaciones: Operation[];
    modos_disponibles: AvailableModes;
    operaciones_disponibles: string[];
    progreso_desbloqueos: UnlockProgress;
}

export interface UserProfile {
    _id: string;
    user_ref: string;
    pp_total: number;
    pp_dia: number;
    pp_semana: number;
    pd_global: number;
    pd_semana: number;
    xp_total: number;
    nivel_jugador: number;
    racha_dias: number;
    unlocked_mix_suma_resta: boolean;
    unlocked_mix_mult_div: boolean;
    unlocked_speed: boolean;
    unlocked_bosses: boolean;
    unlocked_elite: boolean;
    unlocked_master: boolean;
}

export interface Operation {
    _id: string;
    user_ref: string;
    operacion: 'suma' | 'resta' | 'mult' | 'div';
    pd_operacion: number;
    nivel_dominio: number;
    unlocked: boolean;
    miniboss_completed: boolean;
    miniboss_attempts: number;
    ejercicios_totales: number;
    ejercicios_correctos: number;
}

export interface AvailableModes {
    mix_suma_resta: boolean;
    mix_mult_div: boolean;
    speed: boolean;
    bosses: boolean;
    elite: boolean;
    master: boolean;
}

export interface UnlockProgress {
    resta?: UnlockRequirements;
    mult?: UnlockRequirements;
    div?: UnlockRequirements;
}

export interface UnlockRequirements {
    desbloqueada: boolean;
    requisitos?: {
        pd_global?: Requirement;
        pd_suma?: Requirement;
        pd_resta?: Requirement;
        pd_mult?: Requirement;
        minijefe_suma?: { completado: boolean };
        minijefe_mult?: { completado: boolean };
        minijefe_div?: { completado: boolean };
    };
}

export interface Requirement {
    actual: number;
    requerido: number;
    cumplido: boolean;
}

export interface GamificationRewards {
    resumen: {
        total_items: number;
        correctos: number;
        porcentaje_acierto: number;
        dificultad_media: number;
    };
    recompensas: {
        pp_ganados: number;
        pd: {
            por_items: number;
            bonus_batch: number;
            bonus_racha: number;
            bonus_levelup: number;
            total_pd_global: number;
        };
        xp_ganada: number;
    };
    progreso: {
        nivel_jugador: number;
        hubo_levelup: boolean;
        nivel_dominio: number;
        pd_global: number;
        pd_operacion: number;
        xp_total: number;
        racha_dias: number;
    };
    items_pendientes: {
        total: number;
        nuevos: number;
        mensaje: string;
    };
    desbloqueos: {
        operaciones: { [key: string]: boolean };
        modos: { [key: string]: boolean };
        hubo_desbloqueos: boolean;
    };
}

export interface MinibossInfo {
    operacion: string;
    nombre: string;
    descripcion: string;
    num_ejercicios: number;
    tiempo_limite_segundos: number;
    acierto_minimo_porcentaje: number;
    permite_reintentos: boolean;
    desbloquea: string | null;
    condiciones: any;
}

export interface MinibossResult {
    operacion: string;
    exito: boolean;
    detalles: {
        nombre: string;
        exito: boolean;
        correctos: number;
        total: number;
        porcentaje_acierto: number;
        acierto_requerido: number;
        cumple_acierto: boolean;
        tiempo_segundos: number;
        tiempo_limite: number;
        cumple_tiempo: boolean;
        cumple_reintentos: boolean;
        desbloquea: string | null;
    };
    desbloqueo: {
        hubo_desbloqueo: boolean;
        operaciones_desbloqueadas?: string[];
    } | null;
    total_exercises: number;
    correct_answers: number;
    tiempo_total_segundos: number;
}

export interface LeaderboardEntry {
    rank: number;
    user_ref: string;
    username: string;
    email: string;
    pp_semana: number;
    pd_semana: number;
    score_semanal: number;
    nivel_jugador: number;
    racha_dias: number;
    institution_ref?: string;
}

export interface LeaderboardResponse {
    leaderboard: LeaderboardEntry[];
    total_users: number;
    top_count: number;
    institution_ref: string | null;
}

// Helper types
export type OperationType = 'suma' | 'resta' | 'mult' | 'div';

export const OPERATION_NAMES: Record<OperationType, string> = {
    suma: 'Suma',
    resta: 'Resta',
    mult: 'Multiplicación',
    div: 'División',
};

export const OPERATION_ICONS: Record<OperationType, string> = {
    suma: '+',
    resta: '-',
    mult: '×',
    div: '÷',
};

export const OPERATION_COLORS: Record<OperationType, string> = {
    suma: '#43e97b',
    resta: '#fa709a',
    mult: '#4facfe',
    div: '#fee140',
};

// Level names
export const LEVEL_NAMES: Record<number, string> = {
    0: 'Bloqueado',
    1: 'Básico',
    2: 'Intermedio',
    3: 'Avanzado',
    4: 'Experto',
    5: 'Maestro',
};

// Level colors (Clash Royale style)
export const LEVEL_COLORS: Record<number, string> = {
    0: '#888888',
    1: '#8B4513', // Bronze
    2: '#C0C0C0', // Silver
    3: '#FFD700', // Gold
    4: '#9370DB', // Purple
    5: '#00CED1', // Turquoise
};

// PD ranges for levels
export const PD_RANGES: { min: number; max: number }[] = [
    { min: 0, max: 0 },      // Level 0 (locked)
    { min: 0, max: 19 },     // Level 1
    { min: 20, max: 49 },    // Level 2
    { min: 50, max: 89 },    // Level 3
    { min: 90, max: 139 },   // Level 4
    { min: 140, max: 999 },  // Level 5
];

// Calculate level from PD
export function calculateLevelFromPD(pd: number): number {
    for (let i = PD_RANGES.length - 1; i >= 0; i--) {
        if (pd >= PD_RANGES[i].min) {
            return i;
        }
    }
    return 0;
}

// Calculate progress within level
export function calculateLevelProgress(pd: number, level: number): number {
    if (level === 0 || level === 5) return 0;

    const range = PD_RANGES[level];
    const total = range.max - range.min + 1;
    const current = pd - range.min;

    return Math.min(100, Math.max(0, (current / total) * 100));
}

// Calculate XP required for level
export function calculateXPRequired(level: number): number {
    return Math.floor(50 * Math.pow(level, 1.5));
}

// Calculate XP progress to next level
export function calculateXPProgress(xp: number, currentLevel: number): number {
    const currentReq = calculateXPRequired(currentLevel);
    const nextReq = calculateXPRequired(currentLevel + 1);
    const total = nextReq - currentReq;
    const current = xp - currentReq;

    return Math.min(100, Math.max(0, (current / total) * 100));
}
