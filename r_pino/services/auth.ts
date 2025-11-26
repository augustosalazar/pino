import { LocalStorage } from './storage';
import { PineServerAPI } from './api';
import { config } from '../config';

export interface AuthUser {
    id: string;
    email: string;
    name: string;
    accessToken: string;
    refreshToken: string;
    user_type?: number;  // 1 = student, 2 = admin
    age?: number;
    grade?: string;
    institution_ref?: string;
    institution_name?: string;
}

export class AuthService {
    private baseUrl: string;

    constructor() {
        this.baseUrl = `${config.roble.baseUrl}/auth/${config.roble.projectId}`;
    }

    async login(email: string, password: string, institutionRef?: string): Promise<AuthUser> {
        try {
            const response = await fetch(`${this.baseUrl}/login`, {
                method: 'POST',
                headers: { "Content-Type": "application/json; charset=UTF-8" },
                body: JSON.stringify({ email, password }),
            });
            console.log('Auth login', email, password, this.baseUrl);

            if (response.status === 201) {
                const data = await response.json();
                const accessToken = data.accessToken;
                const refreshToken = data.refreshToken;
                const userId = data.user.id;

                await LocalStorage.storeData('token', accessToken);
                await LocalStorage.storeData('refreshToken', refreshToken);
                await LocalStorage.storeData('userId', userId);
                await LocalStorage.storeData('email', email);

                console.log('Auth login basic success');

                // Ensure user exists in pine_users and get their data (like username)
                const pineUserResponse = await PineServerAPI.ensureUser(userId, email, undefined, institutionRef);
                const pineUser = pineUserResponse.user;

                // Store institution if provided
                if (institutionRef) {
                    await LocalStorage.storeData('institutionRef', institutionRef);
                }

                // Fetch institution name
                let institutionName: string | undefined;
                if (pineUser.institution_ref) {
                    try {
                        const institutions = await PineServerAPI.getInstitutions();
                        const userInst = institutions.find((i: any) => i._id === pineUser.institution_ref);
                        if (userInst) {
                            institutionName = userInst.name;
                        }
                    } catch (e) {
                        console.warn('Failed to fetch institution name', e);
                    }
                }

                const user: AuthUser = {
                    id: userId,
                    email: email,
                    name: pineUser.username || email.split('@')[0],
                    accessToken,
                    refreshToken,
                    user_type: pineUser.user_type || 1,
                    age: pineUser.age,
                    grade: pineUser.grade,
                    institution_ref: pineUser.institution_ref,
                    institution_name: institutionName
                };

                console.log('Auth login success', user);

                return user;
            } else {
                const body = await response.json();
                throw new Error(body.message || 'Login failed');
            }
        } catch (error) {
            console.error('Auth Login error:', error);
            throw error;
        }
    }

    async signup(email: string, password: string, name: string, institutionRef?: string): Promise<AuthUser> {
        try {
            // 1. Create account in Roble Auth
            const response = await fetch(`${this.baseUrl}/signup-direct`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email,
                    name, // Roble auth stores a name, we can send it but we rely on pine_users
                    password,
                }),
            });

            if (response.status === 201) {
                // 2. Login to get token
                const loginResponse = await fetch(`${this.baseUrl}/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password }),
                });

                const loginData = await loginResponse.json();
                const accessToken = loginData.accessToken;
                const userId = loginData.user.id;

                await LocalStorage.storeData('token', accessToken);
                await LocalStorage.storeData('refreshToken', loginData.refreshToken);
                await LocalStorage.storeData('userId', userId);
                await LocalStorage.storeData('email', email);

                // Store institution if provided
                if (institutionRef) {
                    await LocalStorage.storeData('institutionRef', institutionRef);
                }

                // 3. Create entry in pine_users directly
                await PineServerAPI.ensureUser(userId, email, name, institutionRef);

                return {
                    id: userId,
                    email,
                    name,
                    accessToken,
                    refreshToken: loginData.refreshToken
                };
            } else {
                const body = await response.json();
                throw new Error(body.message || 'Signup failed');
            }
        } catch (error) {
            console.error('Signup error:', error);
            throw error;
        }
    }

    async logout(): Promise<void> {
        try {
            const token = await LocalStorage.retrieveData<string>('token');
            if (token) {
                await fetch(`${this.baseUrl}/logout`, {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${token}` },
                });
            }
        } catch (e) {
            console.warn('Logout error', e);
        } finally {
            await LocalStorage.removeData('token');
            await LocalStorage.removeData('refreshToken');
            await LocalStorage.removeData('userId');
            await LocalStorage.removeData('email');
        }
    }

    async getCurrentUser(): Promise<AuthUser | null> {
        try {
            const userId = await LocalStorage.retrieveData<string>('userId');
            const token = await LocalStorage.retrieveData<string>('token');
            const email = await LocalStorage.retrieveData<string>('email');

            if (!userId || !token) return null;

            // Verify token validity
            const verifyResponse = await fetch(`${this.baseUrl}/verify-token`, {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (verifyResponse.status !== 200) {
                // Token invalid
                await this.logout();
                return null;
            }

            // Get user details from pine_users to ensure we have the name
            let name = email?.split('@')[0] || 'User';
            try {
                if (email) {
                    const pineUserResponse = await PineServerAPI.ensureUser(userId, email);
                    if (pineUserResponse.user && pineUserResponse.user.username) {
                        name = pineUserResponse.user.username;
                    }
                }
            } catch (e) {
                console.warn('Could not fetch pine user details', e);
            }

            return {
                id: userId,
                email: email || '',
                name: name,
                accessToken: token,
                refreshToken: await LocalStorage.retrieveData<string>('refreshToken') || ''
            };
        } catch (error) {
            console.error('Get current user error:', error);
            return null;
        }
    }
}

export const authService = new AuthService();
