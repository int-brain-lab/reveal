from pathlib import Path
import pandas as pd
from PIL import Image
import pandas as pd
import reveal

# ROOT_PATH = Path("/mnt/s1/ephys-atlas")
REVEAL_PATH = Path.home().joinpath('Documents/JS/benchmarks')
BWM_DIR = Path("/mnt/s1/bwm")
pids = [
    '1a276285-8b0e-4cc9-9f0a-a3a002978724',
    '1e104bf4-7a24-4624-a5b2-c2c8289c0de7',
    '5d570bf6-a4c6-4bf1-a14b-2c878c84ef0e',
    '5f7766ce-8e2e-410c-9195-6bf089fea4fd',
    '6638cfb3-3831-4fc2-9327-194b76cf22e1',
    '749cb2b7-e57e-4453-a794-f6230e4d0226',
    'd7ec0892-0a6c-4f4f-9d8f-72083692af5c',
    'da8dfec1-d265-44e8-84ce-6ae9c109b8bd',
    'dab512bd-a02d-4c1f-8dbc-9155a163efc0',
    'dc7e9403-19f7-409f-9240-05ee57cb7aea',
    'e8f9fba4-d151-4b00-bee7-447f0f3e752c',
    'eebcaf65-7fa4-4118-869d-a084e84530e2',
    'fe380793-8035-414e-b000-09bfe5ece92a',
]


def slide(pid, *args, **kwargs):
    post = pid
    return reveal.slide_image(*args, **kwargs, post=post)

def slide_compare(pid, *args, **kwargs):
    post = pid
    return reveal.slide_compare_images(*args, **kwargs, post=post)


images = ['raster', 'raster_good_units']
file_slides = REVEAL_PATH.joinpath('slides.html')
import tqdm
with open(file_slides, 'w+') as f:
    c = 0
    for i, pid in enumerate(pids):
        c += 1
        imfiles = {}
        missing = False
        images_source = {}
        images_source['raster'] = next(BWM_DIR.joinpath("qc_raster").glob(f"{pid}*_raster.png"), Path('not_found.png'))
        images_source['raster_good'] = next(BWM_DIR.joinpath("qc_raster").glob(f"{pid}*_raster_good_units.png"), Path('not_found.png'))
        images_source['raw_butter1'] = next(BWM_DIR.joinpath("qc_rawdata").glob(f"{pid}*_raw_T0600.png"), Path('not_found.png'))
        images_source['raw_destripe1'] = next(BWM_DIR.joinpath("qc_rawdata").glob(f"{pid}*_destripe_T0600.png"), Path('not_found.png'))
        images_source['raw_butter2'] = next(BWM_DIR.joinpath("qc_rawdata").glob(f"{pid}*_raw_T1800.png"), Path('not_found.png'))
        images_source['raw_destripe2'] = next(BWM_DIR.joinpath("qc_rawdata").glob(f"{pid}*_destripe_T1800.png"), Path('not_found.png'))
        images_source['raw_butter3'] = next(BWM_DIR.joinpath("qc_rawdata").glob(f"{pid}*_raw_T3000.png"), Path('not_found.png'))
        images_source['raw_destripe3'] = next(BWM_DIR.joinpath("qc_rawdata").glob(f"{pid}*_destripe_T3000.png"), Path('not_found.png'))
        images = {}
        for kim, im in images_source.items():
            jpg_image = REVEAL_PATH.joinpath('img').joinpath(im.name).with_suffix('.jpg')
            images[kim] = jpg_image.name
            if im == Path('not_found.png'):
                continue
            # REVEAL_PATH.joinpath('img').joinpath(im.name).symlink_to(im)

            if jpg_image.exists():
                continue
            pimg = Image.open(im)
            pimg.convert('RGB').save(jpg_image)



        f.write(f"<section>\n")
        f.write(slide(pid, img_name=images['raster'], title=f'{pid[:8]} raster'))
        f.write(slide(pid, img_name=images['raster_good'], title=f'{pid[:8]} raster good'))
        f.write(slide_compare(pid, img_name1=images['raw_butter1'], img_name2=images['raw_destripe1'], title=f'{pid[:8]} raw 600s',))
        f.write(slide_compare(pid, img_name1=images['raw_butter2'], img_name2=images['raw_destripe2'], title=f'{pid[:8]} raw 1800s'))
        f.write(slide_compare(pid, img_name1=images['raw_butter3'], img_name2=images['raw_destripe3'], title=f'{pid[:8]} raw 3000s'))
        f.write(f"</section>\n")

reveal.build(reveal_path=REVEAL_PATH, title='Benchmarks', theme='moon')
