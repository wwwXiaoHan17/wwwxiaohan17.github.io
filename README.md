# Pyera Documentation Site

This directory contains the source files for the Pyera documentation website,
designed to be hosted on **GitHub Pages**.

## Features

- **Trilingual**: Chinese (中文), English, Japanese (日本語)
- **Dark / Light mode**: Automatic system preference + manual toggle
- **Responsive**: Mobile-friendly sidebar and layout
- **API Search**: Ctrl+K to search across all documented APIs
- **Copy code**: One-click copy for all code blocks
- **Markdown/RST rendering**: Common docstring syntax such as fenced code blocks,
  inline code, bold/emphasis, lists, links, `:func:` references, and NumPy-style
  sections is rendered into readable HTML.
- **Beginner-friendly API parameters**: Parameter cards show whether a value is
  required, its Python type, default value, and a plain-language description.
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

## Writing Docstrings

Use NumPy-style sections so the generator can extract parameter help:

```python
def print_line(text: str) -> None:
    """打印一行文本。

    支持常见 Markdown/RST 片段，例如 ``inline code``、**强调**、
    :func:`print` 引用、项目列表和代码块。

    Parameters
    ----------
    text : str
        要显示在 Emuera 输出窗口中的文本。

    Returns
    -------
    None
    """
```

The API page shows only the summary prose above `Parameters` in the description
area. Parameter details are rendered separately as beginner-friendly cards.

## Search Behavior

Every generated page embeds the global API search index in
`<script id="search-data" type="application/json">`. This keeps `Ctrl+K` working
when the docs are opened from disk or previewed in environments where `fetch()`
cannot load local JSON files. The standalone `api/search-index.json` is still
generated for tools and hosted previews.

## Language Switching

The site uses JavaScript-based language switching with `localStorage` persistence.
Each page contains three `<div class="lang-content">` blocks (zh/en/ja), and the
active language is toggled by the top-bar buttons.

## License

Same as pyera: MIT
