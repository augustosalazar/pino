import AsyncStorage from '@react-native-async-storage/async-storage';

export class LocalStorage {
    static async storeData(key: string, value: string): Promise<void> {
        try {
            await AsyncStorage.setItem(key, value);
        } catch (e) {
            console.error('Error storing data', e);
        }
    }

    static async retrieveData<T>(key: string): Promise<T | null> {
        try {
            const value = await AsyncStorage.getItem(key);
            if (value !== null) {
                // Try to parse if it looks like JSON, otherwise return as string
                try {
                    return JSON.parse(value) as T;
                } catch {
                    return value as unknown as T;
                }
            }
            return null;
        } catch (e) {
            console.error('Error retrieving data', e);
            return null;
        }
    }

    static async removeData(key: string): Promise<void> {
        try {
            await AsyncStorage.removeItem(key);
        } catch (e) {
            console.error('Error removing data', e);
        }
    }
}
