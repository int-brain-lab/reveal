from reveal import reveal
import pandas as pd
from pathlib import Path
import os
import webbrowser

class RevealSite:

    def __init__(self, df, name, reveal_path = None):
        """
        :param df: A Pandas DataFrame of dicts. Each dict must contain
            a "image_path" field and a "title" field. Optionally, each dict
            may specify an "image_path_compare" field to create a comparison 
            slide.
        :param name: The name of the site.
        :param reveal_path: Local path to the Revealjs files.
        """
        self.df = df
        self.name = name
        if not reveal_path:
            self.reveal_path = reveal.REVEAL_PATH

        self.prez = reveal.Presentation(self.name, self.reveal_path)

    def build(self):
        """
        Construct presentation locally. The webpage will appear in the
        `reveal_path` as "`self.name`.html"
        """
        for col in self.df:
            self.prez.new_section()
            for idx, slide in self.df[col].items():
                if isinstance(slide, dict):
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

    def open(self):
        """
        Open the site locally in web browser.
        """
        webbrowser.open(f"file://{self.reveal_path}/{self.name}.html")

    def publish(self, page_name=None):
        """
        Publish the site to IBL reveal on AWS.
        Requires AWS CLI access.

        :param page_name: Name of webpage on IBL reveal to publish to. 
            Defaults to self.name
        """
        if page_name is None:
            page_name = self.name
        os.system(f"aws s3 cp {self.reveal_path}/{self.name}.html s3://reveal.internationalbrainlab.org/{page_name}.html ")
        os.system(f"aws s3 sync {self.reveal_path}/images/{self.name}/ s3://reveal.internationalbrainlab.org/images/{self.name}/")



