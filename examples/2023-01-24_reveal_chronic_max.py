from pathlib import Path
from one.api import ONE
from iblatlas.regions import BrainRegions
import reveal
one = ONE()
br = BrainRegions()

FOLDER_CHRONIC = Path("/datadisk/Data/reveal/chronic")
REVEAL_PATH = Path.home().joinpath('Documents/NODEJS/chronic')

subject_name = "MM007"

sessions = one.alyx.rest('sessions', 'list', subject=subject_name)
insertions = one.alyx.rest('insertions', 'list', django=f'session__subject__nickname,{subject_name}')

pids = [i['id'] for i in insertions]


IMIN = 42
## first make the pictures
for i, pid in enumerate(pids):
    print(i, pid)
    if i < IMIN:
        continue
    reveal.make_rawdata_plot(FOLDER_CHRONIC, pid, one=one, regions=br, clobber=False)
    reveal.make_raster_plot(FOLDER_CHRONIC, pid, one=one, regions=br, clobber=False)

from PIL import Image
REVEAL_PATH.joinpath('img').mkdir(exist_ok=True)
for png_file in FOLDER_CHRONIC.glob('*.png'):
    png_out = REVEAL_PATH.joinpath('img', png_file.name)
    if png_out.exists():
        png_out.unlink()
    pimg = Image.open(png_file)
    pimg.convert('RGB').save(png_out)



## then aggregate the pictures by acquisition day
ins = insertions[0]
import datetime
list_days = sorted(list(set([ins['session_info']['start_time'][:10] for ins in insertions])))

# loop over dates
with open(REVEAL_PATH.joinpath('slides.html'), 'w+') as f:
    for day in list_days:
        f.write(f"<section>\n")
        # displays the probe00
        for pname in ['probe00', 'probe01']:
            im = next(FOLDER_CHRONIC.glob(f'*{day}*{pname}*_raster.png'), None)
            f.write(reveal.slide_image(img_name=im, title=f'{day} {pname} raster'))
            im = next(FOLDER_CHRONIC.glob(f'*{day}*{pname}*_raster_good_units.png'), None)
            f.write(reveal.slide_image(img_name=im, title=f'{day} {pname} raster good'))
        for pname in ['probe00', 'probe01']:
            for t0 in ['T0600', 'T1800', 'T3000']:
                im = next(FOLDER_CHRONIC.glob(f'*{day}*{pname}*_raw_{t0}.png'), None)
                im_ = next(FOLDER_CHRONIC.glob(f'*{day}*{pname}*_destripe_{t0}.png'), None)
                f.write(reveal.slide_compare_images(img_name1=im, img_name2=im_, title=f'{day} {pname} raw  {t0}'))
        f.write(f"</section>\n")






reveal.build(reveal_path=REVEAL_PATH, title='Chronic', theme='solarized')
print("aws --profile ibl s3 sync ~/Documents/NODEJS/chronic s3://chronic.internationalbrainlab.org --exclude reveal.js/node_modules")