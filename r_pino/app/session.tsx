import { View, Text, StyleSheet, TouchableOpacity, TextInput, ActivityIndicator, ScrollView } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { useState, useEffect } from 'react';
import { PineServerAPI } from '../services/api';
import { Exercise, ExerciseWithAnswer } from '../services/types';
import { StatusBar } from 'expo-status-bar';

export default function SessionScreen() {
    const router = useRouter();
    const { userRef } = useLocalSearchParams<{ userRef: string }>();

    const [loading, setLoading] = useState(true);
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
            const response = await PineServerAPI.startSession(userRef as string, 10);
            setSessionId(response.session_id);
            setExercises(response.exercises);
            setStartTime(Date.now());
        } catch (error) {
            console.error('Failed to start session:', error);
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
        }
    };

    if (loading) {
        return (
            <View style={styles.container}>
                <ActivityIndicator size="large" color="#007AFF" />
            </View>
        );
    }

    const exercise = exercises[currentIndex];
    const progress = ((currentIndex + 1) / exercises.length) * 100;

    return (
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
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#F5F5F7',
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
