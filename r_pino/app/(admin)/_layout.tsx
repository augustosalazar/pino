import { createMaterialTopTabNavigator } from '@react-navigation/material-top-tabs';
import { withLayoutContext } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useAuth } from '../../contexts/AuthContext';
import { useRouter } from 'expo-router';

const { Navigator } = createMaterialTopTabNavigator();

// Create a custom Expo Router layout using MaterialTopTabs
export const MaterialTopTabs = withLayoutContext(Navigator);

export default function AdminLayout() {
    const { user, logout } = useAuth();
    const router = useRouter();

    const handleLogout = async () => {
        await logout();
        router.replace('/auth');
    };

    return (
        <View style={styles.container}>
            {/* Admin Header */}
            <View style={styles.header}>
                <View style={styles.greetingSection}>
                    <Text style={styles.greeting}>Hi, {user?.name?.split(' ')[0] || 'Admin'}! 👋</Text>
                    <Text style={styles.institutionName}>{user?.institution_name || 'Institution'}</Text>
                </View>
                <TouchableOpacity onPress={handleLogout} style={styles.logoutButton}>
                    <Ionicons name="log-out-outline" size={24} color="#FF3B30" />
                </TouchableOpacity>
            </View>

            {/* Top Tabs */}
            <MaterialTopTabs
                screenOptions={{
                    tabBarActiveTintColor: '#007AFF',
                    tabBarInactiveTintColor: '#8E8E93',
                    tabBarLabelStyle: {
                        textTransform: 'none',
                        fontWeight: '600',
                        fontSize: 14
                    },
                    tabBarIndicatorStyle: {
                        backgroundColor: '#007AFF',
                        height: 3
                    },
                    tabBarStyle: {
                        backgroundColor: 'white',
                        elevation: 0,
                        shadowOpacity: 0,
                        borderBottomWidth: 1,
                        borderBottomColor: '#E5E5EA',
                    },
                }}
            >
                <MaterialTopTabs.Screen
                    name="stats"
                    options={{
                        title: 'Statistics',
                    }}
                />
                <MaterialTopTabs.Screen
                    name="users"
                    options={{
                        title: 'User Progress',
                    }}
                />
            </MaterialTopTabs>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#F5F5F7',
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 20,
        paddingTop: 60,
        backgroundColor: 'white',
        borderBottomWidth: 1,
        borderBottomColor: '#E5E5EA',
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
});
