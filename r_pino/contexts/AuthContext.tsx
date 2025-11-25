import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { authService, AuthUser } from '../services/auth';
import { useRouter, useSegments } from 'expo-router';

interface AuthContextType {
    user: AuthUser | null;
    loading: boolean;
    login: (email: string, password: string) => Promise<void>;
    signup: (email: string, password: string, name: string) => Promise<void>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<AuthUser | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();
    const segments = useSegments();

    useEffect(() => {
        setUser(currentUser);
    } catch (error) {
        console.error('Failed to load user:', error);
    } finally {
        setLoading(false);
    }
};

const login = async (email: string, password: string) => {
    try {
        const authUser = await authService.login(email, password);
        setUser(authUser);
        // Navigation handled by useEffect
    } catch (error) {
        console.error('Login failed:', error);
        throw error;
    }
};

const signup = async (email: string, password: string, name: string) => {
    try {
        const authUser = await authService.signup(email, password, name);
        setUser(authUser);
        // Navigation handled by useEffect
    } catch (error) {
        console.error('Signup failed:', error);
        throw error;
    }
};

const logout = async () => {
    try {
        await authService.logout();
        setUser(null);
    } catch (error) {
        console.error('Logout failed:', error);
        throw error;
    }
};

return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
        {children}
    </AuthContext.Provider>
);
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
