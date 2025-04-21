from reveal import reveal
import webbrowser
import pandas as pd


class RevealSite:

    themes = [
        "black",
        "white",
        "league",
        "beige",
        "night",
        "serif",
        "simple",
        "solarized",
        "moon",
        "dracula",
        "sky",
        "blood",

    ]

    def __init__(self, df, name, reveal_path=None):
        """
        :param df: A [nrows, ncolumns] Pandas DataFrame of dicts, where each dict represents a slide.
        The dictionaries have two required keys: "image_path" and "title".
        To implement a straight dictionary use the following dictionary:
            {
            "image_path": full_path_to_image,
            "title": "title",
            "post": "some text to appear below the image",  # optional
            "image_name": "unique_image_name.jpg"  # optional, to avoid conflicts if several images bear the same name
            }
        To implement a slider comparison for two images you can add the following keys:
            {
            ...
            "image_path_compare": full_path_to_image_2,
            "image_name_compare": "unique_image_name2.jpg"  # optional, to avoid conflicts if several images bear the same name
            }
        :param name: The name of the site.
        :param reveal_path: Local path to the Revealjs files.
        """
        self.df = pd.DataFrame(df)
        self.name = name
        self.reveal_path = reveal.REVEAL_PATH if reveal_path is None else reveal_path
        self.prez = reveal.Presentation(self.name, self.reveal_path)

    def build(self, theme="white"):
        """
        Construct presentation locally. The webpage will appear in the
        `reveal_path` as "`self.name`.html"
        """
        if theme not in self.themes:
            raise ValueError(f"{theme} is not a revealJS theme! Use one of {str(self.themes)}")
        for column_idx, col in enumerate(self.df):
            self.prez.new_section()
            for idx, slide in self.df[col].items():
                if isinstance(slide, dict):
                    if "image_path_compare" in slide:
                        self.prez.add_slide_compare(
                            full_path_image1=slide["image_path"],
                            full_path_image2=slide["image_path_compare"],
                            image_name1=slide.get('image_name', None),
                            image_name2=slide.get('image_name_compare', None),
                            title=slide["title"],
                            post=slide.get('post', ''),
                            column_idx=column_idx,
                        )
                    else:
                        self.prez.add_slide_image(
                            full_path_image=slide["image_path"],
                            image_name=slide.get('image_name', None),
                            title=slide["title"],
                            post=slide.get('post', ''),
                            column_idx=column_idx,
                        )
            self.prez.close_section()
        self.prez.build(theme=theme)

    def open(self):
        """
        Open the site locally in web browser.
        """
        webbrowser.open(f"file://{self.reveal_path}/{self.name}.html")

    def publish(self, page_name=None, profile=None):
        """
        Publish the site to IBL reveal on AWS.
        Requires AWS CLI access.

        :param page_name: Name of webpage on IBL reveal to publish to. 
            Defaults to self.name
        """
        import subprocess

        if page_name is None:
            page_name = self.name
        command1 = ['aws', 's3', 'cp', f"{self.reveal_path}/{self.name}.html",
                    f"s3://reveal.internationalbrainlab.org/{page_name}.html"]
        command2 = ['aws', 's3', 'sync', f"{self.reveal_path}/images/{self.name}/",
                    f"s3://reveal.internationalbrainlab.org/images/{self.name}/"]
        if profile is not None:
            command1.extend(['--profile', profile])
            command2.extend(['--profile', profile])
        print(' '.join(command1))
        print(' '.join(command2))
        subprocess.run(command1)
        subprocess.run(command2)
        print(f"Published at: http://reveal.internationalbrainlab.org.s3-website-us-east-1.amazonaws.com/{page_name}.html")
