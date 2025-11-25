import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

export default function ResultsScreen() {
    const router = useRouter();
    const { totalExercises, correctAnswers, scoreEarned, accuracy } = useLocalSearchParams<{
        totalExercises: string;
        correctAnswers: string;
        scoreEarned: string;
        accuracy: string;
    }>();

    const incorrectAnswers = parseInt(totalExercises) - parseInt(correctAnswers);
    const accuracyNum = parseFloat(accuracy);

    const getMessage = () => {
        if (accuracyNum >= 90) return { emoji: '🎉', text: 'Outstanding!', color: '#34C759' };
        if (accuracyNum >= 70) return { emoji: '👏', text: 'Great Job!', color: '#007AFF' };
        if (accuracyNum >= 50) return { emoji: '👍', text: 'Good Effort!', color: '#FF9500' };
        return { emoji: '💪', text: 'Keep Practicing!', color: '#FF3B30' };
    };

    const message = getMessage();

    return (
        <View style={styles.container}>
            <StatusBar style="auto" />

            <ScrollView contentContainerStyle={styles.content}>
                {/* Header */}
                <View style={styles.header}>
                    <Text style={styles.emoji}>{message.emoji}</Text>
                    <Text style={[styles.title, { color: message.color }]}>{message.text}</Text>
                </View>

                {/* Score Card */}
                <View style={styles.scoreCard}>
                    <Text style={styles.scoreLabel}>Score Earned</Text>
                    <Text style={styles.scoreValue}>+{scoreEarned}</Text>
                </View>

                {/* Stats Grid */}
                <View style={styles.statsGrid}>
                    <View style={styles.statCard}>
                        <Text style={styles.statValue}>{accuracy}%</Text>
                        <Text style={styles.statLabel}>Accuracy</Text>
                    </View>

                    <View style={styles.statCard}>
                        <Text style={[styles.statValue, { color: '#34C759' }]}>{correctAnswers}</Text>
                        <Text style={styles.statLabel}>Correct</Text>
                    </View>

                    <View style={styles.statCard}>
                        <Text style={[styles.statValue, { color: '#FF3B30' }]}>{incorrectAnswers}</Text>
                        <Text style={styles.statLabel}>Incorrect</Text>
                    </View>
                </View>

                {/* Feedback */}
                <View style={styles.feedbackCard}>
                    <Text style={styles.feedbackTitle}>Your Performance</Text>
                    <Text style={styles.feedbackText}>
                        {accuracyNum >= 90 && "Excellent work! Your difficulty will increase to keep challenging you."}
                        {accuracyNum >= 70 && accuracyNum < 90 && "You're doing great! Keep up the good work."}
                        {accuracyNum >= 50 && accuracyNum < 70 && "Good job! A bit more practice and you'll master these."}
                        {accuracyNum < 50 && "Don't give up! The difficulty will adjust to help you improve."}
                    </Text>
                </View>

                {/* Action Buttons */}
                <TouchableOpacity
                    style={styles.primaryButton}
                    onPress={() => router.replace('/')}
                >
                    <Text style={styles.primaryButtonText}>Back to Home</Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={styles.secondaryButton}
                    onPress={() => router.push('/stats')}
                >
                    <Text style={styles.secondaryButtonText}>View Statistics</Text>
                </TouchableOpacity>
            </ScrollView>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#F5F5F7',
    },
    content: {
        padding: 20,
        paddingTop: 60,
    },
    header: {
        alignItems: 'center',
        marginBottom: 32,
    },
    emoji: {
        fontSize: 80,
        marginBottom: 16,
    },
    title: {
        fontSize: 32,
        fontWeight: 'bold',
    },
    scoreCard: {
        backgroundColor: 'white',
        borderRadius: 16,
        padding: 32,
        alignItems: 'center',
        marginBottom: 24,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 3,
    },
    scoreLabel: {
        fontSize: 16,
        color: '#666',
        marginBottom: 8,
    },
    scoreValue: {
        fontSize: 48,
        fontWeight: 'bold',
        color: '#007AFF',
    },
    statsGrid: {
        flexDirection: 'row',
        gap: 12,
        marginBottom: 24,
    },
    statCard: {
        flex: 1,
        backgroundColor: 'white',
        borderRadius: 12,
        padding: 20,
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 2,
    },
    statValue: {
        fontSize: 28,
        fontWeight: 'bold',
        color: '#007AFF',
        marginBottom: 4,
    },
    statLabel: {
        fontSize: 12,
        color: '#999',
    },
    feedbackCard: {
        backgroundColor: 'white',
        borderRadius: 16,
        padding: 24,
        marginBottom: 32,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 3,
    },
    feedbackTitle: {
        fontSize: 18,
        fontWeight: '600',
        color: '#333',
        marginBottom: 12,
    },
    feedbackText: {
        fontSize: 16,
        color: '#666',
        lineHeight: 24,
    },
    primaryButton: {
        backgroundColor: '#007AFF',
        borderRadius: 12,
        padding: 18,
        alignItems: 'center',
        marginBottom: 12,
    },
    primaryButtonText: {
        color: 'white',
        fontSize: 18,
        fontWeight: '600',
    },
    secondaryButton: {
        backgroundColor: 'white',
        borderRadius: 12,
        padding: 18,
        alignItems: 'center',
        borderWidth: 2,
        borderColor: '#007AFF',
    },
    secondaryButtonText: {
        color: '#007AFF',
        fontSize: 18,
        fontWeight: '600',
    },
});
