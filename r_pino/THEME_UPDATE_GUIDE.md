# Quick Guide: Applying Theme to Remaining Screens

This guide shows you how to quickly update any screen in the app to support dark/light mode.

## Step-by-Step Process

### 1. Import the Theme Hook

At the top of your component file, add:

```tsx
import { useTheme } from '../contexts/ThemeContext';
// or for admin screens:
import { useTheme } from '../../contexts/ThemeContext';
```

### 2. Use the Hook in Your Component

```tsx
export default function YourScreen() {
    const { theme, isDark } = useTheme();
    // ... rest of your code
}
```

### 3. Replace Hardcoded Colors

#### Before:
```tsx
<View style={styles.container}>
    <Text style={styles.text}>Hello</Text>
</View>

const styles = StyleSheet.create({
    container: {
        backgroundColor: '#F5F5F7',
    },
    text: {
        color: '#333',
    },
});
```

#### After:
```tsx
<View style={[styles.container, { backgroundColor: theme.background }]}>
    <Text style={[styles.text, { color: theme.text }]}>Hello</Text>
</View>

const styles = StyleSheet.create({
    container: {
        // Remove: backgroundColor: '#F5F5F7',
    },
    text: {
        // Remove: color: '#333',
    },
});
```

### 4. Update StatusBar

```tsx
<StatusBar style={theme.statusBarStyle} />
```

## Common Color Mappings

| Old Hardcoded Color | New Theme Property |
|---------------------|-------------------|
| `#F5F5F7` (light gray bg) | `theme.background` |
| `#FFFFFF` (white) | `theme.surface` or `theme.cardBackground` |
| `#007AFF` (blue) | `theme.primary` |
| `#333`, `#000` (dark text) | `theme.text` |
| `#666` (gray text) | `theme.textSecondary` |
| `#999` (light gray text) | `theme.textTertiary` |
| `#E0E0E0` (border) | `theme.border` |
| `#FF3B30` (error red) | `theme.error` |
| `#34C759` (success green) | `theme.success` |

## Complete Example

Here's a complete before/after example:

### Before:
```tsx
import { View, Text, StyleSheet } from 'react-native';
import { StatusBar } from 'expo-status-bar';

export default function MyScreen() {
    return (
        <View style={styles.container}>
            <StatusBar style="dark" />
            <View style={styles.card}>
                <Text style={styles.title}>Title</Text>
                <Text style={styles.subtitle}>Subtitle</Text>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#F5F5F7',
    },
    card: {
        backgroundColor: '#FFFFFF',
        borderRadius: 12,
        padding: 16,
        borderWidth: 1,
        borderColor: '#E0E0E0',
    },
    title: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#333',
    },
    subtitle: {
        fontSize: 14,
        color: '#666',
    },
});
```

### After:
```tsx
import { View, Text, StyleSheet } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { useTheme } from '../contexts/ThemeContext';

export default function MyScreen() {
    const { theme } = useTheme();
    
    return (
        <View style={[styles.container, { backgroundColor: theme.background }]}>
            <StatusBar style={theme.statusBarStyle} />
            <View style={[
                styles.card,
                {
                    backgroundColor: theme.cardBackground,
                    borderColor: theme.border,
                }
            ]}>
                <Text style={[styles.title, { color: theme.text }]}>Title</Text>
                <Text style={[styles.subtitle, { color: theme.textSecondary }]}>Subtitle</Text>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        // No backgroundColor here anymore
    },
    card: {
        borderRadius: 12,
        padding: 16,
        borderWidth: 1,
        // No backgroundColor or borderColor here anymore
    },
    title: {
        fontSize: 20,
        fontWeight: 'bold',
        // No color here anymore
    },
    subtitle: {
        fontSize: 14,
        // No color here anymore
    },
});
```

## Tips

1. **Keep styles minimal**: Only keep positioning, sizing, and non-color properties in StyleSheet
2. **Use inline styles for colors**: Apply theme colors using inline styles like `{ backgroundColor: theme.background }`
3. **Test both themes**: Always test your screen in both light and dark mode
4. **Use the array syntax**: Combine static styles with theme styles using `[styles.container, { backgroundColor: theme.background }]`

## Quick Checklist

- [ ] Import `useTheme` hook
- [ ] Use theme in component: `const { theme } = useTheme()`
- [ ] Update StatusBar: `<StatusBar style={theme.statusBarStyle} />`
- [ ] Replace background colors with `theme.background`, `theme.surface`, or `theme.cardBackground`
- [ ] Replace text colors with `theme.text`, `theme.textSecondary`, or `theme.textTertiary`
- [ ] Replace primary color (#007AFF) with `theme.primary`
- [ ] Replace border colors with `theme.border`
- [ ] Replace divider colors with `theme.divider`
- [ ] Test in both light and dark modes
