# PulsarAI Chat

LLM chatbot with support for multiple providers (VseLLM, OpenRouter, Mock).

## Installation

### Via Installer (Windows)

1. Download the installer file `pulsar-chat-setup.exe` from releases
2. Run the installer and follow the instructions
3. After installation, launch the application via the desktop shortcut

### Via Docker

```bash
# Clone repository
git clone <repo-url>
cd llm_chat

# Run in development mode
docker-compose --profile dev up -d

# Run in production mode
docker-compose --profile prod up -d
```

### Local Development

**Backend (Python 3.13+):**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

**Frontend (Node.js 18+):**
```bash
cd frontend
npm install
npm run dev
```

## Building

### Using build.ps1

The `build.ps1` script is designed for convenient project building:

```powershell
# Full build (backend + frontend)
.\build.ps1

# Only backend
.\build.ps1 -Target backend

# Only frontend
.\build.ps1 -Target frontend

# Build Electron application
.\build.ps1 -Target electron
```

**Requirements:**
- Windows PowerShell 5.1+
- Python 3.13+ (for backend)
- Node.js 18+ (for frontend)

### Manual Build

**Backend:**
```bash
cd backend
python -m PyInstaller --onefile --name pulsar_backend run.py
```

**Frontend:**
```bash
cd frontend
npm run build
```

## Configuration

### Provider Configuration

1. Open the chat
2. Click the "Settings" button (⚙)
3. Navigate to the "AI Providers" section
4. Select a provider and enter the API key:
   - **VseLLM**: enter VseLLM API key
   - **OpenRouter**: enter OpenRouter API key
   - **Mock**: no key required (for testing)

### Chat Parameters

In settings you can change:
- Chat model
- Temperature (response creativity)
- Maximum tokens
- System prompt

### Storage Settings

Chats are saved locally in the `chats.json` file in the application folder.

## Website Integration

**In Development**

Integration will be available in the future via:
- Embeddable widget
- API for embedding into existing projects
- Plugins for popular CMS

## Development

### Project Structure

```
llm_chat/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── providers/   # LLM provider adapters
│   │   ├── routes/      # API endpoints
│   │   └── storage.py   # Chat storage
│   └── requirements.txt
├── frontend/         # Vue 3 + Vite frontend
│   ├── src/
│   │   ├── components/  # Vue components
│   │   ├── stores/      # Pinia stores
│   │   └── themes/      # UI themes
│   └── package.json
└── docker-compose.yml
```

### Running Tests

```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
pytest
```

## Restarting Containers

To restart all containers use:

```bash
docker-compose restart
```

**Important:** Do not use `docker compose --profile dev restart frontend-dev` — it does not restart the server correctly.

## Windows Specifics

If you have a SOCKS proxy configured (e.g., `socks=127.0.0.1:10808`), set this before running:

```powershell
$env:no_proxy="*"
```

## Themes

The application supports theme switching. Themes are located in the `frontend/src/themes/` folder.

Available themes:
- Dark Space (default)
- Neutral Gray
- Light Clean
- Light Warm
- Ocean Dark
- Forest
- Steampunk

### How to Add Your Own Theme

To create a new theme:

1. **Create theme folder**

   In `frontend/src/themes/` create a new folder with your theme name, e.g., `my-theme/`.

2. **Add theme files**

   In the theme folder create two files:
   - `index.scss` — theme styles
   - `index.css` — compiled styles (if using a preprocessor)

3. **Register theme in index.ts**

   Open `frontend/src/themes/index.ts` and add the new theme to the `THEMES` array:

   ```typescript
   {
     id: 'my-theme',              // Unique theme identifier
     name: 'My Theme',            // Display name
     description: 'Theme description', // Brief description
     dark: true,                  // true for dark theme, false for light
     vars: {
       accent:       '#6366F1',    // Primary accent color
       accentL:      '#818CF8',   // Light accent color
       accentDim:    'rgba(99,102,241,0.18)', // Dimmed accent
       accentBorder: 'rgba(99,102,241,0.45)', // Accent border
       bg:           '#0a0a0f',    // Main background
       bgS:          'rgba(255,255,255,0.06)', // Surface background
       bgG:          'rgba(255,255,255,0.08)', // Group background
       bgGh:         'rgba(255,255,255,0.13)', // Hover background
       bgPanel:      '#13131f',    // Panel background
       brd:          'rgba(255,255,255,0.13)', // Borders
       brdA:         'rgba(99,102,241,0.55)', // Accent borders
       t1:           '#F1F1F5',    // Primary text
       t2:           '#A9A9C0',    // Secondary text
       t3:           '#6B6B85',    // Tertiary text
       blur:         'blur(20px)',  // Blur effect
       shadowPop:    '0 20px 60px rgba(0,0,0,0.6),0 0 0 1px rgba(255,255,255,0.07)', // Shadows
       bodyGradient: 'radial-gradient(...)', // Background gradient (or 'none')
       codeInlineColor: '#e2b96f', // Inline code color
       hljsStyle:    'github-dark', // Syntax highlighting style
     },
   },
   ```

4. **Choosing syntax highlighting style**

   Available values for `hljsStyle`:
   - `github-dark` — GitHub dark theme
   - `github` — GitHub light theme
   - `base16-tomorrow` — Base16 Tomorrow theme
   - `atom-one-light` — Atom One Light theme

5. **Applying the theme**

   After adding the theme to the `THEMES` array, it will automatically become available in the application settings dropdown.

6. **Testing**

   Run the application in development mode:
   ```bash
   cd frontend
   npm run dev
   ```

   Open settings and select your theme from the list.

### Theme Creation Example

Complete example of creating a dark theme with green accent:

```typescript
{
  id: 'green-dark',
  name: 'Green Dark',
  description: 'Dark theme with green accent',
  dark: true,
  vars: {
    accent:       '#10B981',
    accentL:      '#34D399',
    accentDim:    'rgba(16,185,129,0.15)',
    accentBorder: 'rgba(16,185,129,0.40)',
    bg:           '#0a0f0a',
    bgS:          'rgba(255,255,255,0.05)',
    bgG:          'rgba(255,255,255,0.07)',
    bgGh:         'rgba(255,255,255,0.11)',
    bgPanel:      '#0d1f14',
    brd:          'rgba(255,255,255,0.10)',
    brdA:         'rgba(52,211,153,0.5)',
    t1:           '#ECFDF5',
    t2:           '#6EE7B7',
    t3:           '#2D5A3D',
    blur:         'blur(20px)',
    shadowPop:    '0 20px 60px rgba(0,0,0,0.7),0 0 0 1px rgba(16,185,129,0.10)',
    bodyGradient: 'radial-gradient(ellipse 60% 50% at 15% 20%,rgba(16,185,129,0.10) 0%,transparent 60%)',
    codeInlineColor: '#34D399',
    hljsStyle:    'github-dark',
  },
}
```

## License

MIT License
