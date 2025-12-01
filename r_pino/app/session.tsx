import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    TextInput,
    ActivityIndicator,
    ScrollView,
    Alert,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { PineServerAPI } from '../services/api';
import { Exercise, ExerciseWithAnswer } from '../services/types';

export default function SessionScreen() {
    const router = useRouter();
    const { userRef } = useLocalSearchParams<{ userRef: string }>();

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [sessionId, setSessionId] = useState<string>('');
    const [exercises, setExercises] = useState<Exercise[]>([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [userAnswers, setUserAnswers] = useState<ExerciseWithAnswer[]>([]);
    const [textAnswer, setTextAnswer] = useState('');
    const [startTime, setStartTime] = useState(Date.now());
    const [selectedOption, setSelectedOption] = useState<number | null>(null);

    useEffect(() => {
        startSession();
    }, []);

    const startSession = async () => {
        try {
            setLoading(true);
            setError(null);
            console.log('[SessionScreen] Starting session for user:', userRef);

            const response = await PineServerAPI.startSession(userRef as string, 10);

            console.log('[SessionScreen] Session response:', response);

            if (!response || !response.exercises || response.exercises.length === 0) {
                throw new Error('No exercises received from server');
            }

            setSessionId(response.session_id);
            setExercises(response.exercises);
            setStartTime(Date.now());

            console.log('[SessionScreen] Session started successfully with', response.exercises.length, 'exercises');
        } catch (error: any) {
            console.error('[SessionScreen] Failed to start session:', error);
            const errorMessage = error.message || 'Failed to start session. Please try again.';
            setError(errorMessage);
            Alert.alert('Error', errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const handleMultipleChoiceAnswer = (answer: number) => {
        setSelectedOption(answer);

        // Small delay to show selection before proceeding
        setTimeout(() => {
            const exercise = exercises[currentIndex];
            const timeTaken = Date.now() - startTime;
            const isCorrect = answer === exercise.correct_answer;

            const exerciseWithAnswer: ExerciseWithAnswer = {
                ...exercise,
                user_answer: answer,
                is_correct: isCorrect,
                time_taken_ms: timeTaken,
            };

            const newAnswers = [...userAnswers, exerciseWithAnswer];
            setUserAnswers(newAnswers);
            setSelectedOption(null);

            if (currentIndex < exercises.length - 1) {
                setCurrentIndex(currentIndex + 1);
                setStartTime(Date.now());
            } else {
                completeSession(newAnswers);
            }
        }, 300);
    };

    const handleTextInputSubmit = () => {
        const answer = parseInt(textAnswer);
        if (isNaN(answer)) return;

        const exercise = exercises[currentIndex];
        const timeTaken = Date.now() - startTime;
        const isCorrect = answer === exercise.correct_answer;

        const exerciseWithAnswer: ExerciseWithAnswer = {
            ...exercise,
            user_answer: answer,
            is_correct: isCorrect,
            time_taken_ms: timeTaken,
        };

        const newAnswers = [...userAnswers, exerciseWithAnswer];
        setUserAnswers(newAnswers);
        setTextAnswer('');

        if (currentIndex < exercises.length - 1) {
            setCurrentIndex(currentIndex + 1);
            setStartTime(Date.now());
        } else {
            completeSession(newAnswers);
        }
    };

    const completeSession = async (answers: ExerciseWithAnswer[]) => {
        try {
            const result = await PineServerAPI.completeSession(sessionId, answers);
            router.replace({
                pathname: '/results',
                params: {
                    sessionId: sessionId,
                    totalExercises: result.total_exercises.toString(),
                    correctAnswers: result.correct_answers.toString(),
                    scoreEarned: result.score_earned.toString(),
                    accuracy: ((result.correct_answers / result.total_exercises) * 100).toFixed(1),
                },
            });
        } catch (error) {
            console.error('Failed to complete session:', error);
            Alert.alert('Error', 'Failed to complete session. Please try again.');
        }
    };

    if (loading) {
        return (
            <LinearGradient colors={['#1a1a2e', '#16213e', '#0f3460']} style={styles.centerContainer}>
                <StatusBar style="light" />
                <ActivityIndicator size="large" color="#FFD700" />
                <Text style={styles.loadingText}>Cargando ejercicios...</Text>
            </LinearGradient>
        );
    }

    if (error || !exercises || exercises.length === 0) {
        return (
            <LinearGradient colors={['#1a1a2e', '#16213e', '#0f3460']} style={styles.centerContainer}>
                <StatusBar style="light" />
                <Ionicons name="alert-circle" size={64} color="#FF3B30" />
                <Text style={styles.errorTitle}>¡Oops!</Text>
                <Text style={styles.errorText}>{error || 'No se pudieron cargar los ejercicios'}</Text>
                <TouchableOpacity style={styles.retryButton} onPress={startSession} activeOpacity={0.8}>
                    <LinearGradient colors={['#4facfe', '#00f2fe']} style={styles.retryGradient}>
                        <Ionicons name="refresh" size={20} color="#FFFFFF" />
                        <Text style={styles.retryButtonText}>Reintentar</Text>
                    </LinearGradient>
                </TouchableOpacity>
                <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
                    <Text style={styles.backButtonText}>Volver</Text>
                </TouchableOpacity>
            </LinearGradient>
        );
    }

    const exercise = exercises[currentIndex];

    if (!exercise) {
        return (
            <LinearGradient colors={['#1a1a2e', '#16213e', '#0f3460']} style={styles.centerContainer}>
                <StatusBar style="light" />
                <Text style={styles.errorText}>Datos de ejercicio inválidos</Text>
                <TouchableOpacity style={styles.retryButton} onPress={startSession}>
                    <Text style={styles.retryButtonText}>Reintentar</Text>
                </TouchableOpacity>
            </LinearGradient>
        );
    }

    const progress = ((currentIndex + 1) / exercises.length) * 100;

    return (
        <LinearGradient colors={['#1a1a2e', '#16213e', '#0f3460']} style={styles.container}>
            <StatusBar style="light" />

            {/* Progress Bar */}
            <View style={styles.progressContainer}>
                <View style={styles.progressBar}>
                    <LinearGradient
                        colors={['#4facfe', '#00f2fe']}
                        style={[styles.progressFill, { width: `${progress}%` }]}
                        start={{ x: 0, y: 0 }}
                        end={{ x: 1, y: 0 }}
                    />
                </View>
                <Text style={styles.progressText}>
                    Ejercicio {currentIndex + 1} de {exercises.length}
                </Text>
            </View>

            <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
                {/* Exercise Card */}
                <View style={styles.exerciseCard}>
                    <LinearGradient
                        colors={['rgba(255, 255, 255, 0.1)', 'rgba(255, 255, 255, 0.05)']}
                        style={styles.exerciseGradient}
                    >
                        <Text style={styles.exerciseLabel}>Resuelve:</Text>
                        <View style={styles.expressionContainer}>
                            <Text style={styles.exerciseText}>
                                {exercise.operand_1} {exercise.operator} {exercise.operand_2} =
                            </Text>
                            <View style={styles.questionMark}>
                                <Text style={styles.questionText}>?</Text>
                            </View>
                        </View>
                        <View style={styles.difficultyBadge}>
                            <Ionicons name="star" size={14} color="#FFD700" />
                            <Text style={styles.difficultyText}>Nivel {exercise.difficulty_level.toFixed(1)}</Text>
                        </View>
                    </LinearGradient>
                </View>

                {/* Answer Options */}
                {exercise.exercise_type === 1 && exercise.options ? (
                    <View style={styles.optionsContainer}>
                        {exercise.options.map((option, index) => {
                            const isSelected = selectedOption === option;
                            return (
                                <TouchableOpacity
                                    key={index}
                                    style={styles.optionButton}
                                    onPress={() => handleMultipleChoiceAnswer(option)}
                                    activeOpacity={0.7}
                                >
                                    <LinearGradient
                                        colors={
                                            isSelected
                                                ? ['#4facfe', '#00f2fe']
                                                : ['rgba(255, 255, 255, 0.1)', 'rgba(255, 255, 255, 0.05)']
                                        }
                                        style={styles.optionGradient}
                                    >
                                        <Text style={[styles.optionText, isSelected && styles.optionTextSelected]}>
                                            {option}
                                        </Text>
                                    </LinearGradient>
                                </TouchableOpacity>
                            );
                        })}
                    </View>
                ) : (
                    <View style={styles.textInputContainer}>
                        <View style={styles.inputWrapper}>
                            <TextInput
                                style={styles.textInput}
                                value={textAnswer}
                                onChangeText={setTextAnswer}
                                keyboardType="numeric"
                                placeholder="Tu respuesta"
                                placeholderTextColor="rgba(255, 255, 255, 0.4)"
                                autoFocus
                            />
                        </View>
                        <TouchableOpacity
                            style={styles.submitButton}
                            onPress={handleTextInputSubmit}
                            disabled={!textAnswer}
                            activeOpacity={0.8}
                        >
                            <LinearGradient
                                colors={textAnswer ? ['#4facfe', '#00f2fe'] : ['#666666', '#444444']}
                                style={styles.submitGradient}
                            >
                                <Ionicons name="checkmark-circle" size={24} color="#FFFFFF" />
                                <Text style={styles.submitButtonText}>Enviar</Text>
                            </LinearGradient>
                        </TouchableOpacity>
                    </View>
                )}
            </ScrollView>
        </LinearGradient>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    centerContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20,
    },
    loadingText: {
        marginTop: 16,
        fontSize: 16,
        color: '#FFFFFF',
    },
    errorTitle: {
        fontSize: 28,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginTop: 16,
        marginBottom: 8,
    },
    errorText: {
        fontSize: 16,
        color: 'rgba(255, 255, 255, 0.8)',
        textAlign: 'center',
        marginBottom: 24,
        paddingHorizontal: 20,
    },
    retryButton: {
        borderRadius: 12,
        overflow: 'hidden',
        marginBottom: 12,
    },
    retryGradient: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 14,
        paddingHorizontal: 28,
        gap: 8,
    },
    retryButtonText: {
        color: '#FFFFFF',
        fontSize: 16,
        fontWeight: '600',
    },
    backButton: {
        paddingVertical: 12,
        paddingHorizontal: 24,
    },
    backButtonText: {
        color: '#FFD700',
        fontSize: 16,
        fontWeight: '600',
    },
    progressContainer: {
        padding: 20,
        paddingTop: 60,
    },
    progressBar: {
        height: 10,
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: 5,
        overflow: 'hidden',
        marginBottom: 12,
    },
    progressFill: {
        height: '100%',
        borderRadius: 5,
    },
    progressText: {
        textAlign: 'center',
        color: '#FFFFFF',
        fontSize: 14,
        fontWeight: '600',
    },
    content: {
        flex: 1,
    },
    contentContainer: {
        padding: 20,
        paddingTop: 0,
    },
    exerciseCard: {
        borderRadius: 20,
        overflow: 'hidden',
        marginBottom: 32,
    },
    exerciseGradient: {
        padding: 32,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.2)',
    },
    exerciseLabel: {
        fontSize: 16,
        color: 'rgba(255, 255, 255, 0.7)',
        marginBottom: 20,
        textTransform: 'uppercase',
        letterSpacing: 1,
    },
    expressionContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 12,
        marginBottom: 20,
    },
    exerciseText: {
        fontSize: 42,
        fontWeight: 'bold',
        color: '#FFFFFF',
    },
    questionMark: {
        width: 50,
        height: 50,
        borderRadius: 25,
        backgroundColor: '#FFD700',
        justifyContent: 'center',
        alignItems: 'center',
    },
    questionText: {
        fontSize: 32,
        fontWeight: 'bold',
        color: '#1a1a2e',
    },
    difficultyBadge: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 6,
        backgroundColor: 'rgba(255, 215, 0, 0.2)',
        paddingHorizontal: 16,
        paddingVertical: 6,
        borderRadius: 16,
    },
    difficultyText: {
        fontSize: 13,
        color: '#FFD700',
        fontWeight: '600',
    },
    optionsContainer: {
        gap: 14,
    },
    optionButton: {
        borderRadius: 16,
        overflow: 'hidden',
    },
    optionGradient: {
        padding: 20,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.2)',
    },
    optionText: {
        fontSize: 30,
        fontWeight: 'bold',
        color: '#FFFFFF',
    },
    optionTextSelected: {
        color: '#FFFFFF',
    },
    textInputContainer: {
        gap: 16,
    },
    inputWrapper: {
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: 16,
        borderWidth: 2,
        borderColor: '#4facfe',
        overflow: 'hidden',
    },
    textInput: {
        padding: 24,
        fontSize: 32,
        textAlign: 'center',
        color: '#FFFFFF',
        fontWeight: 'bold',
    },
    submitButton: {
        borderRadius: 16,
        overflow: 'hidden',
    },
    submitGradient: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 18,
        gap: 8,
    },
    submitButtonText: {
        color: '#FFFFFF',
        fontSize: 18,
        fontWeight: 'bold',
    },
});
