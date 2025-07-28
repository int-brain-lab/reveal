"""
Getting Started with Reveal Site

This script demonstrates how to create a simple slide deck using the RevealSite API.
It generates a 2x3 grid of slides, each containing an image with text indicating its row and column position.
Each slide has two versions - one with black text and one with red text - that can be compared using a slider.

The script:
1. Creates a directory structure for the slide deck
2. Generates images with text for each slide
3. Builds a slide deck configuration
4. Renders the slide deck using RevealSite
5. Opens the slide deck in a web browser

Requirements:
- PIL (Python Imaging Library)
- numpy
- reveal (custom library for slide deck generation)

Usage:
Run this script to generate and view a sample slide deck.
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
nr, nc = (2, 3)  # Define grid dimensions: 2 rows, 3 columns

# This is the directory from which the website will be served
project_path = Path.home().joinpath('Documents', 'JS', 'slide_deck_tutorial')


def make_image(txt, fill=(0, 0, 0), img_file=None):
    """
    Create an image with text for demonstration purposes.
    
    Parameters:
    -----------
    txt : str
        The text to display on the image
    fill : tuple
        RGB color tuple for the text (default: black)
    img_file : Path or str, optional
        Path where the image should be saved. If None, the image is not saved.
        
    Returns:
    --------
    PIL.Image
        The generated image object
    """
    out = Image.new("RGB", (450, 300), (255, 255, 255))  # Create a white image
    d = ImageDraw.Draw(out)  # Create a drawing context
    d.multiline_text((200, 150), txt, fill=fill)  # Draw text on the image
    if img_file is not None:
        with open(img_file, 'wb') as fp:
            out.save(fp, format='png')  # Save the image if a file path is provided
    return out


# Create a 2D array to hold slide information, ech cell of this array is a dictionary containing slide configuration
deck = np.zeros((nr, nc), dtype=object)

# Generate slides for each position in the grid
for i in range(nr):
    for j in range(nc):
        # Create two versions of each image: one with black text and one with red text
        img_black = project_path / f'slide_{i}_{j}_black.png'
        img_red = project_path / f'slide_{i}_{j}_red.png'
        make_image(f"row {i} \n column {j}", img_file=img_black)
        make_image(f"row {i} \n column {j}", fill=(255, 0, 0), img_file=img_red)
        
        # Create a dictionary with slide configuration
        deck[i, j] = {
            "image_path": img_black,  # Path to the main image (black text)
            "title": f"row {i} \n column {j}",  # Slide title
            "post": "slide to change text colour",  # Caption below the figure
            "image_path_compare": img_red,  # Path to the comparison image (red text)
            }

# Create and build the slide deck using RevealSite
from reveal.api import RevealSite
site = RevealSite(deck, name='tutorial', reveal_path=project_path)
site.build(theme='serif')  # Build the slide deck with the 'serif' theme
site.open()  # Open the slide deck in a web browser
