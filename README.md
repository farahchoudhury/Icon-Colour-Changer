# Icon Colour Changer

A Python desktop application for generating accessibility-friendly icon variants.

The application processes PNG icons and automatically creates light, dark, and colourblind-friendly versions using image outlining and K-Means colour clustering. A simple GUI allows you to select multiple files, choose an output directory, and process icons in bulk.

## Features

- Generate light and dark theme icon variants
- Create colourblind-friendly versions for:
  - Deuteranopia
  - Protanopia
  - Tritanopia
- Dark mode uses a white outline for improved visibility instead of colour inversion
- K-Means colour clustering for intelligent colour remapping
- Batch process multiple PNG files at once
- Simple desktop GUI built with Tkinter
- Scrollable file list for larger batches
- Status bar with processing and completion feedback
- Can be packaged as a standalone executable using PyInstaller

## How It Works

### Light Theme

Exports the original icon without modification.

### Dark Theme

Adds a clean white outline around the icon to improve visibility on dark backgrounds.

### Colourblind-Friendly Themes

The application uses K-Means clustering to identify dominant colours in an icon and remaps them to accessibility-focused palettes designed for:

- Deuteranopia
- Protanopia
- Tritanopia

This helps improve colour distinction while preserving the overall appearance of the original icon.

## Supported File Types

### Input

- PNG (`.png`)

### Output

The application generates separate output folders for:

```text
light/
dark/
deuteranopia/
protanopia/
tritanopia/
```

## Running the Application

### From Source

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python colour-changer.py
```

## Building an Executable

Create a standalone executable with PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed colour-changer.py
```

The generated executable will be placed in:

```text
dist/
```

## Usage

1. Launch the application.
2. Select one or more PNG icons.
3. Choose an output directory.
4. Click **Process**.
5. Generated icon variants will be written into theme-specific folders.

## Contributing

Feel free to fork the project, experiment, and submit improvements.
