from pathlib import Path
import logging

from PIL import Image

logger = logging.getLogger(__name__)
REVEAL_PATH = Path.home().joinpath('Documents/JS/reveal.js')


class Presentation(object):
    """
    prez = Presentation(name='prez')
    """
    def __init__(self, name, path_reveal=REVEAL_PATH):
        self.name = name  # this is the name of the presentation
        self.list_buffer = []
        self.path_reveal = path_reveal
        self.path_images = Path(path_reveal).joinpath('images', name)
        self.path_images.mkdir(parents=True, exist_ok=True)

    def _convert_image(self, full_path_image, image_name=None, clobber=True):
        """
        :param full_path_image:
        :param clobber:
        :return:
        """
        image_name = image_name or Path(full_path_image).name
        jpg_image = Path(self.path_images).joinpath(image_name).with_suffix('.jpg')
        if clobber or not jpg_image.exists():
            pimg = Image.open(full_path_image)
            pimg.convert('RGB').save(jpg_image)
        return jpg_image.name

    def new_section(self):
        self.list_buffer.append("<section>\n")

    def close_section(self):
        self.list_buffer.append("</section>\n")

    def add_slide(self, **kwargs):
        # if 2 pictures, add slide compare, if one, add slide
        # TODO
        pass

    def add_slide_image(self, full_path_image, title=None, post='', image_name=None):
        img_name = self._convert_image(full_path_image, image_name=image_name)
        if title is None:
            title = img_name
        str_slide = f"""
        <section>
            <p>{title}</p>
            <img data-src=images/{self.name}/{img_name}>
            <p>{post}</p>
        </section>
        """
        self.list_buffer.append(str_slide)

    def add_slide_compare(self, full_path_image1, full_path_image2, title=None, post='', image_name1=None, image_name2=None):
        img_name1 = self._convert_image(full_path_image1, image_name1)
        img_name2 = self._convert_image(full_path_image2, image_name1)
        if title is None:
            title = img_name1
        str_slide = f"""
        <section>
            <p>{title}</p>
            <div class="r-stack"><div class="compare">
                <img data-src=images/{self.name}/{img_name1}>
                <img data-src=images/{self.name}/{img_name2}>
            </div></div>
        {post}</section>
        """
        self.list_buffer.append(str_slide)

    def build(self, theme='white', title=None):
        """Build reveal.js index.html file"""
        file_index_template = self.path_reveal.joinpath('index_template.html')
        file_presentation = self.path_reveal.joinpath(f'{self.name}.html')

        title = title or self.name
        with open(file_index_template, 'r') as f:
            template = f.read()

        html = template.replace("{% theme %}", theme)
        html = html.replace("{% title %}", title)
        html = html.replace("{% slides %}", ''.join(self.list_buffer))

        with open(file_presentation, 'w+') as f:
            f.write(html)
