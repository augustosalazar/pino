import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    ActivityIndicator,
    Alert,
    Modal,
    FlatList,
    KeyboardAvoidingView,
    Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../contexts/AuthContext';
import { LocalStorage } from '../services/storage';
import { useTranslation } from 'react-i18next';
import { PineServerAPI } from '../services/api';

interface Institution {
    _id: string;
    name: string;
}

export default function LoginScreen() {
    const { login, signup } = useAuth();
    const { t } = useTranslation();

    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [rememberMe, setRememberMe] = useState(false);

    // Institution state
    const [institutions, setInstitutions] = useState<Institution[]>([]);
    const [selectedInstitution, setSelectedInstitution] = useState<Institution | null>(null);
    const [showInstitutionPicker, setShowInstitutionPicker] = useState(false);
    const [loadingInstitutions, setLoadingInstitutions] = useState(true);

    useEffect(() => {
        loadSavedData();
        fetchInstitutions();
    }, []);

    const fetchInstitutions = async () => {
        try {
            setLoadingInstitutions(true);
            const data = await PineServerAPI.getInstitutions();
            setInstitutions(data);

            const savedInstitutionId = await LocalStorage.retrieveData<string>('saved_institution_id');

            if (savedInstitutionId) {
                const savedInst = data.find((inst: Institution) => inst._id === savedInstitutionId);
                if (savedInst) {
                    setSelectedInstitution(savedInst);
                } else if (data.length > 0) {
                    setSelectedInstitution(data[0]);
                    await LocalStorage.storeData('saved_institution_id', data[0]._id);
                }
            } else if (data.length > 0) {
                setSelectedInstitution(data[0]);
                await LocalStorage.storeData('saved_institution_id', data[0]._id);
            }
        } catch (error) {
            console.error('Failed to fetch institutions:', error);
            Alert.alert(t('common.error'), 'Failed to load institutions. Please try again.');
        } finally {
            setLoadingInstitutions(false);
        }
    };

    const loadSavedData = async () => {
        const savedEmail = await LocalStorage.retrieveData<string>('saved_email');
        const savedPassword = await LocalStorage.retrieveData<string>('saved_password');

        if (savedEmail && savedPassword) {
            setEmail(savedEmail);
            setPassword(savedPassword);
            setRememberMe(true);
        }
    };

    const handleInstitutionSelect = async (institution: Institution) => {
        setSelectedInstitution(institution);
        setShowInstitutionPicker(false);
        await LocalStorage.storeData('saved_institution_id', institution._id);
    };

    const handleSubmit = async () => {
        if (!email || !password) {
            Alert.alert(t('common.error'), t('auth.fillAllFields'));
            return;
        }

        if (!selectedInstitution) {
            Alert.alert(t('common.error'), t('auth.institutionRequired'));
            return;
        }

        if (!isLogin && !name) {
            Alert.alert(t('common.error'), t('auth.enterName'));
            return;
        }

        setLoading(true);
        try {
            if (isLogin) {
                await login(email, password, selectedInstitution._id);

                if (rememberMe) {
                    await LocalStorage.storeData('saved_email', email);
                    await LocalStorage.storeData('saved_password', password);
                } else {
                    await LocalStorage.removeData('saved_email');
                    await LocalStorage.removeData('saved_password');
                }
            } else {
                await signup(email, password, name, selectedInstitution._id);
            }
        } catch (error: any) {
            if (error.message && error.message.includes('Institution mismatch')) {
                Alert.alert(t('common.error'), t('auth.institutionMismatch'));
            } else {
                Alert.alert(t('common.error'), error.message || t('auth.authFailed'));
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <LinearGradient colors={['#1a1a2e', '#16213e', '#0f3460']} style={styles.container}>
            <StatusBar style="light" />

            <KeyboardAvoidingView
                behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                style={styles.keyboardView}
            >
                <View style={styles.content}>
                    {/* Logo/Title */}
                    <View style={styles.logoContainer}>
                        <Ionicons name="calculator" size={64} color="#FFD700" />
                        <Text style={styles.appName}>Pino Math</Text>
                        <Text style={styles.appTagline}>Sistema de Gamificación</Text>
                    </View>

                    {/* Form Card */}
                    <View style={styles.formCard}>
                        <Text style={styles.title}>
                            {isLogin ? '👋 Bienvenido de vuelta' : '🎮 Crear Cuenta'}
                        </Text>
                        <Text style={styles.subtitle}>
                            {isLogin ? 'Ingresa para continuar jugando' : 'Únete y comienza a ganar'}
                        </Text>

                        {!isLogin && (
                            <View style={styles.inputContainer}>
                                <Ionicons name="person" size={20} color="#FFD700" style={styles.inputIcon} />
                                <TextInput
                                    style={styles.input}
                                    placeholder="Nombre completo"
                                    placeholderTextColor="rgba(255, 255, 255, 0.5)"
                                    value={name}
                                    onChangeText={setName}
                                    autoCapitalize="words"
                                />
                            </View>
                        )}

                        {/* Institution Picker */}
                        <TouchableOpacity
                            style={styles.inputContainer}
                            onPress={() => setShowInstitutionPicker(true)}
                            disabled={loadingInstitutions}
                        >
                            <Ionicons name="business" size={20} color="#FFD700" style={styles.inputIcon} />
                            <Text style={[styles.pickerText, !selectedInstitution && styles.placeholderText]}>
                                {loadingInstitutions
                                    ? 'Cargando...'
                                    : selectedInstitution
                                        ? selectedInstitution.name
                                        : 'Seleccionar institución'}
                            </Text>
                            <Ionicons name="chevron-down" size={20} color="rgba(255, 255, 255, 0.6)" />
                        </TouchableOpacity>

                        <View style={styles.inputContainer}>
                            <Ionicons name="mail" size={20} color="#FFD700" style={styles.inputIcon} />
                            <TextInput
                                style={styles.input}
                                placeholder="Email"
                                placeholderTextColor="rgba(255, 255, 255, 0.5)"
                                value={email}
                                onChangeText={setEmail}
                                keyboardType="email-address"
                                autoCapitalize="none"
                            />
                        </View>

                        <View style={styles.inputContainer}>
                            <Ionicons name="lock-closed" size={20} color="#FFD700" style={styles.inputIcon} />
                            <TextInput
                                style={styles.input}
                                placeholder="Contraseña"
                                placeholderTextColor="rgba(255, 255, 255, 0.5)"
                                value={password}
                                onChangeText={setPassword}
                                secureTextEntry={!showPassword}
                            />
                            <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                                <Ionicons
                                    name={showPassword ? "eye-off" : "eye"}
                                    size={20}
                                    color="rgba(255, 255, 255, 0.6)"
                                />
                            </TouchableOpacity>
                        </View>

                        {isLogin && (
                            <TouchableOpacity
                                style={styles.rememberContainer}
                                onPress={() => setRememberMe(!rememberMe)}
                            >
                                <View style={[styles.checkbox, rememberMe && styles.checkboxChecked]}>
                                    {rememberMe && <Ionicons name="checkmark" size={14} color="#FFFFFF" />}
                                </View>
                                <Text style={styles.rememberText}>Recordarme</Text>
                            </TouchableOpacity>
                        )}

                        {/* Submit Button */}
                        <TouchableOpacity
                            style={styles.submitButton}
                            onPress={handleSubmit}
                            disabled={loading}
                            activeOpacity={0.8}
                        >
                            <LinearGradient
                                colors={loading ? ['#666666', '#444444'] : ['#4facfe', '#00f2fe']}
                                style={styles.submitGradient}
                            >
                                {loading ? (
                                    <ActivityIndicator color="#FFFFFF" />
                                ) : (
                                    <>
                                        <Ionicons name={isLogin ? "log-in" : "person-add"} size={20} color="#FFFFFF" />
                                        <Text style={styles.submitText}>
                                            {isLogin ? 'Iniciar Sesión' : 'Crear Cuenta'}
                                        </Text>
                                    </>
                                )}
                            </LinearGradient>
                        </TouchableOpacity>

                        {/* Switch Mode */}
                        <TouchableOpacity onPress={() => setIsLogin(!isLogin)} style={styles.switchButton}>
                            <Text style={styles.switchText}>
                                {isLogin ? '¿No tienes cuenta? ' : '¿Ya tienes cuenta? '}
                                <Text style={styles.switchTextBold}>
                                    {isLogin ? 'Regístrate' : 'Inicia Sesión'}
                                </Text>
                            </Text>
                        </TouchableOpacity>
                    </View>
                </View>
            </KeyboardAvoidingView>

            {/* Institution Picker Modal */}
            <Modal
                visible={showInstitutionPicker}
                transparent={true}
                animationType="fade"
                onRequestClose={() => setShowInstitutionPicker(false)}
            >
                <TouchableOpacity
                    style={styles.modalOverlay}
                    activeOpacity={1}
                    onPress={() => setShowInstitutionPicker(false)}
                >
                    <View style={styles.modalContent} onStartShouldSetResponder={() => true}>
                        <Text style={styles.modalTitle}>🏢 Seleccionar Institución</Text>
                        <FlatList
                            data={institutions}
                            keyExtractor={(item) => item._id}
                            renderItem={({ item }) => (
                                <TouchableOpacity
                                    style={[
                                        styles.institutionItem,
                                        selectedInstitution?._id === item._id && styles.selectedInstitutionItem
                                    ]}
                                    onPress={() => handleInstitutionSelect(item)}
                                >
                                    <Text style={[
                                        styles.institutionText,
                                        selectedInstitution?._id === item._id && styles.selectedInstitutionText
                                    ]}>
                                        {item.name}
                                    </Text>
                                    {selectedInstitution?._id === item._id && (
                                        <Ionicons name="checkmark-circle" size={24} color="#4facfe" />
                                    )}
                                </TouchableOpacity>
                            )}
                        />
                    </View>
                </TouchableOpacity>
            </Modal>
        </LinearGradient>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    keyboardView: {
        flex: 1,
        justifyContent: 'center',
        padding: 20,
    },
    content: {
        alignItems: 'center',
    },
    logoContainer: {
        alignItems: 'center',
        marginBottom: 32,
    },
    appName: {
        fontSize: 32,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginTop: 12,
    },
    appTagline: {
        fontSize: 14,
        color: 'rgba(255, 255, 255, 0.7)',
        marginTop: 4,
    },
    formCard: {
        width: '100%',
        maxWidth: 400,
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: 24,
        padding: 24,
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.2)',
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginBottom: 8,
        textAlign: 'center',
    },
    subtitle: {
        fontSize: 14,
        color: 'rgba(255, 255, 255, 0.7)',
        marginBottom: 24,
        textAlign: 'center',
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: 12,
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.2)',
        paddingHorizontal: 16,
        marginBottom: 16,
    },
    inputIcon: {
        marginRight: 12,
    },
    input: {
        flex: 1,
        paddingVertical: 16,
        fontSize: 16,
        color: '#FFFFFF',
    },
    pickerText: {
        flex: 1,
        paddingVertical: 16,
        fontSize: 16,
        color: '#FFFFFF',
    },
    placeholderText: {
        color: 'rgba(255, 255, 255, 0.5)',
    },
    rememberContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 16,
    },
    checkbox: {
        width: 20,
        height: 20,
        borderRadius: 4,
        borderWidth: 2,
        borderColor: '#4facfe',
        marginRight: 8,
        alignItems: 'center',
        justifyContent: 'center',
    },
    checkboxChecked: {
        backgroundColor: '#4facfe',
    },
    rememberText: {
        color: 'rgba(255, 255, 255, 0.9)',
        fontSize: 14,
    },
    submitButton: {
        borderRadius: 12,
        overflow: 'hidden',
        marginBottom: 16,
        shadowColor: '#4facfe',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.5,
        shadowRadius: 8,
        elevation: 8,
    },
    submitGradient: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 16,
        gap: 8,
    },
    submitText: {
        color: '#FFFFFF',
        fontSize: 16,
        fontWeight: 'bold',
    },
    switchButton: {
        alignItems: 'center',
    },
    switchText: {
        color: 'rgba(255, 255, 255, 0.7)',
        fontSize: 14,
    },
    switchTextBold: {
        color: '#FFD700',
        fontWeight: 'bold',
    },
    modalOverlay: {
        flex: 1,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        justifyContent: 'center',
        alignItems: 'center',
    },
    modalContent: {
        backgroundColor: 'rgba(26, 26, 46, 0.95)',
        borderRadius: 16,
        padding: 20,
        width: '80%',
        maxHeight: '60%',
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.2)',
    },
    modalTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#FFFFFF',
        marginBottom: 16,
        textAlign: 'center',
    },
    institutionItem: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 16,
        borderBottomWidth: 1,
        borderBottomColor: 'rgba(255, 255, 255, 0.1)',
    },
    selectedInstitutionItem: {
        backgroundColor: 'rgba(79, 172, 254, 0.2)',
        borderRadius: 8,
        borderBottomWidth: 0,
    },
    institutionText: {
        fontSize: 16,
        color: '#FFFFFF',
    },
    selectedInstitutionText: {
        color: '#4facfe',
        fontWeight: '600',
    },
});
