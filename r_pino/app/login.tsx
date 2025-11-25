import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Alert, Modal, FlatList, ScrollView } from 'react-native';
import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { LocalStorage } from '../services/storage';
import { AdaptiveContainer } from '../components/AdaptiveContainer';
import { useResponsive } from '../hooks/useResponsive';
import { useTranslation } from 'react-i18next';
import { PineServerAPI } from '../services/api';

interface Institution {
    _id: string;
    name: string;
}

export default function LoginScreen() {
    const { login, signup } = useAuth();
    const { isTabletOrDesktop } = useResponsive();
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
        loadSavedCredentials();
        fetchInstitutions();
    }, []);

    const fetchInstitutions = async () => {
        try {
            setLoadingInstitutions(true);
            const data = await PineServerAPI.getInstitutions();
            setInstitutions(data);

            // Auto-select if only one institution
            if (data.length === 1) {
                setSelectedInstitution(data[0]);
            }
        } catch (error) {
            console.error('Failed to fetch institutions:', error);
            Alert.alert(t('common.error'), 'Failed to load institutions. Please try again.');
        } finally {
            setLoadingInstitutions(false);
        }
    };

    const loadSavedCredentials = async () => {
        const savedEmail = await LocalStorage.retrieveData<string>('saved_email');
        const savedPassword = await LocalStorage.retrieveData<string>('saved_password');

        if (savedEmail && savedPassword) {
            setEmail(savedEmail);
            setPassword(savedPassword);
            setRememberMe(true);
        }
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
            // Check if error is institution mismatch
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
        <AdaptiveContainer centerOnDesktop={true} maxWidth={500}>
            <View style={styles.container}>
                <StatusBar style="auto" />

                <View style={[styles.content, isTabletOrDesktop && styles.contentWeb]}>
                    <Text style={styles.title}>{isLogin ? t('auth.welcomeBack') : t('auth.createAccount')}</Text>
                    <Text style={styles.subtitle}>
                        {isLogin ? t('auth.signInSubtitle') : t('auth.signUpSubtitle')}
                    </Text>

                    <View style={styles.form}>
                        {!isLogin && (
                            <View style={styles.inputContainer}>
                                <Ionicons name="person-outline" size={20} color="#666" style={styles.inputIcon} />
                                <TextInput
                                    style={styles.input}
                                    placeholder={t('auth.fullName')}
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
                            <Ionicons name="business-outline" size={20} color="#666" style={styles.inputIcon} />
                            <Text style={[styles.pickerText, !selectedInstitution && styles.placeholderText]}>
                                {loadingInstitutions
                                    ? t('common.loading')
                                    : selectedInstitution
                                        ? selectedInstitution.name
                                        : t('auth.selectInstitution')}
                            </Text>
                            <Ionicons name="chevron-down-outline" size={20} color="#666" />
                        </TouchableOpacity>

                        <View style={styles.inputContainer}>
                            <Ionicons name="mail-outline" size={20} color="#666" style={styles.inputIcon} />
                            <TextInput
                                style={styles.input}
                                placeholder={t('auth.email')}
                                value={email}
                                onChangeText={setEmail}
                                keyboardType="email-address"
                                autoCapitalize="none"
                            />
                        </View>

                        <View style={styles.inputContainer}>
                            <Ionicons name="lock-closed-outline" size={20} color="#666" style={styles.inputIcon} />
                            <TextInput
                                style={styles.input}
                                placeholder={t('auth.password')}
                                value={password}
                                onChangeText={setPassword}
                                secureTextEntry={!showPassword}
                            />
                            <TouchableOpacity onPress={() => setShowPassword(!showPassword)} style={styles.eyeIcon}>
                                <Ionicons name={showPassword ? "eye-off-outline" : "eye-outline"} size={20} color="#666" />
                            </TouchableOpacity>
                        </View>

                        {isLogin && (
                            <TouchableOpacity
                                style={styles.rememberContainer}
                                onPress={() => setRememberMe(!rememberMe)}
                            >
                                <View style={[styles.checkbox, rememberMe && styles.checkboxChecked]}>
                                    {rememberMe && <Ionicons name="checkmark" size={14} color="white" />}
                                </View>
                                <Text style={styles.rememberText}>{t('auth.rememberMe')}</Text>
                            </TouchableOpacity>
                        )}

                        <TouchableOpacity
                            style={[styles.button, loading && styles.buttonDisabled]}
                            onPress={handleSubmit}
                            disabled={loading}
                        >
                            {loading ? (
                                <ActivityIndicator color="white" />
                            ) : (
                                <Text style={styles.buttonText}>{isLogin ? t('auth.signIn') : t('auth.signUp')}</Text>
                            )}
                        </TouchableOpacity>

                        <TouchableOpacity onPress={() => setIsLogin(!isLogin)} style={styles.switchButton}>
                            <Text style={styles.switchText}>
                                {isLogin ? t('auth.dontHaveAccount') : t('auth.alreadyHaveAccount')}
                            </Text>
                        </TouchableOpacity>
                    </View>
                </View>

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
                            <Text style={styles.modalTitle}>{t('auth.institution')}</Text>
                            <FlatList
                                data={institutions}
                                keyExtractor={(item) => item._id}
                                renderItem={({ item }) => (
                                    <TouchableOpacity
                                        style={[
                                            styles.institutionItem,
                                            selectedInstitution?._id === item._id && styles.selectedInstitutionItem
                                        ]}
                                        onPress={() => {
                                            setSelectedInstitution(item);
                                            setShowInstitutionPicker(false);
                                        }}
                                    >
                                        <Text style={[
                                            styles.institutionText,
                                            selectedInstitution?._id === item._id && styles.selectedInstitutionText
                                        ]}>
                                            {item.name}
                                        </Text>
                                        {selectedInstitution?._id === item._id && (
                                            <Ionicons name="checkmark-circle" size={24} color="#007AFF" />
                                        )}
                                    </TouchableOpacity>
                                )}
                            />
                        </View>
                    </TouchableOpacity>
                </Modal>
            </View>
        </AdaptiveContainer>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#F5F5F7',
        justifyContent: 'center',
        padding: 20,
    },
    content: {
        backgroundColor: 'white',
        padding: 30,
        borderRadius: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 5,
    },
    contentWeb: {
        marginHorizontal: 'auto',
        marginVertical: 'auto',
    },
    title: {
        fontSize: 32,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 8,
        textAlign: 'center',
    },
    subtitle: {
        fontSize: 16,
        color: '#666',
        marginBottom: 32,
        textAlign: 'center',
    },
    form: {
        gap: 16,
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#F5F5F7',
        borderRadius: 12,
        borderWidth: 1,
        borderColor: '#E0E0E0',
        paddingHorizontal: 12,
    },
    inputIcon: {
        marginRight: 8,
    },
    input: {
        flex: 1,
        paddingVertical: 16,
        fontSize: 16,
    },
    eyeIcon: {
        padding: 8,
    },
    rememberContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginTop: 4,
    },
    checkbox: {
        width: 20,
        height: 20,
        borderRadius: 4,
        borderWidth: 2,
        borderColor: '#007AFF',
        marginRight: 8,
        alignItems: 'center',
        justifyContent: 'center',
    },
    checkboxChecked: {
        backgroundColor: '#007AFF',
    },
    rememberText: {
        color: '#666',
        fontSize: 14,
    },
    button: {
        backgroundColor: '#007AFF',
        padding: 16,
        borderRadius: 12,
        alignItems: 'center',
        marginTop: 8,
    },
    buttonDisabled: {
        opacity: 0.7,
    },
    buttonText: {
        color: 'white',
        fontSize: 16,
        fontWeight: 'bold',
    },
    switchButton: {
        alignItems: 'center',
        marginTop: 16,
    },
    switchText: {
        color: '#007AFF',
        fontSize: 14,
    },
    pickerText: {
        flex: 1,
        paddingVertical: 16,
        fontSize: 16,
        color: '#333',
    },
    placeholderText: {
        color: '#999',
    },
    modalOverlay: {
        flex: 1,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        justifyContent: 'center',
        alignItems: 'center',
    },
    modalContent: {
        backgroundColor: 'white',
        borderRadius: 16,
        padding: 20,
        width: '80%',
        maxHeight: '60%',
    },
    modalTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 16,
        textAlign: 'center',
    },
    institutionItem: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 16,
        borderBottomWidth: 1,
        borderBottomColor: '#E0E0E0',
    },
    selectedInstitutionItem: {
        backgroundColor: '#F0F8FF',
    },
    institutionText: {
        fontSize: 16,
        color: '#333',
    },
    selectedInstitutionText: {
        color: '#007AFF',
        fontWeight: '600',
    },
});
