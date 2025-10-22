# Web Deployment Guide

This Chemistry Card Game can be played in any modern web browser using Pygbag!

## Quick Local Testing

1. **Install Pygbag:**
   ```bash
   pip install pygbag
   ```

2. **Run locally in browser:**
   ```bash
   pygbag chemistry_card_game.py
   ```

3. **Open your browser to:**
   ```
   http://localhost:8000
   ```

The game will load and run directly in your browser!

## Deploy to Web (GitHub Pages)

### Step 1: Build for Production
```bash
# Build the web version
pygbag --build chemistry_card_game.py
```

This creates a `build/web` directory with all necessary files.

### Step 2: Deploy to GitHub Pages

1. Create a new repository on GitHub (or use existing)

2. Copy the contents of `build/web` to your repository

3. In GitHub repository settings:
   - Go to **Settings** → **Pages**
   - Set **Source** to `main` branch
   - Click **Save**

4. Your game will be live at:
   ```
   https://yourusername.github.io/repository-name/
   ```

## Deploy to itch.io

1. **Build for web:**
   ```bash
   pygbag --build chemistry_card_game.py
   ```

2. **Create a ZIP file:**
   - Navigate to `build/web`
   - Select all files
   - Create a ZIP archive

3. **Upload to itch.io:**
   - Go to itch.io and create a new project
   - Set **Kind of project** to "HTML"
   - Upload your ZIP file
   - Check "This file will be played in the browser"
   - Set viewport dimensions: 1400x900 (or use iframe)
   - Publish!

## Deploy to Your Own Server

Simply upload the contents of `build/web` to any web hosting service:

- Netlify: Drag and drop the `build/web` folder
- Vercel: Deploy via CLI or GitHub integration
- Any static host: Upload via FTP/SFTP

## Browser Compatibility

The game works in all modern browsers that support:
- WebAssembly
- HTML5 Canvas
- ES6 JavaScript

Tested on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

### Game doesn't load
- Make sure you're using a modern browser
- Check browser console for errors (F12)
- Ensure all files from `build/web` are uploaded together

### Performance issues
- The game is optimized for 60 FPS
- Close other browser tabs
- Try a different browser

### Files not found
- Ensure `game_info.json` is in the same directory as `chemistry_card_game.py`
- Pygbag will automatically bundle it during build

## Development Notes

The game has been modified for web compatibility:
- Uses `asyncio` for non-blocking game loop
- Replaces `sys.exit()` with clean `pygame.quit()`
- All file operations are web-compatible

To switch back to desktop mode, simply run:
```bash
python3 chemistry_card_game.py
```

Both versions work from the same codebase!
