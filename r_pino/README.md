# R_PINE - React Native App

Math exercise training app with adaptive difficulty powered by AI.

## Features

- ✅ Personalized exercise generation
- ✅ Adaptive difficulty system
- ✅ Two exercise types: multiple choice and text input
- ✅ Real-time progress tracking
- ✅ Detailed statistics and insights
- ✅ Beautiful, modern UI

## Project Structure

```
r_pino/
├── app/
│   ├── _layout.tsx          # Root navigation
│   ├── index.tsx            # Home screen
│   ├── session.tsx          # Exercise session
│   ├── results.tsx          # Session results
│   └── stats.tsx            # User statistics
├── services/
│   ├── api.ts               # PineServer API client
│   └── types.ts             # TypeScript types
└── package.json
```

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure API

Update `services/api.ts` with your PineServer URL:

```typescript
const API_BASE_URL = 'http://your-server-url:8000/api';
```

For local development with Android emulator:
```typescript
const API_BASE_URL = 'http://10.0.2.2:8000/api';
```

For iOS simulator:
```typescript
const API_BASE_URL = 'http://localhost:8000/api';
```

For physical device:
```typescript
const API_BASE_URL = 'http://YOUR_COMPUTER_IP:8000/api';
```

### 3. Run the App

```bash
# Start Expo server
npm start

# Run on Android
npm run android

# Run on iOS
npm run ios

# Run on web
npm run web
```

## Screens

### Home Screen (`index.tsx`)
- Displays current score
- Shows quick stats (sessions, accuracy, exercises)
- Shows current difficulty levels
- **Actions:**
  - Start New Session
  - View Statistics

### Session Screen (`session.tsx`)
- Shows current exercise
- Tracks progress
- **Exercise Types:**
  - Multiple choice (4 options)
  - Text input (keyboard entry)
- Real-time feedback
- Live stats counter

### Results Screen (`results.tsx`)
- Session summary
- Score earned
- Accuracy percentage
- Difficulty adjustments explained
- Motivational messages

### Statistics Screen (`stats.tsx`)
- Overall performance metrics
- Total score
- Sessions completed
- Total exercises & correct answers
- Accuracy with visual progress bar
- Difficulty levels by operator
- Personalized insights

## Development

### Environment

- Expo SDK: ~54.0
- React: 19.1.0
- React Native: 0.81.5
- TypeScript: ~5.9.2

### Key Dependencies

- expo-router: File-based navigation
- @react-navigation: Navigation stack
- expo-status-bar: Status bar management

## API Integration

### Start Session
```typescript
const response = await PineServerAPI.startSession(userRef, numExercises);
// Returns: { session_id, exercises, user_profile }
```

### Complete Session
```typescript
const response = await PineServerAPI.completeSession(sessionId, exercises);
// Returns: { total_exercises, correct_answers, score_earned, difficulty_adjustments }
```

### Get Stats
```typescript
const stats = await PineServerAPI.getUserStats(userRef);
// Returns: { current_score, total_sessions, accuracy, etc. }
```

## Configuration

### User Reference
Currently hardcoded in screens. To integrate with Roble auth:

1. Add Roble auth SDK
2. Get user ID after login
3. Pass to screens via context or state management

```typescript
// services/auth.ts
export const getUserRef = () => {
  // Get from Roble authentication
  return RobleAuth.getCurrentUserId();
};
```

## Customization

### Colors
Main colors are defined in styles. To customize:
- Primary: `#007AFF` (iOS Blue)
- Success: `#34C759` (Green)
- Warning: `#FF9500` (Orange)
- Error: `#FF3B30` (Red)

### Fonts
Uses system fonts. To add custom fonts:
1. Add font files to `assets/fonts/`
2. Load in `app/_layout.tsx`
3. Reference in styles

## Testing

### With Backend
1. Ensure PineServer is running: `python main.py`
2. Update API_BASE_URL in `services/api.ts`
3. Run app and test full flow

### Mock Data (Optional)
Create `services/mock.ts` for offline development:
```typescript
export const mockExercises = [...];
```

## Troubleshooting

### Network Issues
- Check API_BASE_URL configuration
- Ensure PineServer is accessible
- For physical devices, use computer's IP address
- Check firewall settings

### Build Errors
```bash
# Clear cache
npx expo start --clear

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

## Future Enhancements

- [ ] User authentication with Roble
- [ ] Offline mode with local caching
- [ ] Dark mode support
- [ ] Sound effects and haptic feedback
- [ ] Achievement badges
- [ ] Leaderboards
- [ ] Practice mode (time-limited sessions)
- [ ] Custom exercise sets

## License

Copyright © 2025 R_PINE Project
