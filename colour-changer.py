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
from tkinter import ttk
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

def apply_color_scheme(input_path, output_path, palette):
    """
    Apply a colorblind-mode palette to an image file and save the result.

    Args:
        input_path: path to source icon
        output_path: directory for output
        palette: palette dict mapping color categories to RGB values
    """
    img = Image.open(input_path)
    img_transformed = kmeans_recolor_image(img, palette)

    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, os.path.basename(input_path))
    img_transformed.save(output_file)


def process_files(files, output_dir, export_options, progress_callback=None):
    """
    Processes the selected icon files and generates the requested exports.

    Args:
        files: List of source PNG file paths
        output_dir: Root output directory
        export_options: Dict indicating which variants to generate
        progress_callback: Optional callback receiving (current_file, total_files) progress updates
    """
    total = len(files)

    for index, input_file in enumerate(files):

        # -------------------------
        # Light/Dark Theme Processing
        # -------------------------
        if export_options.get("light"):
            output_path = os.path.join(output_dir, "light")
            os.makedirs(output_path, exist_ok=True)

            img = Image.open(input_file).convert("RGBA")
            img.save(os.path.join(output_path, os.path.basename(input_file)))

        if export_options.get("dark"):
            output_path = os.path.join(output_dir, "dark")
            os.makedirs(output_path, exist_ok=True)

            img = Image.open(input_file).convert("RGBA")

            outlined = add_white_outline(
                img,
                thickness=3,
                outline_color=(255, 255, 255)
            )

            outlined.save(os.path.join(output_path, os.path.basename(input_file)))

        # -------------------------
        # Colorblind-Friendly Versions
        # -------------------------
        for mode, palette in COLORBLIND_PALETTES.items():

            if not export_options.get(mode, False):
                continue

            output_path = os.path.join(output_dir, mode)

            apply_color_scheme(
                input_file,
                output_path,
                palette
            )

        # Update UI progress after processing each file
        if progress_callback:
            progress_callback(index + 1, total)


def shorten_path(path, max_length=55):
    """Shortens long filesystem paths for display labels."""
    if len(path) <= max_length:
        return path

    return "..." + path[-(max_length - 3):]


def show_selected_files(parent, files):
    """Display a window containing the selected file paths."""
    window = tk.Toplevel(parent)
    window.title("Selected Files")
    window.geometry("700x400")

    # Create a popup window for viewing selected files
    frame = ttk.Frame(window, padding=10)
    frame.pack(fill="both", expand=True)

    listbox = tk.Listbox(
        frame,
        font=("Consolas", 10)
    )
    listbox.pack(fill="both", expand=True)

    # Populate list with all selected file paths
    for file in files:
        listbox.insert(tk.END, file)


# -----------------------------------------------------------
# Main UI Application
# -----------------------------------------------------------

