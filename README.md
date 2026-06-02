# Icon-Colour-Changer

This Python script processes icon images and generates multiple accessibility-friendly variants. It provides a graphical user interface (GUI) for selecting input files and an output directory, and automatically produces light, dark, and colourblind-optimized versions using outline generation and K-Means colour clustering.
## Features

* Generate light and dark versions of icons.
* Dark mode automatically adds a clean white outline instead of inverting colours.
* Create colourblind-friendly icons using K-Means clustering and predefined palettes.
* Display selected files in a vertical list in the GUI.
* Show the selected output directory in the main window.
* Batch-process multiple images at once.
* Package the app into an executable using `PyInstaller`.

## Colour Schemes

The script supports the following output themes:

* Light: Original icon
* Dark: White-outline variant for dark UIs
* Deuteranopia: Optimized recolour using accessible palette
* Protanopia: Optimized recolour using accessible palette
* Tritanopia: Optimized recolour using accessible palette

K-Means is used to detect dominant colours in the icon and recolour them based on the selected accessibility mode.

## Usage
- You can run the exe (windows only)
- You can clone and edit the source code and build it yourself, go nuts!
