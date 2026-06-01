# Pyera Documentation Site

This directory contains the source files for the Pyera documentation website,
designed to be hosted on **GitHub Pages**.

## Features

- **Trilingual**: Chinese (中文), English, Japanese (日本語)
- **Dark / Light mode**: Automatic system preference + manual toggle
- **Responsive**: Mobile-friendly sidebar and layout
- **API Search**: Ctrl+K to search across all documented APIs
- **Copy code**: One-click copy for all code blocks
- **Offline-ready**: All static files, no external CDN dependencies

## File Structure

```
docs/
├── index.html              # Homepage
├── getting-started.html    # Quick start guide
├── api/                    # API reference pages (18 modules)
│   ├── display.html
│   ├── input.html
│   ├── flow.html
│   ├── chara-ops.html
│   ├── array-ops.html
│   ├── csv.html
│   ├── save-load.html
│   ├── builtin.html
│   ├── sound.html
│   ├── vars.html
│   ├── chara-class.html
│   ├── async.html
│   ├── events.html
│   ├── logging.html
│   ├── types.html
│   ├── utils.html
│   ├── exceptions.html
│   └── core.html
├── examples/
│   ├── basic-game.html
│   └── async-integration.html
├── css/
│   └── style.css           # Shared stylesheet
├── js/
│   └── lang.js             # Language switching, theme, search, copy
└── generate.py             # Documentation generator script
```

## Deployment

### Option 1: GitHub Actions (Recommended)

1. Push this repo to GitHub
2. Go to **Settings → Pages** in your GitHub repository
3. Set **Source** to "GitHub Actions"
4. The included `.github/workflows/pages.yml` will automatically build and deploy on every push

### Option 2: Manual (docs folder)

1. Push this repo to GitHub
2. Go to **Settings → Pages**
3. Set **Source** to "Deploy from a branch"
4. Select **Branch: main / master** and **Folder: /docs**
5. Click Save

### Option 3: Local Preview

```bash
cd docs
python -m http.server 8080
# Open http://localhost:8080
```

## Regenerating Documentation

If you modify the pyera source code docstrings, regenerate the docs:

```bash
cd docs
python generate.py
```

This script parses all `pyera/*.py` modules via AST and regenerates the HTML pages.

## Language Switching

The site uses JavaScript-based language switching with `localStorage` persistence.
Each page contains three `<div class="lang-content">` blocks (zh/en/ja), and the
active language is toggled by the top-bar buttons.

## License

Same as pyera: MIT
