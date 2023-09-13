import sys
sys.path.append("/home/ibladmin/Documents/PYTHON/int-brain-lab/ibldevtools/olivier/modules")
from pathlib import Path
from PIL import Image
import reveal
from one.api import ONE
import reproducible_ephys_functions
from iblatlas.regions import BrainRegions

REVEAL_PATH = Path.home().joinpath('Documents/JS/reproducible')
BWM_DIR = Path("/mnt/s1/bwm")
regions = BrainRegions()
path_qc = Path("/mnt/s1/bwm")
one = ONE(base_url="https://alyx.internationalbrainlab.org")

insertions = reproducible_ephys_functions.query(one=one)
pids = [i['probe_insertion'] for i in insertions]
pids.sort()
print(len(pids))

pids += [
'0132a739-be48-494a-a722-c4299b266d29', # - CRIICAL  - no spike sorting
'098b405f-0e30-4952-85db-61cc62e5a9fd', #- no tracing, potential
'143cff36-30b4-4b25-9d26-5a2dbe6f6fc2', #- CRITICAL
'17d9710a-f292-4226-b033-687d54b6545a', #- not resolved, potential
'22212d26-a167-45fb-9963-35ecd003e8a2',
'3443eceb-50b3-450e-b7c1-fc465a3bc84f', #- CRITICAL  - no spike sortings
'3bc030ba-c070-4443-a981-54ea9896b7a1', #- not resolved, potential
'553f8d56-b6e7-46bd-a146-ac43b8ec6de7', #- CRITICAL
'6bfa4a99-bdfa-4e44-aa01-9c7eac7e253d', #- CRITICAL
'6d9b6393-6729-4a15-ad08-c6838842a074', #- no tracing, potential
'99b8eb91-393d-4ed1-913e-ce5ee2e31bc3',
'ad1a1cc5-ecf4-460c-9d2f-dad2dcd4a4f8', #- no tracing, potential
'dc6eea9b-a8fb-4151-b298-718f321e6968', #- CRITICAL
'e7abb87f-4324-4c89-8a46-97ed4b40577e', #- CRITICAL
'f68d9f26-ac40-4c67-9cbf-9ad1851292f7',# - no tracing, potential
'fc626c12-bd1e-45c3-9434-4a7a8c81d7c0', #- CRITICAL
]
pids = list(set(pids))
pids.sort()
print(len(pids))

path_qc_rawdata = Path(path_qc.joinpath('qc_rawdata'))
path_qc_raster = Path(path_qc.joinpath('qc_raster'))

IMIN = 0
eqcs = {}
for i, pid in enumerate(pids):
    if i < IMIN:
        continue
    try:
        reveal.make_raster_plot(path_qc_raster, pid, one=one, regions=regions, clobber=False)
        reveal.make_rawdata_plot(path_qc_rawdata, pid, one=one, regions=regions, clobber=False)
    except Exception:
        print(pid, 'uncaught error')




def slide(pid, *args, **kwargs):
    post = pid
    return reveal.slide_image(*args, **kwargs, post=post)

def slide_compare(pid, *args, **kwargs):
    post = pid
    return reveal.slide_compare_images(*args, **kwargs, post=post)

## %%
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
                jpg_image.unlink()
            pimg = Image.open(im)
            pimg.convert('RGB').save(jpg_image)

        f.write(f"<section>\n")
        f.write(slide(pid, img_name=images['raster'], title=f'{pid[:8]} raster'))
        f.write(slide(pid, img_name=images['raster_good'], title=f'{pid[:8]} raster good'))
        f.write(slide_compare(pid, img_name1=images['raw_butter1'], img_name2=images['raw_destripe1'], title=f'{pid[:8]} raw 600s',))
        f.write(slide_compare(pid, img_name1=images['raw_butter2'], img_name2=images['raw_destripe2'], title=f'{pid[:8]} raw 1800s'))
        f.write(slide_compare(pid, img_name1=images['raw_butter3'], img_name2=images['raw_destripe3'], title=f'{pid[:8]} raw 3000s'))
        f.write(f"</section>\n")

reveal.build(reveal_path=REVEAL_PATH, title='Reproducible', theme='solarized')
print("aws --profile ibl s3 sync ~/Documents/JS/reproducible s3://reproducible.internationalbrainlab.org --exclude reproducible.js/node_modules")
