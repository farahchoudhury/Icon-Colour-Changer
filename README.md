# Colorblind-Friendly Icon Processor

A Python desktop application for generating accessibility-friendly icon variants.

The application processes PNG icons and automatically creates light, dark, and colourblind-friendly versions using image outlining and K-Means colour clustering. A simple GUI allows you to select multiple files, choose an output directory, and process icons in bulk.

## Features

- Generate light theme icon exports (original icon)
- Generate dark theme icon exports using a white outline for visibility
- Generate colourblind-friendly icon variants for:
  - Deuteranopia
  - Protanopia
  - Tritanopia
- K-Means colour clustering for intelligent colour remapping
- Batch process multiple PNG files at once
- Select which output variants to generate
- View selected files before processing
- Progress bar and status updates during processing
- Built with Tkinter for a lightweight desktop interface
- Can be packaged as a standalone executable using PyInstaller

## How It Works

### Light Theme

Exports the original icon without modification.

### Dark Theme

Adds a white outline around the icon while preserving the original colours. This improves visibility when icons are displayed on dark backgrounds.

### Colourblind-Friendly Themes

The application uses K-Means clustering to identify dominant colours within an icon. Detected colours are classified and remapped to accessibility-focused palettes designed for:

- Deuteranopia
- Protanopia
- Tritanopia

This approach preserves the overall appearance of the icon while improving colour distinction for users with colour vision deficiencies.

## Supported File Types

### Input

- PNG (`.png`)

### Output

Selected variants are generated into separate folders:

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
2. Click **Add Files** and select one or more PNG icons
3. (Optional) Click **View Files** to review selected inputs
4. Choose an output directory.
5. Select which variants you want to generate.
6. Click **Process Icons**.
7. Output folders will be created per selected variant.

## Contributing

Feel free to fork the project, experiment, and submit improvements!
