from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
nr, nc = (2, 3)

project_path = Path.home() / 'Documents/JS/slide_deck_tutorial'


def make_image(txt, fill=(0, 0, 0), img_file=None):
    """
    Create an image with text
    """
    out = Image.new("RGB", (450, 300), (255, 255, 255))
    d = ImageDraw.Draw(out)
    d.multiline_text((200, 150), txt, fill=fill)
    if img_file is not None:
        with open(img_file, 'wb') as fp:
            out.save(fp, format='png')


deck = np.zeros((nr, nc), dtype=object)
for i in range(nr):
    for j in range(nc):
        # first create an image with text relative to columns and rows on them
        img_black = project_path / f'slide_{i}_{j}_black.png'
        img_red = project_path / f'slide_{i}_{j}_red.png'
        make_image(f"row {i} \n column {j}", img_file=img_black)
        make_image(f"row {i} \n column {j}", fill=(255, 0, 0), img_file=img_red)
        # then we create the dictionary for each item of the slide deck
        deck[i, j] = {
            "image_path": img_black,  # full path to the image
            "title": f"row {i} \n column {j}",  # a slide title that will display on top of the slide
            "post": "slide to change text colour",  # optional: caption below the figure
            "image_path_compare": img_red,  # optional, if this is set, a comparison slider will be created
            }

# %%
from reveal.api import RevealSite
site = RevealSite(deck, name='tutorial', reveal_path=project_path)
site.build(theme='serif')
site.open()
