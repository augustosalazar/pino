import React, { useState, useEffect, useCallback } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    ActivityIndicator,
    RefreshControl,
    Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { MinibossCard } from '../components/gamification';
import gamificationService from '../services/gamification/GamificationService';
import { MinibossInfo, GamificationProfile } from '../services/gamification/types';

export default function MinibossScreen() {
    const router = useRouter();
    const [minibosses, setMinibosses] = useState<MinibossInfo[]>([]);
    const [profile, setProfile] = useState<GamificationProfile | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    // TODO: Get from auth context
    const userRef = 'current_user';

    const loadData = useCallback(async () => {
        try {
            setLoading(true);

            // Load minibosses info
            const minibossData = await gamificationService.getMinibosses();
            setMinibosses(minibossData.minibosses);

            // Load user profile to check availability
            const profileData = await gamificationService.getProfile(userRef);
            setProfile(profileData);
        } catch (error) {
            console.error('Error loading miniboss data:', error);
            Alert.alert('Error', 'No se pudieron cargar los mini-jefes');
        } finally {
            setLoading(false);
        }
    }, [userRef]);

    const onRefresh = useCallback(async () => {
        setRefreshing(true);
        await loadData();
        setRefreshing(false);
    }, [loadData]);

    useEffect(() => {
        loadData();
    }, [loadData]);

    const handleMinibossPress = (miniboss: MinibossInfo) => {
        // Check if can attempt
        const { canAttempt, reason } = gamificationService.canAttemptMiniboss(
            profile!,
            miniboss.operacion as 'suma' | 'mult' | 'div'
        );

        if (!canAttempt) {
            Alert.alert('No Disponible', reason || 'No puedes intentar este mini-jefe aún');
            return;
        }

        // Navigate to session
        router.push({
            pathname: '/miniboss-session',
            params: { operacion: miniboss.operacion },
        });
    };

    const getCompletionStatus = (operacion: string) => {
        if (!profile) return false;
        const op = profile.operaciones.find((o) => o.operacion === operacion);
        return op?.miniboss_completed || false;
    };

    if (loading && !profile) {
        return (
            <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#FFD700" />
                <Text style={styles.loadingText}>Cargando Mini-jefes...</Text>
            </View>
        );
    }

    return (
        <LinearGradient
            colors={['#1a1a2e', '#16213e', '#0f3460']}
            style={styles.container}
        >
            <StatusBar style="light" />

            <ScrollView
                style={styles.scrollView}
                contentContainerStyle={styles.scrollContent}
                refreshControl={
                    <RefreshControl
                        refreshing={refreshing}
                        onRefresh={onRefresh}
                        tintColor="#FFD700"
                    />
                }
            >
                {/* Header */}
                <View style={styles.header}>
                    <Text style={styles.title}>⚔️ MINI-JEFES</Text>
                    <Text style={styles.subtitle}>
                        Desafíos especiales que desbloquean nuevas operaciones
                    </Text>
                </View>

                {/* Info Card */}
                <View style={styles.infoCard}>
                    <Text style={styles.infoTitle}>📋 Reglas Importantes</Text>
                    <View style={styles.infoContent}>
                        <Text style={styles.infoItem}>• Cada mini-jefe tiene tiempo límite</Text>
                        <Text style={styles.infoItem}>• No puedes usar reintentos en los ejercicios</Text>
                        <Text style={styles.infoItem}>• Debes cumplir el % de acierto mínimo</Text>
                        <Text style={styles.infoItem}>• Al completarlos, desbloqueas nuevas operaciones</Text>
                    </View>
                </View>

                {/* Miniboss List */}
                <View style={styles.listSection}>
                    {profile && minibosses.map((miniboss) => {
                        const { canAttempt, reason } = gamificationService.canAttemptMiniboss(
                            profile,
                            miniboss.operacion as 'suma' | 'mult' | 'div'
                        );
                        const completed = getCompletionStatus(miniboss.operacion);

                        return (
                            <MinibossCard
                                key={miniboss.operacion}
                                miniboss={miniboss}
                                canAttempt={canAttempt}
                                reason={reason}
                                completed={completed}
                                onPress={() => handleMinibossPress(miniboss)}
                            />
                        );
                    })}
                </View>

                {/* Progress Summary */}
                {profile && (
                    <View style={styles.progressCard}>
                        <Text style={styles.progressTitle}>Tu Progreso</Text>
                        <View style={styles.progressStats}>
                            <View style={styles.progressStat}>
                                <Text style={styles.progressValue}>
                                    {profile.operaciones.filter((o) => o.miniboss_completed).length}
                                </Text>
                                <Text style={styles.progressLabel}>Completados</Text>
                            </View>
                            <View style={styles.progressStat}>
                                <Text style={styles.progressValue}>
                                    {profile.operaciones.filter((o) => o.unlocked).length}
                                </Text>
                                <Text style={styles.progressLabel}>Operaciones Desbloqueadas</Text>
                            </View>
                        </View>
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
    scrollView: {
        flex: 1,
    },
    scrollContent: {
        padding: 20,
        paddingTop: 20,
        paddingBottom: 40,
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#1a1a2e',
    },
    loadingText: {
        marginTop: 12,
        fontSize: 16,
        color: '#FFFFFF',
    },
    header: {
        alignItems: 'center',
        marginBottom: 24,
    },
    title: {
        fontSize: 32,
        fontWeight: 'bold',
        color: '#FFD700',
        marginBottom: 8,
        textShadowColor: 'rgba(0, 0, 0, 0.5)',
        textShadowOffset: { width: 0, height: 2 },
        textShadowRadius: 4,
    },
    subtitle: {
        fontSize: 16,
        color: 'rgba(255, 255, 255, 0.8)',
        textAlign: 'center',
        paddingHorizontal: 20,
    },
    infoCard: {
        backgroundColor: 'rgba(79, 172, 254, 0.2)',
        borderRadius: 16,
        padding: 16,
        marginBottom: 24,
        borderWidth: 1,
        borderColor: 'rgba(79, 172, 254, 0.4)',
    },
    infoTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#4facfe',
        marginBottom: 12,
    },
    infoContent: {
        gap: 8,
    },
    infoItem: {
        fontSize: 14,
        color: 'rgba(255, 255, 255, 0.9)',
        lineHeight: 20,
    },
    listSection: {
        marginBottom: 24,
    },
    progressCard: {
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: 16,
        padding: 20,
    },
    progressTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginBottom: 16,
        textAlign: 'center',
    },
    progressStats: {
        flexDirection: 'row',
        justifyContent: 'space-around',
    },
    progressStat: {
        alignItems: 'center',
    },
    progressValue: {
        fontSize: 32,
        fontWeight: 'bold',
        color: '#FFD700',
        marginBottom: 4,
    },
    progressLabel: {
        fontSize: 13,
        color: 'rgba(255, 255, 255, 0.8)',
        textAlign: 'center',
    },
});