def main():
    """Launches the Tkinter GUI application."""
    root = tk.Tk()
    root.title("Colorblind-Friendly Icon Processor")
    root.geometry("760x640")
    root.minsize(700, 640)

    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Title.TLabel",
        font=("Segoe UI", 20, "bold")
    )

    style.configure(
        "Subtitle.TLabel",
        foreground="#666666",
        font=("Segoe UI", 9)
    )

    style.configure(
        "Process.TButton",
        font=("Segoe UI", 10, "bold"),
        padding=10
    )

    selected_files = []
    selected_output_folder = None

    status_var = tk.StringVar(value="Ready")
    file_count_var = tk.StringVar(value="No files selected")
    output_var = tk.StringVar(value="No output folder selected")

    main = ttk.Frame(root, padding=20)
    main.pack(fill="both", expand=True)

    # --------------------------------------------------
    # Header
    # --------------------------------------------------

    ttk.Label(
        main,
        text="Colorblind-Friendly Icon Processor",
        style="Title.TLabel"
    ).pack(anchor="w")

    ttk.Label(
        main,
        text="Generate light, dark and accessibility-focused icon variants.",
        style="Subtitle.TLabel"
    ).pack(anchor="w", pady=(0, 20))

    # --------------------------------------------------
    # Files
    # --------------------------------------------------

    files_frame = ttk.LabelFrame(
        main,
        text="Files",
        padding=12
    )
    files_frame.pack(fill="x", pady=(0, 10))

    ttk.Label(
        files_frame,
        textvariable=file_count_var
    ).pack(anchor="w")

    file_button_frame = ttk.Frame(files_frame)
    file_button_frame.pack(anchor="w", pady=(8, 0))

    def browse_files():

        nonlocal selected_files

        files = filedialog.askopenfilenames(
            title="Select PNG Files",
            filetypes=[
                ("PNG Files", "*.png"),
                ("All Files", "*.*")
            ]
        )

        if not files:
            return

        selected_files = list(files)

        file_count_var.set(
            f"{len(selected_files)} file(s) selected"
        )

    ttk.Button(
        file_button_frame,
        text="Add Files",
        command=browse_files
    ).pack(side="left", padx=(0, 8))

    ttk.Button(
        file_button_frame,
        text="View Files",
        command=lambda: show_selected_files(
            root,
            selected_files
        )
    ).pack(side="left")

    # --------------------------------------------------
    # Output Folder
    # --------------------------------------------------

    output_frame = ttk.LabelFrame(
        main,
        text="Output Folder",
        padding=12
    )
    output_frame.pack(fill="x", pady=(0, 10))

    ttk.Label(
        output_frame,
        textvariable=output_var
    ).pack(anchor="w")

    def browse_output_folder():

        nonlocal selected_output_folder

        folder = filedialog.askdirectory(
            title="Select Output Folder"
        )

        if not folder:
            return

        selected_output_folder = folder

        output_var.set(
            shorten_path(folder)
        )

    ttk.Button(
        output_frame,
        text="Choose Folder",
        command=browse_output_folder
    ).pack(anchor="w", pady=(8, 0))

    # --------------------------------------------------
    # Variants
    # --------------------------------------------------

    options_frame = ttk.LabelFrame(
        main,
        text="Variants",
        padding=12
    )
    options_frame.pack(fill="x", pady=(0, 15))

    light_var = tk.BooleanVar(value=True)
    dark_var = tk.BooleanVar(value=True)

    deut_var = tk.BooleanVar(value=True)
    prot_var = tk.BooleanVar(value=True)
    trit_var = tk.BooleanVar(value=True)

    ttk.Checkbutton(
        options_frame,
        text="Light",
        variable=light_var
    ).grid(row=0, column=0, sticky="w")

    ttk.Checkbutton(
        options_frame,
        text="Dark",
        variable=dark_var
    ).grid(row=0, column=1, sticky="w")

    ttk.Checkbutton(
        options_frame,
        text="Deuteranopia",
        variable=deut_var
    ).grid(row=1, column=0, sticky="w")

    ttk.Checkbutton(
        options_frame,
        text="Protanopia",
        variable=prot_var
    ).grid(row=1, column=1, sticky="w")

    ttk.Checkbutton(
        options_frame,
        text="Tritanopia",
        variable=trit_var
    ).grid(row=2, column=0, sticky="w")

    # --------------------------------------------------
    # Progress
    # --------------------------------------------------

    progress = ttk.Progressbar(
        main,
        mode="determinate"
    )

    progress.pack(
        fill="x",
        pady=(0, 15)
    )

    # --------------------------------------------------
    # Process
    # --------------------------------------------------

    def process():

        if not selected_files:
            messagebox.showwarning(
                "Missing Files",
                "Please select at least one PNG file."
            )
            return

        if not selected_output_folder:
            messagebox.showwarning(
                "Missing Output Folder",
                "Please select an output folder."
            )
            return

        export_options = {
            "light": light_var.get(),
            "dark": dark_var.get(),
            "deuteranopia": deut_var.get(),
            "protanopia": prot_var.get(),
            "tritanopia": trit_var.get(),
        }

        progress["value"] = 0
        progress["maximum"] = len(selected_files)

        def update_progress(current, total):

            progress["value"] = current

            status_var.set(
                f"Processing {current}/{total}"
            )

            root.update_idletasks()

        try:

            if not any(export_options.values()):
                messagebox.showwarning(
                    "No Variants Selected",
                    "Please select at least one output variant."
                )
                return

            process_files(
                selected_files,
                selected_output_folder,
                export_options,
                update_progress
            )

            status_var.set("Completed")

            enabled = [
                name
                for name, enabled in export_options.items()
                if enabled
            ]

            messagebox.showinfo(
                "Completed",
                f"Files processed: {len(selected_files)}\n\n"
                f"Generated:\n"
                + "\n".join(f"- {x}" for x in enabled)
                + f"\n\nOutput:\n{selected_output_folder}"
            )

        except Exception as e:

            status_var.set("Error")

            messagebox.showerror(
                "Processing Error",
                str(e)
            )

    ttk.Button(
        main,
        text="Process Icons",
        style="Process.TButton",
        command=process
    ).pack(
        pady=(0, 10),
        ipadx=30
    )

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    status = ttk.Label(
        root,
        textvariable=status_var,
        relief="sunken",
        anchor="w"
    )

    status.pack(
        side="bottom",
        fill="x"
    )

    root.mainloop()


if __name__ == "__main__":
    main()
