from pathlib import Path
import shutil


folder_old_buckets = Path("/home/olivier/Documents/JS/old_buckets")
folder_reveal_repo = Path("/home/olivier/Documents/JS/reveal.js")
tag_names = {
    'chronic.internationalbrainlab.org': '2023-01-24-chronic-max',
    'reproducible.internationalbrainlab.org': 'reproducible',
    'reveal.internationalbrainlab.org': 'bwm',
    'critical.internationalbrainlab.org': 'critical',
    'benchmarks.internationalbrainlab.org': 'benchmarks',
}


with open(folder_reveal_repo.joinpath('index.html'), 'w+') as fp:
    for bucket in folder_old_buckets.iterdir():
        title = tag_names[bucket.name]
        print(bucket.name, title)
        fp.write(f"<p><a href=\"{title}.html\">{title}</a></p>")

        # shutil.copy(folder_reveal_repo.joinpath('index_template.html'), folder_reveal_repo.joinpath(f"{title}.html"))
        file_webpage = folder_reveal_repo.joinpath(f"{title}.html")
        folder_image = folder_reveal_repo.joinpath('images', title)
        folder_image.mkdir(exist_ok=True, parents=True)
        # shutil.copytree(bucket.joinpath('img'), folder_image, dirs_exist_ok=True)
        shutil.copy(bucket.joinpath('index.html'), file_webpage)

        with open(file_webpage, 'r') as ffp:
            html_slides = ffp.read()

        html_slides = html_slides.replace("data-src=img/", f"data-src=images/{title}/")
        with open(file_webpage, 'w+') as ffp:
            ffp.write(html_slides)
