import { View, Text, StyleSheet, TouchableOpacity, TextInput, ActivityIndicator, ScrollView, Alert } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { useState, useEffect } from 'react';
import { PineServerAPI } from '../services/api';
import { Exercise, ExerciseWithAnswer } from '../services/types';
import { StatusBar } from 'expo-status-bar';
import { AdaptiveContainer } from '../components/AdaptiveContainer';
import { useResponsive } from '../hooks/useResponsive';
import { Ionicons } from '@expo/vector-icons';

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
        const exercise = exercises[currentIndex];
        const timeTaken = Date.now() - startTime;
        const isCorrect = answer === exercise.correct_answer;

        const exerciseWithAnswer: ExerciseWithAnswer = {
            ...exercise,
            user_answer: answer,
            is_correct: isCorrect,
            time_taken_ms: timeTaken
        };

        const newAnswers = [...userAnswers, exerciseWithAnswer];
        setUserAnswers(newAnswers);

        if (currentIndex < exercises.length - 1) {
            setCurrentIndex(currentIndex + 1);
            setStartTime(Date.now());
        } else {
            completeSession(newAnswers);
        }
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
            time_taken_ms: timeTaken
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
                }
            });
        } catch (error) {
            console.error('Failed to complete session:', error);
            Alert.alert('Error', 'Failed to complete session. Please try again.');
        }
    };

    if (loading) {
        return (
            <View style={styles.centerContainer}>
                <ActivityIndicator size="large" color="#007AFF" />
                <Text style={styles.loadingText}>Loading exercises...</Text>
            </View>
        );
    }

    if (error || !exercises || exercises.length === 0) {
        return (
            <View style={styles.centerContainer}>
                <Ionicons name="alert-circle-outline" size={64} color="#FF3B30" />
                <Text style={styles.errorTitle}>Oops!</Text>
                <Text style={styles.errorText}>
                    {error || 'Failed to load exercises'}
                </Text>
                <TouchableOpacity style={styles.retryButton} onPress={startSession}>
                    <Ionicons name="refresh-outline" size={20} color="white" />
                    <Text style={styles.retryButtonText}>Retry</Text>
                </TouchableOpacity>
                <TouchableOpacity
                    style={styles.backButton}
                    onPress={() => router.back()}
                >
                    <Text style={styles.backButtonText}>Go Back</Text>
                </TouchableOpacity>
            </View>
        );
    }

    const exercise = exercises[currentIndex];

    // Safety check
    if (!exercise) {
        return (
            <View style={styles.centerContainer}>
                <Text style={styles.errorText}>Exercise data is invalid</Text>
                <TouchableOpacity style={styles.retryButton} onPress={startSession}>
                    <Text style={styles.retryButtonText}>Retry</Text>
                </TouchableOpacity>
            </View>
        );
    }

    const progress = ((currentIndex + 1) / exercises.length) * 100;

    return (
        <AdaptiveContainer centerOnDesktop={true} maxWidth={700}>
            <View style={styles.container}>
                <StatusBar style="auto" />

                {/* Progress Bar */}
                <View style={styles.progressContainer}>
                    <View style={styles.progressBar}>
                        <View style={[styles.progressFill, { width: `${progress}%` }]} />
                    </View>
                    <Text style={styles.progressText}>
                        {currentIndex + 1} / {exercises.length}
                    </Text>
                </View>

                <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
                    {/* Exercise */}
                    <View style={styles.exerciseCard}>
                        <Text style={styles.exerciseLabel}>Solve this:</Text>
                        <Text style={styles.exerciseText}>
                            {exercise.operand_1} {exercise.operator} {exercise.operand_2} = ?
                        </Text>
                        <Text style={styles.difficultyLabel}>Difficulty: {exercise.difficulty_level.toFixed(1)}</Text>
                    </View>

                    {/* Answer Options */}
                    {exercise.exercise_type === 1 && exercise.options ? (
                        <View style={styles.optionsContainer}>
                            {exercise.options.map((option, index) => (
                                <TouchableOpacity
                                    key={index}
                                    style={styles.optionButton}
                                    onPress={() => handleMultipleChoiceAnswer(option)}
                                >
                                    <Text style={styles.optionText}>{option}</Text>
                                </TouchableOpacity>
                            ))}
                        </View>
                    ) : (
                        <View style={styles.textInputContainer}>
                            <TextInput
                                style={styles.textInput}
                                value={textAnswer}
                                onChangeText={setTextAnswer}
                                keyboardType="numeric"
                                placeholder="Enter your answer"
                                autoFocus
                            />
                            <TouchableOpacity
                                style={[styles.submitButton, !textAnswer && styles.submitButtonDisabled]}
                                onPress={handleTextInputSubmit}
                                disabled={!textAnswer}
                            >
                                <Text style={styles.submitButtonText}>Submit</Text>
                            </TouchableOpacity>
                        </View>
                    )}
                </ScrollView>
            </View>
        </AdaptiveContainer>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#F5F5F7',
    },
    centerContainer: {
        flex: 1,
        backgroundColor: '#F5F5F7',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20,
    },
    loadingText: {
        marginTop: 16,
        fontSize: 16,
        color: '#666',
    },
    errorTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#333',
        marginTop: 16,
        marginBottom: 8,
    },
    errorText: {
        fontSize: 16,
        color: '#666',
        textAlign: 'center',
        marginBottom: 24,
        paddingHorizontal: 20,
    },
    retryButton: {
        flexDirection: 'row',
        backgroundColor: '#007AFF',
        paddingVertical: 12,
        paddingHorizontal: 24,
        borderRadius: 12,
        alignItems: 'center',
        gap: 8,
        marginBottom: 12,
    },
    retryButtonText: {
        color: 'white',
        fontSize: 16,
        fontWeight: '600',
    },
    backButton: {
        paddingVertical: 12,
        paddingHorizontal: 24,
    },
    backButtonText: {
        color: '#007AFF',
        fontSize: 16,
    },
    progressContainer: {
        padding: 20,
        paddingTop: 60,
    },
    progressBar: {
        height: 8,
        backgroundColor: '#E0E0E0',
        borderRadius: 4,
        overflow: 'hidden',
        marginBottom: 8,
    },
    progressFill: {
        height: '100%',
        backgroundColor: '#007AFF',
    },
    progressText: {
        textAlign: 'center',
        color: '#666',
        fontSize: 14,
    },
    content: {
        flex: 1,
    },
    contentContainer: {
        padding: 20,
    },
    exerciseCard: {
        backgroundColor: 'white',
        borderRadius: 16,
        padding: 32,
        marginBottom: 24,
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 3,
    },
    exerciseLabel: {
        fontSize: 16,
        color: '#666',
        marginBottom: 16,
    },
    exerciseText: {
        fontSize: 36,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 16,
    },
    difficultyLabel: {
        fontSize: 14,
        color: '#999',
    },
    optionsContainer: {
        gap: 12,
    },
    optionButton: {
        backgroundColor: 'white',
        borderRadius: 12,
        padding: 20,
        borderWidth: 2,
        borderColor: '#007AFF',
        alignItems: 'center',
    },
    optionText: {
        fontSize: 24,
        fontWeight: '600',
        color: '#007AFF',
    },
    textInputContainer: {
        gap: 12,
    },
    textInput: {
        backgroundColor: 'white',
        borderRadius: 12,
        padding: 20,
        fontSize: 24,
        textAlign: 'center',
        borderWidth: 2,
        borderColor: '#007AFF',
    },
    submitButton: {
        backgroundColor: '#007AFF',
        borderRadius: 12,
        padding: 20,
        alignItems: 'center',
    },
    submitButtonDisabled: {
        opacity: 0.5,
    },
    submitButtonText: {
        color: 'white',
        fontSize: 18,
        fontWeight: '600',
    },
});
