# %% Step 1: Create the reveal deck of images
import joblib
from pathlib import Path
import tqdm

import pandas as pd
import numpy as np

from one.api import ONE
import iblatlas.atlas
import reveal.plots


import iblatlas.atlas
import ephys_atlas.data
import ephys_atlas.decoding


ba = iblatlas.atlas.AllenAtlas()
regions = iblatlas.atlas.BrainRegions()

path_features = Path('/mnt/s0/ephys-atlas-decoding/features/2024_W50')  # parede
# path_features = Path('/datadisk/Data/paper-ephys-atlas/ephys-atlas-decoding/features/2024_W50')  # linux laptop
df_features, df_clusters, df_channels, df_probes = ephys_atlas.data.load_voltage_features(path_features)

one = ONE(base_url='https://alyx.internationalbrainlab.org')
path_reveal = Path(f"/home/olivier/scratch/reveal_ephys_atlas")
path_reveal.mkdir(parents=True, exist_ok=True)

PIDS = list(df_probes['pid'])

def make_pid_reveal_figures_multiprocessing(pid):
    try:
        reveal.plots.pid_electrophysiology_qc(
            pid=pid,
            path_reveal=path_reveal,
            regions=regions,
            one=one
        )
    except Exception as e:
        for _ in range(30):
            print(f"Error processing PID {pid}: {str(e)}")

jobs = []
for pid in PIDS:
    jobs.append(joblib.delayed(make_pid_reveal_figures_multiprocessing)(pid))

list(tqdm.tqdm(joblib.Parallel(return_as='generator', n_jobs=8)(jobs)))

c = 0
for pid in PIDS:
    if len(list(path_reveal.joinpath(pid).glob('*.png'))) == 8:
        continue
    c += 1
    print(f"PID {pid} failed to generate 8 images")
print(c, 'missing images pids')
# %% Builds the website locally
from reveal.api import RevealSite
SITE_NAME = 'ephys_atlas_reveal'
c = 0
deck = []
for i, pid in enumerate(PIDS):
    path_pid = path_reveal.joinpath(pid)
    png_images = sorted(list(path_pid.glob('*.png')))
    if len(png_images) < 8:
        continue
    c += 1
    print(f"PID {pid} done")
    deck.append(np.array([
        dict(image_path=png_images[0], title=f"{pid[:8]}: Raster all units", post=pid),
        dict(image_path=png_images[1], title=f"{pid[:8]}: Raster good units", post=pid),
        dict(image_path=png_images[2], image_path_compare=png_images[3], title=f"{pid[:8]}: raw data snippet 1/3", post=pid),
        dict(image_path=png_images[4], image_path_compare=png_images[5], title=f"{pid[:8]}: raw data snippet 2/3", post=pid),
        dict(image_path=png_images[6], image_path_compare=png_images[7], title=f"{pid[:8]}: raw data snippet 3/3", post=pid),
        ])[np.newaxis, :])
print(c, c / len(PIDS))
deck = np.concatenate(deck).T
reveal_path = Path.home().joinpath('Documents/Reveal/reveal.internationalbrainlab.org')
site = RevealSite(deck, name=SITE_NAME, reveal_path=reveal_path)
site.build(theme='serif')
site.open()

# %% Commands to upload to AWS
print(f"aws --profile ucl s3 cp {reveal_path}/{SITE_NAME}.html s3://reveal.internationalbrainlab.org/{SITE_NAME}.html")
print(f"aws --profile ucl s3 sync {reveal_path}/images/{SITE_NAME} s3://reveal.internationalbrainlab.org/images/{SITE_NAME}")


