/**
 * Clear Saved Language Preference
 * 
 * Run this in your browser console to clear the saved language
 * and let the app re-detect your browser language.
 */

// Open browser DevTools (F12) and paste this in the console:

// For web (localStorage)
localStorage.removeItem('@r_pino_language');

// Then refresh the page
location.reload();
