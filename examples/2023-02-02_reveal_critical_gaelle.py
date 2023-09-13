from pathlib import Path
from one.api import ONE
from iblatlas.regions import BrainRegions
import reveal
one = ONE()
br = BrainRegions()

FOLDER_DATA = Path("/datadisk/Data/reveal/critical")
REVEAL_PATH = Path.home().joinpath('Documents/NODEJS/ks_rerun')


# from reproducible_ephys_functions import query
#
# allIns = query(behavior=False, n_trials=0, resolved=False, min_regions=0, exclude_critical=False, one=one)
# nonCrit = query(behavior=False, n_trials=0, resolved=False, min_regions=0, exclude_critical=True, one=one)
#
# crit = [x for x in allIns if x not in nonCrit]
# crit_pids = [crit[i]['probe_insertion'] for i in range(len(crit))]
#

pids = [
    '44fc10b1-ec82-4f88-afbf-10a6f8a1b5d8',
    '80624507-4be6-4689-92df-0e2c26c3faf3',
    'f8d0ecdc-b7bd-44cc-b887-3d544e24e561',
    'ef3d059a-59d5-4870-b355-563a8d7cfd2d',
    '0132a739-be48-494a-a722-c4299b266d29',
    '79bcfe47-33ed-4432-a598-66006b4cde56',
    'dc6eea9b-a8fb-4151-b298-718f321e6968',
    'fc626c12-bd1e-45c3-9434-4a7a8c81d7c0',
    '72f89097-4836-4b67-a47a-edb3285a6e83',
    'ef03e569-2b50-4534-89f4-fb1e56e81461',
    '5246af08-0730-40f7-83de-29b5d62b9b6d',
    '6bfa4a99-bdfa-4e44-aa01-9c7eac7e253d',
    '143cff36-30b4-4b25-9d26-5a2dbe6f6fc2',
    '94af9073-0914-4323-a90a-5eea1ef5f92c',
    '553f8d56-b6e7-46bd-a146-ac43b8ec6de7',
    '8413c5c6-b42b-4ec6-b751-881a54413628',
    '82a42cdf-3140-427b-8ad0-0d504716c871',
    'f936a701-5f8a-4aa1-b7a9-9f8b5b69bc7c',
    '3443eceb-50b3-450e-b7c1-fc465a3bc84f',
    '1b1028b4-17fd-4235-97b4-a9bdccdd51af',
    'e7abb87f-4324-4c89-8a46-97ed4b40577e',
    'd7361c6f-6751-4b5f-91c2-fdd61f988aa4',
    '8185f1e9-cfe0-4fd6-8d7e-446a8051c588',
    '341ef9bb-25f9-4eeb-8f1d-bdd054b22ba8',
]

pids.sort()
## first make the pictures
IMIN = 11
for i, pid in enumerate(pids):
    print(i, pid)
    if i < IMIN:
        continue
    reveal.make_rawdata_plot(FOLDER_DATA, pid, one=one, regions=br, clobber=False)
    reveal.make_raster_plot(FOLDER_DATA, pid, one=one, regions=br, clobber=False)

from PIL import Image
REVEAL_PATH.joinpath('img').mkdir(exist_ok=True)
for png_file in FOLDER_DATA.glob('*.png'):
    png_out = REVEAL_PATH.joinpath('img', png_file.name)
    if png_out.exists():
        png_out.unlink()
    pimg = Image.open(png_file)
    pimg.convert('RGB').save(png_out)



## then aggregate the pictures by acquisition day
# loop over dates
with open(REVEAL_PATH.joinpath('slides.html'), 'w+') as f:
    nfiles = len(list(FOLDER_DATA.glob(f'{pid}*')))
    for i, pid in enumerate(pids):
        print(i, pid)
        f.write(f"<section>\n")
        im = next(FOLDER_DATA.glob(f'{pid}*_raster.png'), '')
        f.write(reveal.slide_image(img_name=im, title=f'{pid} raster'))
        im = next(FOLDER_DATA.glob(f'{pid}*_raster_good_units.png'), '')
        f.write(reveal.slide_image(img_name=im, title=f'{pid} raster good'))
        for t0 in ['T0600', 'T1800', 'T3000']:
            im = next(FOLDER_DATA.glob(f'*{pid}*_raw_{t0}.png'), None)
            im_ = next(FOLDER_DATA.glob(f'*{pid}*_destripe_{t0}.png'), None)
            f.write(reveal.slide_compare_images(img_name1=im, img_name2=im_, title=f'{pid} raw  {t0}'))
        f.write(f"</section>\n")


reveal.build(reveal_path=REVEAL_PATH, title='Chronic', theme='solarized')
print("aws --profile ibl s3 sync ~/Documents/NODEJS/chronic s3://chronic.internationalbrainlab.org --exclude reveal.js/node_modules")
