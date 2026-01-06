# ClipX

The most simple clipboard history manager for macOS

![macOS](https://img.shields.io/badge/macOS-13.0+-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- **Clipboard History** — Automatically tracks your last 50 copied items (text and images)
- **Global Hotkey** — Press `Cmd + Option + V` anywhere to open the popup
- **Smart Positioning** — Popup appears near your current text cursor using Accessibility APIs
- **Edit Mode** — Easily delete individual items from your history
- **Image Support** — Copies images with thumbnail previews (PNG/TIFF)
- **Menu Bar Integration** — Quick access to preferences, history clearing, and updates
- **Auto-Updates** — Checks for the latest version and updates seamlessly
- **Native UI** — Glassmorphism design with smooth spring animations
- **Privacy Focused** — No data leaves your device; extensive logging disabled in production builds

## Usage

### Shortcut

Press **Cmd + Option + V** to open the clipboard history popup.

### Managing Items

- **Paste**: Click an item or press `Enter` to paste it into your active application.
- **Delete**: Click the "Edit" button (top right of the popup) to enter Edit Mode, then click the trash icon next to any item to remove it.
- **Select**: Use `Up`/`Down` arrows to navigate through the list.

### Menu Bar

Click the ClipX icon in the menu bar to access:
- **Clear History**: Wipes all stored clipboard items.
- **Launch on startup**: Toggle to automatically start ClipX when you log in.
- **Check for Updates**: Manually check for new versions.
- **Quit ClipX**: Exit the application.

### Popup Location

The popup attempts to appear intelligently based on your context:
- Often directly below your text cursor
- Near the active input field (e.g., Chrome URL bar)

## Installation

### Download App (Recommended)

The easiest way to install ClipX is to download the latest pre-built application:

1. Go to the [Releases](../../releases) page.
2. Download the `ClipX.zip` file from the "Automatic Build" (latest) release.
3. Unzip the file and drag `ClipX.app` to your Applications folder.

> **Note:** Since this app is not signed with an Apple Developer ID, you may need to right-click the app and select "Open" the first time you run it.

### Prerequisites (For Source/Dev)

- macOS 13.0 (Ventura) or later
- Python 3.10+

### Setup (Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/ClipX.git
cd ClipX

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

### Building from Source

To create a standalone macOS application (.app):

```bash
# Build the application
python3 setup.py py2app
```

The application will be generated in the `dist/` directory.

### Grant Accessibility Permission

ClipX requires Accessibility permission to:
- Detect the global hotkey
- Position the popup near your cursor

1. Open **System Settings > Privacy & Security > Accessibility**
2. Add **ClipX** (or your Terminal/IDE if running from source) to the list
3. Enable the toggle

## Architecture

```
ClipX/
├── .github/workflows/   # CI/CD pipelines
│   └── release.yml      # Auto-builds and publishes releases
├── main.py              # App entry point & coordinator
├── clipboard_monitor.py # Polls NSPasteboard for changes
├── hotkey_handler.py    # CGEventTap for global hotkey
├── accessibility.py     # AX API for cursor position
├── updater.py           # Auto-update logic
├── startup.py           # Launch on startup management
├── setup.py             # py2app build configuration
├── ui/                  # UI configuration and components
│   ├── popup.py         # Main NSPanel implementation
│   ├── item_view.py     # Individual clipboard item views
│   └── ...
└── icon.icns            # Menu bar icon
```

## License

MIT License — feel free to use and modify.

---

Made with care for macOS power users
