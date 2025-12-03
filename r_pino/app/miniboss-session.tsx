import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    Alert,
    BackHandler,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import gamificationService from '../services/gamification/GamificationService';

export default function MinibossSessionScreen() {
    const router = useRouter();
    const { operacion } = useLocalSearchParams<{ operacion: string }>();

    const [exercises, setExercises] = useState<any[]>([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [timeRemaining, setTimeRemaining] = useState(0);
    const [timeLimit, setTimeLimit] = useState(0);
    const [sessionStartTime, setSessionStartTime] = useState<number>(0);
    const [loading, setLoading] = useState(true);
    const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
    const [results, setResults] = useState<any[]>([]);

    const timerRef = useRef<NodeJS.Timeout | null>(null);
    const userRef = 'current_user'; // TODO: Get from auth

    useEffect(() => {
        loadMinibossSession();

        // Prevent back navigation
        const backHandler = BackHandler.addEventListener('hardwareBackPress', () => {
            Alert.alert(
                'Abandonar Mini-jefe',
                '¿Estás seguro? Perderás todo el progreso.',
                [
                    { text: 'Cancelar', style: 'cancel' },
                    { text: 'Abandonar', style: 'destructive', onPress: () => router.back() },
                ]
            );
            return true;
        });

        return () => {
            if (timerRef.current) clearInterval(timerRef.current);
            backHandler.remove();
        };
    }, []);

    useEffect(() => {
        if (timeLimit > 0 && !loading) {
            startTimer();
        }
    }, [timeLimit, loading]);

    const loadMinibossSession = async () => {
        try {
            setLoading(true);
            const response = await gamificationService.startMiniboss(
                userRef,
                operacion as 'suma' | 'mult' | 'div'
            );

            setExercises(response.exercises);
            setTimeLimit(response.miniboss_info.tiempo_limite_segundos);
            setTimeRemaining(response.miniboss_info.tiempo_limite_segundos);
            setSessionStartTime(Date.now());
            setResults(new Array(response.exercises.length).fill(null));
        } catch (error) {
            console.error('Error loading miniboss:', error);
            Alert.alert('Error', 'No se pudo cargar el mini-jefe');
            router.back();
        } finally {
            setLoading(false);
        }
    };

    const startTimer = () => {
        if (timerRef.current) clearInterval(timerRef.current);

        timerRef.current = setInterval(() => {
            setTimeRemaining((prev) => {
                if (prev <= 1) {
                    // Time's up!
                    handleTimeUp();
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);
    };

    const handleTimeUp = () => {
        if (timerRef.current) clearInterval(timerRef.current);

        Alert.alert(
            '⏱️ Tiempo Agotado',
            'No completaste el mini-jefe a tiempo.',
            [{ text: 'Ver Resultados', onPress: finishSession }]
        );
    };

    const handleAnswerSelect = (answer: number) => {
        if (selectedAnswer !== null) return; // Ya respondió

        setSelectedAnswer(answer);

        const currentEx = exercises[currentIndex];
        const isCorrect = answer === currentEx.correct_answer;

        // Save result
        const newResults = [...results];
        newResults[currentIndex] = {
            ...currentEx,
            user_answer: answer,
            is_correct: isCorrect,
            fue_primer_intento: true, // Miniboss no permite reintentos
            time_taken_ms: 0, // Could track per-exercise time if needed
        };
        setResults(newResults);

        // Wait a moment to show feedback, then next
        setTimeout(() => {
            if (currentIndex < exercises.length - 1) {
                setCurrentIndex(currentIndex + 1);
                setSelectedAnswer(null);
            } else {
                // Last exercise - finish
                finishSession(newResults);
            }
        }, 800);
    };

    const finishSession = async (finalResults?: any[]) => {
        if (timerRef.current) clearInterval(timerRef.current);

        const resultsToSend = finalResults || results;
        const timeElapsed = (Date.now() - sessionStartTime) / 1000;

        try {
            const response = await gamificationService.completeMiniboss(
                userRef,
                operacion as 'suma' | 'mult' | 'div',
                resultsToSend
            );

            // Navigate to results with data
            router.replace({
                pathname: '/miniboss-result',
                params: {
                    operacion: operacion,
                    resultData: JSON.stringify(response),
                },
            });
        } catch (error) {
            console.error('Error completing miniboss:', error);
            Alert.alert('Error', 'No se pudo completar el mini-jefe');
        }
    };

    if (loading || exercises.length === 0) {
        return (
            <View style={styles.loadingContainer}>
                <Text style={styles.loadingText}>Preparando Mini-jefe...</Text>
            </View>
        );
    }

    const currentExercise = exercises[currentIndex];
    const progress = ((currentIndex + 1) / exercises.length) * 100;
    const timePercent = (timeRemaining / timeLimit) * 100;

    // Timer color based on remaining time
    const getTimerColor = () => {
        if (timePercent > 50) return '#4facfe';
        if (timePercent > 25) return '#FFA500';
        return '#FF3B30';
    };

    const getAnswerStyle = (option: number) => {
        if (selectedAnswer === null) return styles.optionButton;

        if (option === currentExercise.correct_answer) {
            return [styles.optionButton, styles.correctOption];
        }

        if (option === selectedAnswer && option !== currentExercise.correct_answer) {
            return [styles.optionButton, styles.incorrectOption];
        }

        return [styles.optionButton, styles.disabledOption];
    };

    return (
        <LinearGradient
            colors={['#1a1a2e', '#16213e', '#0f3460']}
            style={styles.container}
        >
            <StatusBar style="light" />

            {/* Timer Bar */}
            <View style={styles.timerContainer}>
                <View style={styles.timerBar}>
                    <View
                        style={[
                            styles.timerFill,
                            {
                                width: `${timePercent}%`,
                                backgroundColor: getTimerColor(),
                            }
                        ]}
                    />
                </View>
                <Text style={[styles.timerText, { color: getTimerColor() }]}>
                    ⏱️ {Math.floor(timeRemaining / 60)}:{(timeRemaining % 60).toString().padStart(2, '0')}
                </Text>
            </View>

            {/* Progress */}
            <View style={styles.progressContainer}>
                <Text style={styles.progressText}>
                    Pregunta {currentIndex + 1} de {exercises.length}
                </Text>
                <View style={styles.progressBar}>
                    <View style={[styles.progressFill, { width: `${progress}%` }]} />
                </View>
            </View>

            {/* Warning Banner */}
            <View style={styles.warningBanner}>
                <Text style={styles.warningText}>⚠️ NO HAY REINTENTOS</Text>
            </View>

            {/* Question */}
            <View style={styles.questionContainer}>
                <Text style={styles.questionText}>
                    {currentExercise.operand_1} {currentExercise.operator} {currentExercise.operand_2} = ?
                </Text>
            </View>

            {/* Options */}
            <View style={styles.optionsGrid}>
                {currentExercise.options.map((option: number, index: number) => (
                    <TouchableOpacity
                        key={index}
                        style={getAnswerStyle(option)}
                        onPress={() => handleAnswerSelect(option)}
                        disabled={selectedAnswer !== null}
                        activeOpacity={0.7}
                    >
                        <LinearGradient
                            colors={
                                selectedAnswer === null
                                    ? ['rgba(79, 172, 254, 0.3)', 'rgba(0, 242, 254, 0.3)']
                                    : option === currentExercise.correct_answer
                                        ? ['rgba(52, 199, 89, 0.5)', 'rgba(52, 199, 89, 0.3)']
                                        : option === selectedAnswer
                                            ? ['rgba(255, 59, 48, 0.5)', 'rgba(255, 59, 48, 0.3)']
                                            : ['rgba(136, 136, 136, 0.2)', 'rgba(136, 136, 136, 0.1)']
                            }
                            style={styles.optionGradient}
                        >
                            <Text style={styles.optionText}>{option}</Text>
                        </LinearGradient>
                    </TouchableOpacity>
                ))}
            </View>

            {/* Stats Footer */}
            <View style={styles.statsFooter}>
                <View style={styles.statItem}>
                    <Text style={styles.statValue}>
                        {results.filter(r => r?.is_correct).length}
                    </Text>
                    <Text style={styles.statLabel}>Correctas</Text>
                </View>
                <View style={styles.statItem}>
                    <Text style={[styles.statValue, { color: '#FF3B30' }]}>
                        {results.filter(r => r && !r.is_correct).length}
                    </Text>
                    <Text style={styles.statLabel}>Incorrectas</Text>
                </View>
            </View>
        </LinearGradient>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 20,
        paddingTop: 20,
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#1a1a2e',
    },
    loadingText: {
        fontSize: 18,
        color: '#FFFFFF',
    },
    timerContainer: {
        marginBottom: 20,
    },
    timerBar: {
        height: 8,
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: 4,
        overflow: 'hidden',
        marginBottom: 8,
    },
    timerFill: {
        height: '100%',
        borderRadius: 4,
    },
    timerText: {
        fontSize: 24,
        fontWeight: 'bold',
        textAlign: 'center',
    },
    progressContainer: {
        marginBottom: 20,
    },
    progressText: {
        fontSize: 16,
        color: '#FFFFFF',
        textAlign: 'center',
        marginBottom: 8,
    },
    progressBar: {
        height: 6,
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: 3,
        overflow: 'hidden',
    },
    progressFill: {
        height: '100%',
        backgroundColor: '#FFD700',
        borderRadius: 3,
    },
    warningBanner: {
        backgroundColor: 'rgba(255, 149, 0, 0.3)',
        borderRadius: 12,
        padding: 12,
        marginBottom: 20,
        borderWidth: 1,
        borderColor: 'rgba(255, 149, 0, 0.5)',
    },
    warningText: {
        fontSize: 14,
        fontWeight: 'bold',
        color: '#FFA500',
        textAlign: 'center',
    },
    questionContainer: {
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: 20,
        padding: 40,
        marginBottom: 30,
        alignItems: 'center',
    },
    questionText: {
        fontSize: 36,
        fontWeight: 'bold',
        color: '#FFFFFF',
    },
    optionsGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 12,
        marginBottom: 30,
    },
    optionButton: {
        width: '48%',
        aspectRatio: 2,
        borderRadius: 16,
        overflow: 'hidden',
    },
    correctOption: {
        borderWidth: 3,
        borderColor: '#34C759',
    },
    incorrectOption: {
        borderWidth: 3,
        borderColor: '#FF3B30',
    },
    disabledOption: {
        opacity: 0.5,
    },
    optionGradient: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    optionText: {
        fontSize: 32,
        fontWeight: 'bold',
        color: '#FFFFFF',
    },
    statsFooter: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        borderRadius: 12,
        padding: 16,
    },
    statItem: {
        alignItems: 'center',
    },
    statValue: {
        fontSize: 28,
        fontWeight: 'bold',
        color: '#34C759',
        marginBottom: 4,
    },
    statLabel: {
        fontSize: 12,
        color: 'rgba(255, 255, 255, 0.7)',
    },
});
