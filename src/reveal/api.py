from reveal import reveal
import pandas as pd
from pathlib import Path

class RevealSite:

    def __init__(self, df, name, reveal_path = None):
        self.df = df
        self.name = name
        if not reveal_path:
            self.reveal_path = reveal.REVEAL_PATH

        self.prez = reveal.Presentation(self.name, self.reveal_path)

        


    def build(self):
        for col in self.df:
            self.prez.new_section()
            for idx, slide in self.df[col].items():
                assert isinstance(slide, dict)
                image_path = slide["image_path"]
                title = slide["title"]
                if "image_path_compare" in slide:
                    image_path_cmp = slide["image_path_compare"]
                    self.prez.add_slide_compare(full_path_image1=image_path,
                                                full_path_image2=image_path_cmp,
                                                title=title)
                else:
                    self.prez.add_slide_image(full_path_image=image_path,
                                              title=title)
            self.prez.close_section()

        self.prez.build()


    def publish(self):
        pass
