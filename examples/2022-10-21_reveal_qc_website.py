from pathlib import Path
import pandas as pd

from PIL import Image
import pandas as pd
import reveal
REVEAL_PATH = Path.home().joinpath('Documents/JS/reveal.js')

BWM_DIR = Path("/mnt/s1/bwm")
qc_file = BWM_DIR.joinpath('qc_bwm_df.pqt')

# import shutil
# shutil.rmtree(REVEAL_PATH.joinpath('img'))
# REVEAL_PATH.joinpath('img').mkdir()

def slide(*args, c=0, **kwargs):
    link = f"https://docs.google.com/spreadsheets/d/1HSgnm32xP0TBJer3VqvblogmRegsZ00fEyWVnlJjbsw/edit#gid=1000332194&range=A{c + 1}"
    post = f'<small> <a href="{link}" target="_blank" rel="noopener noreferrer">Add your comments to this spreadsheet</a> </small>'
    return reveal.slide_image(*args, **kwargs, post=post)

def slide_compare(*args, c=0, **kwargs):
    link = f"https://docs.google.com/spreadsheets/d/1HSgnm32xP0TBJer3VqvblogmRegsZ00fEyWVnlJjbsw/edit#gid=1000332194&range=A{c + 1}"
    post = f'<small> <a href="{link}" target="_blank" rel="noopener noreferrer">Add your comments to this spreadsheet</a> </small>'
    return reveal.slide_compare_images(*args, **kwargs, post=post)


df = pd.read_parquet(qc_file).sort_values('pid')
images = ['raster', 'raster_good_units']
file_slides = REVEAL_PATH.joinpath('slides.html')
import tqdm
with open(file_slides, 'w+') as f:
    c = 0
    for i, dfi in tqdm.tqdm(df.iterrows()):
        c += 1
        pid = dfi['pid']
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
        f.write(slide(img_name=images['raster'], title=f'{dfi["pid"][:8]} raster', c=c))
        f.write(slide(img_name=images['raster_good'], title=f'{dfi["pid"][:8]} raster good', c=c))
        f.write(slide_compare(img_name1=images['raw_butter1'], img_name2=images['raw_destripe1'], title=f'{dfi["pid"][:8]} raw 600s', c=c))
        f.write(slide_compare(img_name1=images['raw_butter2'], img_name2=images['raw_destripe2'], title=f'{dfi["pid"][:8]} raw 1800s', c=c))
        f.write(slide_compare(img_name1=images['raw_butter3'], img_name2=images['raw_destripe3'], title=f'{dfi["pid"][:8]} raw 3000s', c=c))
        f.write(f"</section>\n")

reveal.build(reveal_path=REVEAL_PATH)
# https://github.com/CreativeTechGuy/RevealJS
# https://www.w3schools.com/howto/howto_js_image_comparison.asp

#// aws --profile ibl s3 sync ~/Documents/JS/reveal.js s3://reveal.internationalbrainlab.org --exclude reveal.js/node_modules
# // http://reveal.internationalbrainlab.org.s3-website-us-east-1.amazonaws.com
# import numpy as np
# from one.api import ONE
# import atlaselectrophysiology.ephys_atlas_gui as ephys_atlas_gui
# from pathlib import Path
#
# one = ONE()
# save_path = Path('/Users/gaelle/Desktop/Reports/PhysAlign/Alignment_tocheck/')
# pids = np.load('/Users/gaelle/Desktop/Reports/PhysAlign/pids_20-09-2022.npy')
#
# for pid in pids:
#     window = ephys_atlas_gui.viewer(pid, one=one, histology=True)
#     window.save_plots(save_path=save_path.joinpath(pid))
#     window.close()
##

