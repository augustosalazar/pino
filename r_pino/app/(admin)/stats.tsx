import { View, Text, StyleSheet, TouchableOpacity, ScrollView, TextInput, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { PineServerAPI } from '../../services/api';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';

interface InstitutionStats {
    total_students: number;
    average_score: number;
    total_score: number;
    total_sessions: number;
    total_exercises: number;
    total_correct: number;
    overall_accuracy: number;
    filter_options: {
        grades: string[];
        age_range: {
            min: number | null;
            max: number | null;
        };
    };
    is_uninorte: boolean;
}

export default function AdminStatsScreen() {
    const router = useRouter();
    const { user, logout } = useAuth();
    const [stats, setStats] = useState<InstitutionStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Filters
    const [ageMin, setAgeMin] = useState('');
    const [ageMax, setAgeMax] = useState('');
    const [selectedGrade, setSelectedGrade] = useState<string | undefined>(undefined);
    const [showFilters, setShowFilters] = useState(false);

    const loadStats = async () => {
        if (!user?.institution_ref) {
            setError('No institution assigned');
            setLoading(false);
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const filters = {
                age_min: ageMin ? parseInt(ageMin) : undefined,
                age_max: ageMax ? parseInt(ageMax) : undefined,
                grade: selectedGrade
            };

            const data = await PineServerAPI.getInstitutionStats(user.institution_ref, filters);
            setStats(data);
        } catch (err: any) {
            setError(err.message || 'Failed to load statistics');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadStats();
    }, []);

    const handleApplyFilters = () => {
        loadStats();
        setShowFilters(false);
    };

    const handleClearFilters = () => {
        setAgeMin('');
        setAgeMax('');
        setSelectedGrade(undefined);
        loadStats();
    };

    if (loading && !stats) {
        return (
            <View style={styles.centerContainer}>
                <ActivityIndicator size="large" color="#007AFF" />
                <Text style={styles.loadingText}>Loading statistics...</Text>
            </View>
        );
    }

    if (error && !stats) {
        return (
            <View style={styles.centerContainer}>
                <Ionicons name="alert-circle" size={48} color="#FF3B30" />
                <Text style={styles.errorText}>{error}</Text>
                <TouchableOpacity style={styles.retryButton} onPress={loadStats}>
                    <Text style={styles.retryButtonText}>Retry</Text>
                </TouchableOpacity>
            </View>
        );
    }

    return (
        <View style={styles.container}>

            <ScrollView contentContainerStyle={styles.content}>


                {/* Filter Section */}
                {showFilters && (
                    <View style={styles.filterCard}>
                        <Text style={styles.filterTitle}>Filters</Text>

                        <View style={styles.filterRow}>
                            <View style={styles.filterInput}>
                                <Text style={styles.filterLabel}>Min Age</Text>
                                <TextInput
                                    style={styles.input}
                                    value={ageMin}
                                    onChangeText={setAgeMin}
                                    keyboardType="numeric"
                                    placeholder="Min"
                                />
                            </View>

                            <View style={styles.filterInput}>
                                <Text style={styles.filterLabel}>Max Age</Text>
                                <TextInput
                                    style={styles.input}
                                    value={ageMax}
                                    onChangeText={setAgeMax}
                                    keyboardType="numeric"
                                    placeholder="Max"
                                />
                            </View>
                        </View>

                        {stats?.filter_options.grades && stats.filter_options.grades.length > 0 && (
                            <View style={styles.gradesContainer}>
                                <Text style={styles.filterLabel}>Grade</Text>
                                <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                                    <TouchableOpacity
                                        style={[styles.gradeChip, !selectedGrade && styles.gradeChipSelected]}
                                        onPress={() => setSelectedGrade(undefined)}
                                    >
                                        <Text style={[styles.gradeChipText, !selectedGrade && styles.gradeChipTextSelected]}>
                                            All
                                        </Text>
                                    </TouchableOpacity>
                                    {stats.filter_options.grades.map((grade) => (
                                        <TouchableOpacity
                                            key={grade}
                                            style={[styles.gradeChip, selectedGrade === grade && styles.gradeChipSelected]}
                                            onPress={() => setSelectedGrade(grade)}
                                        >
                                            <Text style={[styles.gradeChipText, selectedGrade === grade && styles.gradeChipTextSelected]}>
                                                {grade}
                                            </Text>
                                        </TouchableOpacity>
                                    ))}
                                </ScrollView>
                            </View>
                        )}

                        <View style={styles.filterActions}>
                            <TouchableOpacity style={styles.clearButton} onPress={handleClearFilters}>
                                <Text style={styles.clearButtonText}>Clear</Text>
                            </TouchableOpacity>
                            <TouchableOpacity style={styles.applyButton} onPress={handleApplyFilters}>
                                <Text style={styles.applyButtonText}>Apply Filters</Text>
                            </TouchableOpacity>
                        </View>
                    </View>
                )}

                {/* Stats Cards */}
                {stats && (
                    <>
                        <View style={styles.statsGrid}>
                            <View style={styles.statCard}>
                                <Ionicons name="people" size={32} color="#007AFF" />
                                <Text style={styles.statValue}>{stats.total_students}</Text>
                                <Text style={styles.statLabel}>Total Students</Text>
                            </View>

                            <View style={styles.statCard}>
                                <Ionicons name="trophy" size={32} color="#FF9500" />
                                <Text style={styles.statValue}>{stats.average_score.toFixed(1)}</Text>
                                <Text style={styles.statLabel}>Avg Score</Text>
                            </View>
                        </View>

                        <View style={styles.statsGrid}>
                            <View style={styles.statCard}>
                                <Ionicons name="time" size={32} color="#34C759" />
                                <Text style={styles.statValue}>{stats.total_sessions}</Text>
                                <Text style={styles.statLabel}>Total Sessions</Text>
                            </View>

                            <View style={styles.statCard}>
                                <Ionicons name="calculator" size={32} color="#AF52DE" />
                                <Text style={styles.statValue}>{stats.total_exercises}</Text>
                                <Text style={styles.statLabel}>Total Exercises</Text>
                            </View>
                        </View>

                        <View style={styles.accuracyCard}>
                            <View style={styles.accuracyHeader}>
                                <Ionicons name="checkmark-circle" size={40} color="#34C759" />
                                <View style={styles.accuracyTextContainer}>
                                    <Text style={styles.accuracyValue}>{stats.overall_accuracy.toFixed(1)}%</Text>
                                    <Text style={styles.accuracyLabel}>Overall Accuracy</Text>
                                </View>
                            </View>
                            <Text style={styles.accuracyDetail}>
                                {stats.total_correct} correct out of {stats.total_exercises} exercises
                            </Text>
                        </View>
                    </>
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
    centerContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20,
    },
    content: {
        padding: 20,
        paddingTop: 20,
    },
    header: {
        padding: 20,
        paddingTop: 60,
        backgroundColor: 'white',
        borderBottomWidth: 1,
        borderBottomColor: '#E5E5EA',
        marginBottom: 20,
        marginTop: -20,
        marginHorizontal: -20,
    },
    headerContent: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 12,
    },
    greetingSection: {
        flex: 1,
    },
    greeting: {
        fontSize: 20,
        fontWeight: '600',
        color: '#000',
    },
    institutionName: {
        fontSize: 14,
        color: '#8E8E93',
        marginTop: 2,
    },
    logoutButton: {
        padding: 8,
    },
    titleRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    pageTitle: {
        fontSize: 28,
        fontWeight: 'bold',
        color: '#000',
    },
    filterButton: {
        padding: 8,
    },
    backButton: {
        padding: 8,
    },
    headerTextContainer: {
        flex: 1,
        marginLeft: 12,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#333',
    },
    subtitle: {
        fontSize: 14,
        color: '#666',
        marginTop: 2,
    },
    loadingText: {
        marginTop: 12,
        fontSize: 16,
        color: '#666',
    },
    errorText: {
        marginTop: 12,
        fontSize: 16,
        color: '#FF3B30',
        textAlign: 'center',
    },
    retryButton: {
        marginTop: 16,
        backgroundColor: '#007AFF',
        paddingHorizontal: 24,
        paddingVertical: 12,
        borderRadius: 12,
    },
    retryButtonText: {
        color: 'white',
        fontSize: 16,
        fontWeight: '600',
    },
    filterCard: {
        backgroundColor: 'white',
        borderRadius: 16,
        padding: 20,
        marginBottom: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 3,
    },
    filterTitle: {
        fontSize: 18,
        fontWeight: '600',
        color: '#333',
        marginBottom: 16,
    },
    filterRow: {
        flexDirection: 'row',
        gap: 12,
        marginBottom: 16,
    },
    filterInput: {
        flex: 1,
    },
    filterLabel: {
        fontSize: 14,
        fontWeight: '500',
        color: '#666',
        marginBottom: 8,
    },
    input: {
        backgroundColor: '#F5F5F7',
        borderRadius: 12,
        padding: 12,
        fontSize: 14,
        color: '#333',
        borderWidth: 1,
        borderColor: '#E0E0E0',
    },
    gradesContainer: {
        marginBottom: 16,
    },
    gradeChip: {
        backgroundColor: '#F5F5F7',
        borderRadius: 20,
        paddingHorizontal: 16,
        paddingVertical: 8,
        marginRight: 8,
        borderWidth: 1,
        borderColor: '#E0E0E0',
    },
    gradeChipSelected: {
        backgroundColor: '#007AFF',
        borderColor: '#007AFF',
    },
    gradeChipText: {
        fontSize: 14,
        color: '#333',
        fontWeight: '500',
    },
    gradeChipTextSelected: {
        color: 'white',
    },
    filterActions: {
        flexDirection: 'row',
        gap: 12,
    },
    clearButton: {
        flex: 1,
        backgroundColor: '#F5F5F7',
        borderRadius: 12,
        padding: 14,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: '#E0E0E0',
    },
    clearButtonText: {
        color: '#666',
        fontSize: 16,
        fontWeight: '600',
    },
    applyButton: {
        flex: 1,
        backgroundColor: '#007AFF',
        borderRadius: 12,
        padding: 14,
        alignItems: 'center',
    },
    applyButtonText: {
        color: 'white',
        fontSize: 16,
        fontWeight: '600',
    },
    statsGrid: {
        flexDirection: 'row',
        gap: 12,
        marginBottom: 12,
    },
    statCard: {
        flex: 1,
        backgroundColor: 'white',
        borderRadius: 16,
        padding: 20,
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 3,
    },
    statValue: {
        fontSize: 32,
        fontWeight: 'bold',
        color: '#333',
        marginTop: 8,
    },
    statLabel: {
        fontSize: 12,
        color: '#666',
        marginTop: 4,
        textAlign: 'center',
    },
    accuracyCard: {
        backgroundColor: 'white',
        borderRadius: 16,
        padding: 24,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 3,
    },
    accuracyHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 12,
    },
    accuracyTextContainer: {
        marginLeft: 16,
    },
    accuracyValue: {
        fontSize: 36,
        fontWeight: 'bold',
        color: '#34C759',
    },
    accuracyLabel: {
        fontSize: 14,
        color: '#666',
        marginTop: 4,
    },
    accuracyDetail: {
        fontSize: 14,
        color: '#999',
        textAlign: 'center',
    },
});
