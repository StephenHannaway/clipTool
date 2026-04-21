# clipboard-manager

A Windows clipboard history manager with OCR capture, running in the system tray.

## Requirements

- Python 3.12+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`

## Setup

```bash
uv sync
```

## Usage

```bash
just clip
```

| Hotkey | Action |
|--------|--------|
| `Ctrl+Alt+V` | Open clipboard history picker |
| `Ctrl+Alt+G` | OCR screen region — captures text from a drawn selection |
| `Ctrl+Alt+K` | Column select — OCR captures text from a drawn selection and copies it |

Hotkeys and other settings are configurable in `~/.clipboard-manager/settings.json`.

## Development

```bash
just check     # lint + format check + type check (CI gate)
just test      # run tests
just test-cov  # run tests with coverage report
just fmt       # auto-format
just clean     # remove build/cache artifacts
```
