# %% Step 1: Create the reveal deck of images
from pathlib import Path
import tqdm

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn.preprocessing

from one.api import ONE
import ephysatlas.fixtures
import ephysatlas.reveal
import ephysatlas.data

pid = str(np.random.choice(ephysatlas.fixtures.benchmark_pids))
path_features = Path("/datadisk/Data/paper-ephys-atlas/ephys-atlas-decoding/features/2025_W28")
df_features = ephysatlas.data.read_features_from_disk(path_features, strict=False)
df_features_raw = ephysatlas.data.read_features_from_disk(path_features, strict=False, load_denoised=False)

one = ONE(base_url="https://alyx.internationalbrainlab.org")
path_model = Path(
    "/datadisk/Data/paper-ephys-atlas/ephys-atlas-decoding/models/2025_W28_Cosmos_living-olivedrab-cassowary")
path_model_no_coordinates = Path(
    '/datadisk/Data/paper-ephys-atlas/ephys-atlas-decoding/models/2025_W28_Cosmos_sloppy-iris-zebu'
)
df_predictions = pd.read_parquet(path_model / "predictions.pqt")
path_figures = Path(f"/datadisk/Data/paper-ephys-atlas/reveal")
pids_predict = df_predictions.index.get_level_values(level=0).unique()

pids = df_features.index.get_level_values(level=0).unique()
path_reveal = Path.home().joinpath('Documents/JS/reveal.internationalbrainlab.org')

# learn the scaling (ideally this should be in the model data itself)
scaler = sklearn.preprocessing.RobustScaler()
x_list = ephysatlas.features.voltage_features_set()
scaler.fit(df_features.loc[:, x_list])

# %%
IMIN = 290
skip = ['26118c10-35dd-4ab1-9f0f-b9a89a1da070', '31d8dfb1-71fd-4c53-9229-7cd48bee07e4', '3ccb2d59-9e94-48e6-9e72-0b7b96bd3f9b',
        '530f1670-9412-44ac-afdb-935d46bcaad3', '7c11adc6-adbd-484f-8ae9-13946285e3f8', '9915765e-ff15-4371-b1aa-c2ef1db8a254',
        'a3ebc7f4-813a-4f06-a33e-9825c878f9c2', 'c250d4f4-7516-4cf1-a8bd-04873ca9e21c', 'dac5defe-62b8-4cc0-96cb-b9f923957c7f',
        'eebcaf65-7fa4-4118-869d-a084e84530e2', '3bd1f88b-4e0c-43a6-9483-3305e82f2fae', '5a9f8899-556a-43ea-892d-5e35b969ff38']
for i, pid in tqdm.tqdm(enumerate(pids), total=len(pids)):
    if i < IMIN or pid in skip:
        continue
    save_dir = path_figures.joinpath(pid)
    df_pid = df_features.loc[pid]
    ar = ephysatlas.reveal.AtlasReveal(one, pid=pid, df_pid=df_pid)
    # You can also save all figures at once
    # ar.figure_01_features_with_histology_columns(save_dir=save_dir, scaler=scaler)
    ar.figure_01_features_with_histology_columns(save_dir=save_dir, scaler=scaler, df_pid=df_raw_features.loc[pid], filename=f'{pid}_figure_01b_raw_features_with_histology_columns.png')
    # ar.figure_03_histology_slices(save_dir=save_dir)
    # df_preds = df_predictions.loc[pid] if pid in pids_predict else None
    # ar.figure_02_classifier_results(df_predictions=df_preds, path_model=path_model, save_dir=save_dir,
    #                                 filename=f'{pid}_figure_02_classifier_results_0.png', overwrite=True)
    # ar.figure_02_classifier_results(df_predictions=df_preds, path_model=path_model_no_coordinates, save_dir=save_dir,
    #                                 filename=f'{pid}_figure_02_classifier_results_1.png', overwrite=True)
    # ar.figure_04_ap_voltage(save_dir=save_dir)
    # ar.figure_05_lfp_voltage(save_dir=save_dir)
    # ar.figure_06_bad_channels(save_dir=save_dir)
    plt.close('all')

# %% Builds the website locally
from reveal.api import RevealSite
pids = df_features.index.get_level_values(level=0).unique()
pids_train = df_predictions.index.get_level_values(level=0).unique()

SITE_NAME = 'ephys_atlas_reveal'
c = 0

deck = []
for i, pid in enumerate(pids):
    path_pid = path_figures.joinpath(pid)
    png_images = sorted(list(path_pid.glob('*.png')))
    if len(png_images) < 7:
        continue
    c += 1
    print(f"PID {pid} done")
    if pid not in pids_train:
        prefix = 'MISALIGNED ?'
    else:
        prefix = ''
    deck.append(np.array([
        dict(
            image_path=next(path_pid.glob('*_figure_01*.png'), None),
            title=f"{prefix} {pid[:8]}: Features", post=pid
        ),
        dict(
            image_path=next(path_pid.glob('*_figure_02*.png'), None),
            title=f"{prefix} {pid[:8]}: Classifier Results", post=pid
        ),
        dict(
            image_path=next(path_pid.glob('*_figure_03*.png'), None),
            title=f"{prefix} {pid[:8]}: Histology", post=pid
        ),
        dict(
            image_path=next(path_pid.glob('*_figure_04*_0.png'), None),
            image_path_compare=next(path_pid.glob('*_figure_04*_1.png'), None),
            title=f"{prefix} {pid[:8]}: AP Raw Data", post=pid
        ),
        dict(
            image_path=next(path_pid.glob('*_figure_05*_0.png'), None),
            image_path_compare=next(path_pid.glob('*_figure_05*_1.png'), None),
            title=f"{prefix} {pid[:8]}: LFP Raw / CSD Data", post=pid
        ),
        dict(
            image_path=next(path_pid.glob('*_figure_06*.png'), None),
            title=f"{prefix} {pid[:8]}: Bad Channels", post=pid
        ),
        ])[np.newaxis, :])
print(c, c / len(pids))

deck = np.concatenate(deck).T
site = RevealSite(deck, name=SITE_NAME, reveal_path=path_reveal)
site.build(theme='serif')
site.open()

# %% Commands to upload to AWS
print(f"aws --profile ucl s3 cp {path_reveal}/{SITE_NAME}.html s3://reveal.internationalbrainlab.org/{SITE_NAME}.html")
print(f"aws --profile ucl s3 sync {path_reveal}/images/{SITE_NAME} s3://reveal.internationalbrainlab.org/images/{SITE_NAME}")


# %%


