from pathlib import Path
import pandas as pd
import shutil
path_qc = Path("/datadisk/scratch/rs")


files = [f.name for f in path_qc.glob('*.png')]
files.sort()
df = pd.DataFrame(dict(pids=[fn[:36] for fn in files], labels=[fn[37:-4] for fn in files], filenames=files))


df = df.pivot(index='pids', columns='labels', values='filenames')


## %%
from reveal import Presentation
prez = Presentation(name='2023-02-28_lfp_reproducible')


for pid, rec in df.iterrows():
    prez.new_section()
    prez.add_slide_image(title=f'raw {pid}', full_path_image=path_qc.joinpath(rec['00_raw']))
    prez.add_slide_image(title=f'butterworth {pid}', full_path_image=path_qc.joinpath(rec['01_butt']))
    prez.add_slide_image(title=f'destripe {pid}', full_path_image=path_qc.joinpath(rec['02_destripe']))
    prez.add_slide_image(title=f'csd {pid}', full_path_image=path_qc.joinpath(rec['03_csd']))
    prez.add_slide_image(title=f'csd_denoise {pid}', full_path_image=path_qc.joinpath(rec['04_csd_denoise']))
    prez.add_slide_image(title=f'KCSD {pid}', full_path_image=path_qc.joinpath(rec['05_ksd']))
    prez.add_slide_image(title=f'KCSD noise {pid}', full_path_image=path_qc.joinpath(rec['06_ksd_denoise']))
    prez.close_section()

prez.build()
#
# prez.path_images.mkdir(exist_ok=True)
# for f in path_qc.glob('*.png'):
#     shutil.copy(f, prez.path_images.joinpath(f.name))

# aws --profile ibl s3 sync ~/Documents/JS/reveal.js s3://reveal.internationalbrainlab.org --delete