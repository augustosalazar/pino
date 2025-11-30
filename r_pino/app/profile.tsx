import { View, Text, StyleSheet, TextInput, TouchableOpacity, Alert, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { PineServerAPI } from '../services/api';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';

export default function ProfileScreen() {
    const router = useRouter();
    const { user } = useAuth();
    const { theme } = useTheme();
    const [age, setAge] = useState(user?.age?.toString() || '');
    const [grade, setGrade] = useState(user?.grade || '');
    const [loading, setLoading] = useState(false);

    const handleSave = async () => {
        if (!user) return;

        setLoading(true);
        try {
            await PineServerAPI.updateProfile(
                user.id,
                age ? parseInt(age) : undefined,
                grade || undefined
            );
            Alert.alert('Success', 'Profile updated successfully!');
            router.back();
        } catch (error: any) {
            Alert.alert('Error', error.message || 'Failed to update profile');
        } finally {
            setLoading(false);
        }
    };

    return (
        <View style={[styles.container, { backgroundColor: theme.background }]}>
            <StatusBar style={theme.statusBarStyle} />

            <ScrollView contentContainerStyle={styles.content}>
                <View style={styles.header}>
                    <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
                        <Ionicons name="arrow-back" size={24} color={theme.primary} />
                    </TouchableOpacity>
                    <Text style={[styles.title, { color: theme.text }]}>Edit Profile</Text>
                    <View style={{ width: 24 }} />
                </View>

                <View style={[styles.card, { backgroundColor: theme.cardBackground }]}>
                    <View style={styles.userInfo}>
                        <Ionicons name="person-circle" size={80} color={theme.primary} />
                        <Text style={[styles.userName, { color: theme.text }]}>{user?.name}</Text>
                        <Text style={[styles.userEmail, { color: theme.textSecondary }]}>{user?.email}</Text>
                    </View>

                    <View style={styles.formSection}>
                        <Text style={[styles.sectionTitle, { color: theme.text }]}>Personal Information</Text>

                        <View style={styles.inputGroup}>
                            <Text style={[styles.label, { color: theme.textSecondary }]}>Age</Text>
                            <TextInput
                                style={[styles.input, { backgroundColor: theme.surfaceSecondary, borderColor: theme.border, color: theme.text }]}
                                value={age}
                                onChangeText={setAge}
                                keyboardType="numeric"
                                placeholder="Enter your age"
                                placeholderTextColor={theme.textTertiary}
                            />
                        </View>

                        <View style={styles.inputGroup}>
                            <Text style={[styles.label, { color: theme.textSecondary }]}>Grade/Year</Text>
                            <TextInput
                                style={[styles.input, { backgroundColor: theme.surfaceSecondary, borderColor: theme.border, color: theme.text }]}
                                value={grade}
                                onChangeText={setGrade}
                                placeholder="e.g., 9th Grade, Year 10"
                                placeholderTextColor={theme.textTertiary}
                            />
                        </View>
                    </View>

                    <TouchableOpacity
                        style={[styles.saveButton, { backgroundColor: theme.primary }, loading && styles.saveButtonDisabled]}
                        onPress={handleSave}
                        disabled={loading}
                    >
                        <Ionicons name="checkmark-circle" size={20} color="white" style={{ marginRight: 8 }} />
                        <Text style={styles.saveButtonText}>
                            {loading ? 'Saving...' : 'Save Changes'}
                        </Text>
                    </TouchableOpacity>
                </View>
            </ScrollView>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    content: {
        padding: 20,
        paddingTop: 20,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 24,
    },
    backButton: {
        padding: 8,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
    },
    card: {
        borderRadius: 16,
        padding: 24,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 3,
    },
    userInfo: {
        alignItems: 'center',
        marginBottom: 32,
        paddingBottom: 24,
        borderBottomWidth: 1,
        borderBottomColor: '#E0E0E0',
    },
    userName: {
        fontSize: 20,
        fontWeight: '600',
        marginTop: 12,
    },
    userEmail: {
        fontSize: 14,
        marginTop: 4,
    },
    formSection: {
        marginBottom: 24,
    },
    sectionTitle: {
        fontSize: 16,
        fontWeight: '600',
        marginBottom: 16,
    },
    inputGroup: {
        marginBottom: 20,
    },
    label: {
        fontSize: 14,
        fontWeight: '500',
        marginBottom: 8,
    },
    input: {
        borderRadius: 12,
        padding: 16,
        fontSize: 16,
        borderWidth: 1,
    },
    saveButton: {
        borderRadius: 12,
        padding: 18,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
    },
    saveButtonDisabled: {
        opacity: 0.6,
    },
    saveButtonText: {
        color: 'white',
        fontSize: 16,
        fontWeight: '600',
    },
});
