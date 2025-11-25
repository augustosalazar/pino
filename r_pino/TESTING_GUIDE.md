# Testing Guide - Adaptive Interface

## Quick Start

To test the new adaptive interface on web, you'll need to run the Expo web server.

### Option 1: Using PowerShell (if execution policies allow)
```powershell
npm run web
```

### Option 2: PowerShell Execution Policy Issue Fix
If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try:
```powershell
npm run web
```

### Option 3: Use Command Prompt Instead
```cmd
npm run web
```

### Option 4: Direct npx command
```bash
npx expo start --web
```

## What to Test

### 1. Login Screen Responsive Behavior
- **Desktop (>1024px)**: Login form should be centered with max 500px width
- **Tablet (768-1024px)**: Form remains centered but slightly wider
- **Mobile (<768px)**: Form takes full width with padding

### 2. Home Screen Layout Changes
- **Desktop View**:
  - Content constrained to 1000px max width
  - Score card and difficulty card side-by-side (2-column grid)
  - Action buttons (Start Session, View Stats) horizontal
  - Centered with subtle shadow
  
- **Mobile View**:
  - Full-width content
  - Cards stacked vertically
  - Buttons stacked vertically
  - No changes from original mobile design

### 3. Session Screen Optimization
- **Desktop**: Exercise card centered, max 700px width
- **Mobile**: Full width as before

## Testing Checklist

### Desktop Browser Test (Chrome/Firefox/Edge)
- [ ] Open `http://localhost:8081` (or port shown by Expo)
- [ ] Verify login form is centered
- [ ] Verify home screen shows 2-column card layout
- [ ] Verify buttons are side-by-side on home screen
- [ ] Verify session screen exercises are centered

### Responsive Behavior Test
- [ ] Start at desktop width (1920px)
- [ ] Slowly resize browser window to narrow
- [ ] Verify layout switches to mobile at ~768px
- [ ] Cards should stack vertically when narrow
- [ ] Buttons should stack vertically when narrow

### Breakpoint Verification
1. **Desktop (≥1024px)**: Grid layouts active
2. **Tablet (768-1023px)**: Centered but no grid
3. **Mobile (<768px)**: Full-width mobile layout

### Cross-Browser Testing
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if available)

## Visual Expectations

### Before (Mobile-like on Web)
- Content stretched across entire wide screen
- Single column taking 100% width
- Awkward spacing on ultrawide monitors
- Buttons uncomfortably wide

### After (Adaptive Web)
- Content centered with professional margins
- Max widths prevent over-stretching
- Cards arranged in logical grids on desktop
- Buttons appropriately sized
- Depth with shadows

## Console Checks

Open browser DevTools console and verify:
- No React errors
- No style warnings
- Responsive hook updates on resize

## Performance Check

- Resize window rapidly - should be smooth
- No layout shift or flickering
- Hooks should debounce properly

## Mobile Verification

Important: Ensure mobile experience unchanged
- Test on actual mobile device or
- Use Chrome DevTools device emulation
- Verify mobile layouts identical to before
- No unwanted margins or centering on mobile

## Known Issues to Ignore

The TypeScript lints about React/React-Native modules are expected:
- They occur because TypeScript analyzes before node_modules load
- Will disappear once you run the app
- Safe to ignore during development

## Success Criteria

✅ Desktop users see professional, centered layouts
✅ Mobile users see no changes (existing design preserved)
✅ Smooth transitions when resizing browser
✅ All screens maintain functionality
✅ No console errors in browser
