import React, { useState, useEffect, useCallback } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    ActivityIndicator,
    ScrollView,
    RefreshControl,
} from 'react-native';
import { useRouter, Redirect } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../contexts/AuthContext';
import gamificationService from '../services/gamification/GamificationService';
import { GamificationProfile } from '../services/gamification/types';
import { LevelBadge, StreakIndicator } from '../components/gamification';

export default function HomeScreen() {
    const router = useRouter();
    const { user, logout } = useAuth();

    const [profile, setProfile] = useState<GamificationProfile | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadProfile = useCallback(async () => {
        if (!user) return;

        try {
            setError(null);
            const profileData = await gamificationService.getProfile(user.id);
            setProfile(profileData);
        } catch (error) {
            console.error('Error loading profile:', error);
            setError('No se pudo cargar tu perfil');
        } finally {
            setLoading(false);
        }
    }, [user]);

    const onRefresh = useCallback(async () => {
        setRefreshing(true);
        await loadProfile();
        setRefreshing(false);
    }, [loadProfile]);

    useEffect(() => {
        if (user) {
            loadProfile();
        } else {
            setLoading(false);
        }
    }, [user, loadProfile]);

    const handleStartPractice = () => {
        if (!user) return;
        router.push({ pathname: '/session', params: { userRef: user.id } });
    };

    const handleLogout = async () => {
        await logout();
    };

    const getOperationIcon = (operacion: string) => {
        switch (operacion) {
            case 'suma': return '➕';
            case 'resta': return '➖';
            case 'mult': return '✖️';
            case 'div': return '➗';
            default: return '🔢';
        }
    };

    const getOperationName = (operacion: string) => {
        switch (operacion) {
            case 'suma': return 'Suma';
            case 'resta': return 'Resta';
            case 'mult': return 'Mult.';
            case 'div': return 'Div.';
            default: return operacion;
        }
    };

    const getOperationGradient = (operacion: string): [string, string] => {
        switch (operacion) {
            case 'suma': return ['rgba(67, 233, 123, 0.3)', 'rgba(56, 249, 215, 0.3)'];
            case 'resta': return ['rgba(250, 112, 154, 0.3)', 'rgba(254, 225, 64, 0.3)'];
            case 'mult': return ['rgba(79, 172, 254, 0.3)', 'rgba(0, 242, 254, 0.3)'];
            case 'div': return ['rgba(245, 93, 251, 0.3)', 'rgba(245, 87, 108, 0.3)'];
            default: return ['rgba(255, 255, 255, 0.1)', 'rgba(255, 255, 255, 0.1)'];
        }
    };

    // Redirect admin users
    if (!loading && user?.user_type === 2) {
        return <Redirect href="/(admin)/stats" />;
    }

    if (loading && !profile) {
        return (
            <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#FFD700" />
                <Text style={styles.loadingText}>Cargando...</Text>
            </View>
        );
    }

    if (error) {
        return (
            <View style={styles.loadingContainer}>
                <Text style={styles.errorText}>{error}</Text>
                <TouchableOpacity style={styles.retryButton} onPress={loadProfile}>
                    <Text style={styles.retryButtonText}>Reintentar</Text>
                </TouchableOpacity>
            </View>
        );
    }

    return (
        <LinearGradient colors={['#1a1a2e', '#16213e', '#0f3460']} style={styles.container}>
            <StatusBar style="light" />

            <ScrollView
                contentContainerStyle={styles.scrollContent}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#FFD700" />
                }
            >
                {/* Header */}
                <View style={styles.header}>
                    <View style={styles.headerTop}>
                        <View style={styles.userInfo}>
                            <Ionicons name="person-circle" size={40} color="#FFD700" />
                            <View style={styles.userText}>
                                <Text style={styles.greeting}>¡Hola!</Text>
                                <Text style={styles.username}>{user?.name?.split(' ')[0] || 'Usuario'}</Text>
                            </View>
                        </View>

                        <View style={styles.headerActions}>
                            <TouchableOpacity style={styles.iconButton} onPress={() => router.push('/settings')}>
                                <Ionicons name="settings-outline" size={24} color="#FFFFFF" />
                            </TouchableOpacity>
                            <TouchableOpacity style={styles.iconButton} onPress={handleLogout}>
                                <Ionicons name="log-out-outline" size={24} color="#FFFFFF" />
                            </TouchableOpacity>
                        </View>
                    </View>

                    {profile && (
                        <View style={styles.headerStats}>
                            <LevelBadge level={profile.perfil.nivel_jugador} size="large" showName={false} />
                            <View style={styles.levelInfo}>
                                <Text style={styles.levelText}>Nivel {profile.perfil.nivel_jugador}</Text>
                                <View style={styles.xpBar}>
                                    <View
                                        style={[
                                            styles.xpFill,
                                            {
                                                width: `${gamificationService.getLevelProgress(
                                                    profile.perfil.xp_total,
                                                    profile.perfil.nivel_jugador
                                                )}%`,
                                            },
                                        ]}
                                    />
                                </View>
                                <Text style={styles.xpText}>{profile.perfil.xp_total} XP</Text>
                            </View>
                        </View>
                    )}
                </View>

                {/* Quick Stats */}
                {profile && (
                    <View style={styles.quickStats}>
                        <View style={styles.statBox}>
                            <LinearGradient colors={['#43e97b', '#38f9d7']} style={styles.statGradient}>
                                <Text style={styles.statEmoji}>💎</Text>
                                <Text style={styles.statValue}>{profile.perfil.pp_total}</Text>
                                <Text style={styles.statLabel}>PP</Text>
                            </LinearGradient>
                        </View>

                        <View style={styles.statBox}>
                            <LinearGradient colors={['#fa709a', '#fee140']} style={styles.statGradient}>
                                <Text style={styles.statEmoji}>🏆</Text>
                                <Text style={styles.statValue}>{profile.perfil.pd_global}</Text>
                                <Text style={styles.statLabel}>PD</Text>
                            </LinearGradient>
                        </View>

                        <View style={styles.statBox}>
                            <LinearGradient colors={['#f093fb', '#f5576c']} style={styles.statGradient}>
                                <StreakIndicator streakDays={profile.perfil.racha_dias} compact={true} />
                            </LinearGradient>
                        </View>
                    </View>
                )}

                {/* Main Action Button */}
                <TouchableOpacity style={styles.playButton} onPress={handleStartPractice} activeOpacity={0.8}>
                    <LinearGradient colors={['#4facfe', '#00f2fe']} style={styles.playGradient}>
                        <Ionicons name="play-circle" size={32} color="#FFFFFF" />
                        <Text style={styles.playText}>PRACTICAR AHORA</Text>
                    </LinearGradient>
                </TouchableOpacity>

                {/* Operations Section */}
                {profile && (
                    <View style={styles.operationsSection}>
                        <Text style={styles.sectionTitle}>Tus Operaciones</Text>

                        <View style={styles.operationsGrid}>
                            {[...profile.operaciones]
                                .sort((a, b) => {
                                    const order = ['suma', 'resta', 'mult', 'div'];
                                    return order.indexOf(a.operacion) - order.indexOf(b.operacion);
                                })
                                .map((op) => (
                                    <View key={op.operacion} style={styles.operationCard}>
                                        <LinearGradient
                                            colors={getOperationGradient(op.operacion)}
                                            style={styles.operationGradient}
                                        >
                                            {!op.unlocked && (
                                                <View style={styles.lockedOverlay}>
                                                    <Ionicons name="lock-closed" size={20} color="rgba(255, 255, 255, 0.8)" />
                                                </View>
                                            )}
                                            <Text style={styles.operationIcon}>{getOperationIcon(op.operacion)}</Text>
                                            <Text style={styles.operationName}>{getOperationName(op.operacion)}</Text>
                                            <View style={styles.operationStats}>
                                                <Text style={styles.operationLevel}>Nv. {op.nivel_dominio}</Text>
                                                <Text style={styles.operationPD}>{op.pd_operacion} PD</Text>
                                            </View>
                                        </LinearGradient>
                                    </View>
                                ))}
                        </View>
                    </View>
                )}

                {/* Quick Access */}
                <View style={styles.quickAccess}>
                    <Text style={styles.sectionTitle}>Acceso Rápido</Text>

                    <View style={styles.accessGrid}>
                        <TouchableOpacity
                            style={styles.accessCard}
                            onPress={() => router.push('/gamification-profile')}
                            activeOpacity={0.7}
                        >
                            <LinearGradient colors={['rgba(79, 172, 254, 0.3)', 'rgba(0, 242, 254, 0.3)']} style={styles.accessGradient}>
                                <Text style={styles.accessIcon}>📊</Text>
                                <Text style={styles.accessText}>Perfil</Text>
                            </LinearGradient>
                        </TouchableOpacity>

                        <TouchableOpacity
                            style={styles.accessCard}
                            onPress={() => router.push('/miniboss')}
                            activeOpacity={0.7}
                        >
                            <LinearGradient colors={['rgba(245, 93, 251, 0.3)', 'rgba(245, 87, 108, 0.3)']} style={styles.accessGradient}>
                                <Text style={styles.accessIcon}>🐉</Text>
                                <Text style={styles.accessText}>Mini-jefes</Text>
                            </LinearGradient>
                        </TouchableOpacity>

                        <TouchableOpacity
                            style={styles.accessCard}
                            onPress={() => router.push('/leaderboard')}
                            activeOpacity={0.7}
                        >
                            <LinearGradient colors={['rgba(255, 215, 0, 0.3)', 'rgba(255, 165, 0, 0.3)']} style={styles.accessGradient}>
                                <Text style={styles.accessIcon}>🏆</Text>
                                <Text style={styles.accessText}>Ranking</Text>
                            </LinearGradient>
                        </TouchableOpacity>

                    </View>
                </View>

                {/* Institution Info */}
                {user?.institution_name && (
                    <View style={styles.institutionInfo}>
                        <Text style={styles.institutionText}>{user.institution_name}</Text>
                    </View>
                )}
            </ScrollView>
        </LinearGradient>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1 },
    scrollContent: { padding: 20, paddingTop: 60, paddingBottom: 40 },
    loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#1a1a2e' },
    loadingText: { marginTop: 12, fontSize: 16, color: '#FFFFFF' },
    errorText: { fontSize: 16, color: '#FF3B30', marginBottom: 20, textAlign: 'center' },
    retryButton: { backgroundColor: '#4facfe', paddingHorizontal: 24, paddingVertical: 12, borderRadius: 8 },
    retryButtonText: { color: '#FFFFFF', fontSize: 16, fontWeight: '600' },
    header: { marginBottom: 24 },
    headerTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
    userInfo: { flexDirection: 'row', alignItems: 'center' },
    userText: { marginLeft: 12 },
    greeting: { fontSize: 14, color: 'rgba(255, 255, 255, 0.7)' },
    username: { fontSize: 20, fontWeight: 'bold', color: '#FFFFFF' },
    headerActions: { flexDirection: 'row', gap: 12 },
    iconButton: { width: 40, height: 40, borderRadius: 20, backgroundColor: 'rgba(255, 255, 255, 0.1)', justifyContent: 'center', alignItems: 'center' },
    headerStats: { flexDirection: 'row', alignItems: 'center', backgroundColor: 'rgba(255, 255, 255, 0.1)', borderRadius: 16, padding: 16 },
    levelInfo: { flex: 1, marginLeft: 16 },
    levelText: { fontSize: 16, fontWeight: 'bold', color: '#FFD700', marginBottom: 8 },
    xpBar: { height: 8, backgroundColor: 'rgba(255, 255, 255, 0.2)', borderRadius: 4, overflow: 'hidden', marginBottom: 4 },
    xpFill: { height: '100%', backgroundColor: '#4facfe', borderRadius: 4 },
    xpText: { fontSize: 12, color: 'rgba(255, 255, 255, 0.7)' },
    quickStats: { flexDirection: 'row', gap: 12, marginBottom: 24 },
    statBox: { flex: 1, borderRadius: 12, overflow: 'hidden' },
    statGradient: { padding: 16, alignItems: 'center' },
    statEmoji: { fontSize: 24, marginBottom: 4 },
    statValue: { fontSize: 20, fontWeight: 'bold', color: '#FFFFFF', marginBottom: 2 },
    statLabel: { fontSize: 12, color: 'rgba(255, 255, 255, 0.8)' },
    playButton: { borderRadius: 16, overflow: 'hidden', marginBottom: 24, shadowColor: '#4facfe', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.5, shadowRadius: 8, elevation: 8 },
    playGradient: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 20, gap: 12 },
    playText: { fontSize: 20, fontWeight: 'bold', color: '#FFFFFF' },
    operationsSection: { marginBottom: 24 },
    sectionTitle: { fontSize: 20, fontWeight: 'bold', color: '#FFFFFF', marginBottom: 16 },
    operationsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
    operationCard: { width: '48%', borderRadius: 12, overflow: 'hidden' },
    operationGradient: { padding: 16, alignItems: 'center', borderWidth: 1, borderColor: 'rgba(255, 255, 255, 0.2)', position: 'relative' },
    lockedOverlay: { position: 'absolute', top: 8, right: 8, zIndex: 1 },
    operationIcon: { fontSize: 32, marginBottom: 8 },
    operationName: { fontSize: 14, fontWeight: '600', color: '#FFFFFF', marginBottom: 8 },
    operationStats: { flexDirection: 'row', gap: 8 },
    operationLevel: { fontSize: 12, color: 'rgba(255, 255, 255, 0.8)' },
    operationPD: { fontSize: 12, color: '#FFD700', fontWeight: '600' },
    quickAccess: { marginBottom: 24 },
    accessGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
    accessCard: { width: '48%', borderRadius: 12, overflow: 'hidden' },
    accessGradient: { padding: 20, alignItems: 'center', borderWidth: 1, borderColor: 'rgba(255, 255, 255, 0.2)' },
    accessIcon: { fontSize: 32, marginBottom: 8 },
    accessText: { fontSize: 14, fontWeight: '600', color: '#FFFFFF' },
    institutionInfo: { alignItems: 'center', paddingTop: 20, borderTopWidth: 1, borderTopColor: 'rgba(255, 255, 255, 0.1)' },
    institutionText: { fontSize: 13, color: 'rgba(255, 255, 255, 0.5)' },
});
