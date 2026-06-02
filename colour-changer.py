"""
Colorblind-Friendly Icon Processor

This tool processes PNG icon files to generate:
    - Light and Dark theme variants
    - Colorblind-friendly recolored variants (Deuteranopia, Protanopia, Tritanopia)

Dark mode uses a white outline around the original icon for clarity instead of color inversion.
Colorblind modes recolor icon regions using K-Means clustering + palette mapping.

"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
from PIL import Image, ImageFilter, ImageOps
from sklearn.cluster import KMeans


# -----------------------------------------------------------
# Color Replacement Palettes for Colorblind Accessibility
# -----------------------------------------------------------

COLORBLIND_PALETTES = {
    "deuteranopia": {
        "red": (255, 128, 0),
        "green": (0, 128, 255),
        "blue": (128, 0, 255),
        "yellow": (255, 200, 0),
    },
    "protanopia": {
        "red": (255, 200, 0),
        "green": (0, 180, 255),
        "blue": (160, 100, 255),
        "yellow": (255, 220, 120),
    },
    "tritanopia": {
        "red": (255, 80, 80),
        "green": (80, 200, 80),
        "blue": (255, 180, 0),
        "yellow": (255, 200, 100),
    },
}

# Theme outline colors for regular icon exports
ICON_COLORS = {
    "light": "#000000",
    "dark": "#FFFFFF",
}


# -----------------------------------------------------------
# Color Classification Helpers
# -----------------------------------------------------------

def classify_color(rgb):
    """
    Classify an RGB value into a simple color label used for palette mapping.
    Returns:
        A string such as "red", "blue", "green", "yellow", "black",
        or None if the color should be left unchanged.
    """
    r, g, b = rgb
    max_val = max(r, g, b)

    # Treat low brightness as black
    if max_val < 60:
        return "black"

    # Identify dominant color channel
    if b == max_val and b > 80:
        return "blue"
    if r == max_val and r > 80:
        return "red"
    if g == max_val and g > 80:
        return "green"

    # Yellow detection (strong red + green)
    if r > 100 and g > 100 and b < 120:
        return "yellow"

    return None


# -----------------------------------------------------------
# K-Means Colorblind Recoloring
# -----------------------------------------------------------

def kmeans_recolor_image(img, palette, n_colors=12):
    """
    Apply a colorblind-safe palette to an image using K-Means clustering.
    The image colors are grouped into clusters; each cluster is replaced
    with the appropriate palette color if it matches a known category.

    Args:
        img: PIL.Image object
        palette: dict of color mappings for this colorblind mode
        n_colors: number of K-Means clusters to use

    Returns:
        A recolored PIL.Image object in RGBA format.
    """
    img = img.convert("RGBA")
    arr = np.array(img)
    pixels = arr.reshape(-1, 4)

    # Cluster RGB channels only
    rgb_pixels = pixels[:, :3].astype(np.float32)

    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    labels = kmeans.fit_predict(rgb_pixels)
    centers = kmeans.cluster_centers_

    # Map cluster centers to colorblind-safe palette
    recolored_centers = []
    for c in centers:
        category = classify_color(c)
        if category and category in palette:
            recolored_centers.append(palette[category])
        else:
            recolored_centers.append(tuple(map(int, c)))  # preserve original

    # Replace pixels by their recolored cluster center
    recolored_pixels = np.array(
        [recolored_centers[label] for label in labels], dtype=np.uint8
    )

    # Restore alpha channel
    result = np.concatenate([recolored_pixels, pixels[:, 3:4]], axis=1)
    recolored_arr = result.reshape(arr.shape)

    return Image.fromarray(recolored_arr, "RGBA")


# -----------------------------------------------------------
# Icon Outlining (Used for Dark Mode)
# -----------------------------------------------------------

def add_white_outline(img, thickness=3, outline_color=(255, 255, 255)):
    """
    Adds a white outline around non-transparent portions of the icon.

    Args:
        img: PIL.Image object
        thickness: outline thickness in pixels
        outline_color: tuple RGB color for outline

    Returns:
        A PIL.Image with outline applied behind the original icon.
    """
    img = img.convert("RGBA")

    # Extract alpha channel to identify icon shape
    alpha = img.split()[3]

    # Expand alpha to create outline region
    outline_mask = alpha.filter(ImageFilter.MaxFilter(size=thickness * 2 + 1))

    # Prepare outline layer
    outline = Image.new("RGBA", img.size, outline_color + (0,))
    outline.putalpha(outline_mask)

    # Only outline outer edges (avoid painting over icon interior)
    transparent_region = ImageOps.invert(alpha)
    outline.putalpha(
        Image.composite(outline_mask, Image.new("L", img.size, 0), transparent_region)
    )

    # Place outline behind original image
    return Image.alpha_composite(outline, img)


# -----------------------------------------------------------
# File Processing Logic
# -----------------------------------------------------------

def apply_color_scheme(input_path, output_path, theme, palette, outline_color=None):
    """
    Apply a colorblind-mode palette to an image file and save the result.

    Args:
        input_path: path to source icon
        output_path: directory for output
        theme: colorblind mode name
        palette: palette dict mapping color categories to RGB values
    """
    img = Image.open(input_path)
    img_transformed = kmeans_recolor_image(img, palette)

    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, os.path.basename(input_path))
    img_transformed.save(output_file)


def process_files(files, output_dir):
    """
    Processes the selected list of icon files:
        - Exports light and dark theme variants
        - Generates colorblind-friendly versions

    Args:
        files: List of input file paths
        output_dir: Root output directory
    """
    for input_file in files:

        # -------------------------
        # Light/Dark Theme Processing
        # -------------------------
        for theme, outline_color in ICON_COLORS.items():
            output_path = os.path.join(output_dir, theme)
            os.makedirs(output_path, exist_ok=True)

            img = Image.open(input_file).convert("RGBA")

            if theme == "dark":
                # Dark mode: apply white outline
                outlined = add_white_outline(
                    img, thickness=3, outline_color=(255, 255, 255)
                )
                outlined.save(os.path.join(output_path, os.path.basename(input_file)))
            else:
                # Light mode: preserve original image
                img.save(os.path.join(output_path, os.path.basename(input_file)))

        # -------------------------
        # Colorblind-Friendly Versions
        # -------------------------
        for theme, palette in COLORBLIND_PALETTES.items():
            output_path = os.path.join(output_dir, theme)
            apply_color_scheme(input_file, output_path, theme, palette)


# -----------------------------------------------------------
# UI (Tkinter Interface)
# -----------------------------------------------------------

def browse_files(selected_files_listbox):
    """Opens a file dialog and adds selected image paths to the UI listbox."""
    files = filedialog.askopenfilenames(
        title="Select Icons",
        filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")]
    )

    if files:
        selected_files_listbox.delete(0, tk.END)
        for file in files:
            selected_files_listbox.insert(tk.END, file)


def select_output_folder(output_folder_label):
    """Prompts user for an output folder and updates UI label."""
    output_dir = filedialog.askdirectory(title="Select Output Folder")
    if output_dir:
        output_folder_label.config(text=f"Output folder: {output_dir}")
    return output_dir


# -----------------------------------------------------------
# Main UI Application
# -----------------------------------------------------------

def main():
    """Launches the Tkinter GUI application."""
    root = tk.Tk()
    root.title("Colorblind-Friendly Icon Processor (K-Means Version)")
    root.geometry("600x500")

    selected_output_folder = None

    # Selected file list UI
    selected_files_listbox = tk.Listbox(root, height=10, width=80)
    selected_files_listbox.pack(pady=10)

    output_folder_label = tk.Label(root, text="No output folder selected")
    output_folder_label.pack(pady=10)

    def browse_output_folder():
        nonlocal selected_output_folder
        selected_output_folder = select_output_folder(output_folder_label)

    def process():
        """Runs the full processing pipeline."""
        if not selected_files_listbox.size() or selected_output_folder is None:
            messagebox.showwarning(
                "Missing Information",
                "Please select both files and output folder.",
            )
            return

        files = selected_files_listbox.get(0, tk.END)
        process_files(files, selected_output_folder)
        messagebox.showinfo("Processing Complete", "Files processed successfully.")

    # UI Controls
    tk.Button(root, text="Select Files",
              command=lambda: browse_files(selected_files_listbox)).pack(pady=10)

    tk.Button(root, text="Select Output Folder",
              command=browse_output_folder).pack(pady=10)

    tk.Button(root, text="Process Files",
              command=process).pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()