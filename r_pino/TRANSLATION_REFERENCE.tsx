/**
 * Quick Reference: How to Add Translations to Remaining Screens
 * 
 * This file shows the exact replacements needed for each screen.
 */

// ============================================
// 1. HOME SCREEN (app/index.tsx)
// ============================================

// ADD IMPORT at top:
import { useTranslation } from 'react-i18next';

// ADD HOOK in component:
const { t } = useTranslation();

// REPLACE TEXT:
// Line ~40:  setError('Failed to load statistics...')
setError(t('home.failedToLoadStats'));

// Line ~74:  'Retry'
{ t('common.retry') }

// Line ~88:  'R_PINE'
{ t('home.title') }

// Line ~90:  'Logout'
{ t('common.logout') }

// Line ~93:  'Welcome, {user?.name}'
{ t('home.welcome', { name: user?.name }) }

// Line ~98:  'Current Score'
{ t('home.currentScore') }

// Line ~105:  'Sessions'
{ t('home.sessions') }

// Line ~109:  'Accuracy'
{ t('home.accuracy') }

// Line ~113:  'Exercises'
{ t('home.exercises') }

// Line ~124:  'Current Difficulty'
{ t('home.currentDifficulty') }

// Line ~139:  'Start New Session'
{ t('home.startNewSession') }

// Line ~143:  'View Statistics'
{ t('home.viewStatistics') }


// ============================================
// 2. SESSION SCREEN (app/session.tsx)
// ============================================

// ADD IMPORT at top:
import { useTranslation } from 'react-i18next';

// ADD HOOK in component:
const { t } = useTranslation();

// REPLACE TEXT:
// Line ~135:  'Solve this:'
{ t('session.solveThis') }

// Line ~140:  'Difficulty: {exercise.difficulty_level.toFixed(1)}'
{ t('session.difficulty', { level: exercise.difficulty_level.toFixed(1) }) }

// Line ~161:  placeholder="Enter your answer"
placeholder = { t('session.enterAnswer') }

// Line ~168:  'Submit'
{ t('common.submit') }


// ============================================
// EXACT CODE SNIPPETS
// ============================================

/* 
HOME SCREEN - Add after line 14:
*/
const { t } = useTranslation();

/*
HOME SCREEN - Replace loadUserStats error handler (line 38-40):
*/
} catch (error) {
    console.error('Failed to load stats:', error);
    setError(t('home.failedToLoadStats'));
}

/*
HOME SCREEN - Replace header section (lines 85-93):
*/
<View style={styles.header}>
    <View style={styles.headerTop}>
        <Text style={styles.title}>{t('home.title')}</Text>
        <TouchableOpacity onPress={handleLogout} style={styles.logoutButton}>
            <Text style={styles.logoutText}>{t('common.logout')}</Text>
        </TouchableOpacity>
    </View>
    <Text style={styles.subtitle}>{t('home.welcome', { name: user?.name })}</Text>
</View>

/*
HOME SCREEN - Replace score card labels:
*/
<Text style={styles.scoreLabel}>{t('home.currentScore')}</Text>

<Text style={styles.statLabel}>{t('home.sessions')}</Text>

<Text style={styles.statLabel}>{t('home.accuracy')}</Text>

<Text style={styles.statLabel}>{t('home.exercises')}</Text>

<Text style={styles.cardTitle}>{t('home.currentDifficulty')}</Text>

/*
HOME SCREEN - Replace buttons:
*/
<Text style={styles.primaryButtonText}>{t('home.startNewSession')}</Text>

<Text style={styles.secondaryButtonText}>{t('home.viewStatistics')}</Text>

/*
SESSION SCREEN - Add after line 10:
*/
const { t } = useTranslation();

/*
SESSION SCREEN - Replace exercise card text (lines 135-140):
*/
<View style={styles.exerciseCard}>
    <Text style={styles.exerciseLabel}>{t('session.solveThis')}</Text>
    <Text style={styles.exerciseText}>
        {exercise.operand_1} {exercise.operator} {exercise.operand_2} = ?
    </Text>
    <Text style={styles.difficultyLabel}>
        {t('session.difficulty', { level: exercise.difficulty_level.toFixed(1) })}
    </Text>
</View>

/*
SESSION SCREEN - Replace text input placeholder (line ~161):
*/
<TextInput
    style={styles.textInput}
    value={textAnswer}
    onChangeText={setTextAnswer}
    keyboardType="numeric"
    placeholder={t('session.enterAnswer')}
    autoFocus
/>

/*
SESSION SCREEN - Replace submit button text (line ~168):
*/
<Text style={styles.submitButtonText}>{t('common.submit')}</Text>
