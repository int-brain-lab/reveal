import numpy as np
import pandas as pd
from iblutil.numerical import ismember
from one.api import ONE
from brainbox.io.one import SpikeSortingLoader
from ibllib.atlas import BrainRegions

from pathlib import Path
import one.alf.io as alfio
from brainbox.io.spikeglx import Streamer
from viewephys.gui import viewephys
import scipy.signal
from neurodsp.voltage import destripe

regions = BrainRegions()
REVEAL_PATH = Path.home().joinpath('Documents/JS/reruns')
QC_DIR = REVEAL_PATH.joinpath('img')
RE_RUNS_PATH = Path("/mnt/s1/bwm/reruns")
V_T0 = [600, 60 * 30, 60 * 50]  # sample at 10, 30, 50 min in
N_SEC_LOAD = 1
one = ONE(base_url='https://alyx.internationalbrainlab.org')
CACHE_DIR = Path("/mnt/s1/bwm/raw_data_chunks")  # this is the path containing the metrics and clusters tables for fast releoading

butter_kwargs = {'N': 3, 'Wn': 300 / 30000 * 2, 'btype': 'highpass'}
sos = scipy.signal.butter(**butter_kwargs, output='sos')
eqcs = {}
DISPLAY_TIME = 0.05


def raster(spikes, clusters, channels, regions=regions, label=None, bad_channels=True):
    good_units = clusters['label'] == 1
    isok, _ = ismember(spikes['clusters'], clusters['cluster_id'][good_units])
    if next(QC_DIR.glob(f'{ssl.pid}*_raster_good_units*{label}.png'), None) is None:
        ssl.raster({k: spikes[k][isok] for k in spikes}, channels, save_dir=QC_DIR, br=regions,
                   label=f'raster_good_units_{label}')
        if np.sum(good_units) > 0:
            ssl.raster(spikes, channels, save_dir=QC_DIR, br=regions, label=f"raster_{label}")

    for T0 in V_T0:
        if len(list(QC_DIR.glob(f"{ssl.pid}_*_T{T0:04d}.png"))) == 2:
            continue
        sr = Streamer(pid=pid, one=one, remove_cached=False, typ='ap', cache_folder=CACHE_DIR)
        start = int(T0 * sr.fs)
        end = int((T0 + N_SEC_LOAD) * sr.fs)
        if end > sr.ns:
            continue
        raw = sr[start:end, :-sr.nsync].T
        butter = scipy.signal.sosfiltfilt(sos, raw)
        eqcs['raw'] = viewephys(butter, sr.fs, br=regions, title='raw', channels=channels)
        eqcs['destripe'] = viewephys(destripe(raw, fs=sr.fs, channel_labels=bad_channels)
                                     , sr.fs, br=regions, title='destripe', channels=channels)
        spike_selection = slice(*np.searchsorted(spikes['samples'], [start, end]))
        for k, eqc in eqcs.items():
            sc = clusters['channels'][spikes['clusters'][spike_selection]]
            st = (spikes['samples'][spike_selection] / sr.fs - T0) * 1000
            sl = clusters['label'][spikes['clusters'][spike_selection]]
            # Plot not good spikes in red
            eqc.ctrl.add_scatter(st[sl != 1], sc[sl != 1], (255, 0, 0, 200), label='spikes_bad')
            eqc.ctrl.add_scatter(st[sl == 1], sc[sl == 1], (50, 205, 50, 200), label='spikes_good')
            eqc.viewBox_seismic.setYRange(0, raw.shape[0])
            eqc.viewBox_seismic.setXRange(500, 500 + DISPLAY_TIME * 1000)
            eqc.ctrl.set_gain(25)
            eqc.resize(1960, 1200)
            eqc.grab().save(str(QC_DIR.joinpath(f"{ssl.pid}_{k}_T{T0:04d}_{label}.png")))
            eqc.close()


for path_pid in Path(RE_RUNS_PATH).glob('*'):
    pid = path_pid.parts[-1]
    path_pid.joinpath('alf')
    # 'e10a7a75-4740-41d1-82bb-7696ed14c442' channel loading issue
    if len(list(QC_DIR.glob(f'{pid}*.png'))) < 16:
        rspikes = alfio.load_object(path_pid.joinpath('alf'), 'spikes')
        rclusters = alfio.load_object(path_pid.joinpath('alf'), 'clusters')
        channel_labels = np.load(path_pid.joinpath('channel_labels.npy'))
        rclusters = {k:rclusters[k] for k in rclusters if k in ['channels', 'depths', 'metrics', 'uuids']}
        ssl = SpikeSortingLoader(pid=pid, one=one)
        spikes, clusters, channels = ssl.load_spike_sorting(dataset_types=['spikes.samples'])
        print(f"pid: {pid}, merge clusters original")
        clusters = ssl.merge_clusters(spikes, clusters, channels)
        print(f"pid: {pid}, merge clusters new")
        cluster_cache = path_pid.joinpath('alf').joinpath('cached_clusters.pqt')
        if cluster_cache.exists():
            pd.read_parquet(path_pid.joinpath('alf').joinpath('cached_clusters.pqt'))
        else:
            rclusters = ssl.merge_clusters(rspikes, rclusters, channels, cache_dir=path_pid.joinpath('alf'))
        raster(spikes, clusters, channels, regions=regions, label='original', bad_channels=channel_labels)
        raster(rspikes, rclusters, channels, regions=regions, label='1.4.0alpha', bad_channels=channel_labels)
    else:
        print(f"pid: {pid}, already done")


## %% build the slides.html file for the re-run images display
from pathlib import Path
import reveal
RE_RUNS_PATH = Path("/mnt/s1/bwm/reruns")
REVEAL_PATH = Path.home().joinpath('Documents/JS/reruns')
QC_DIR = REVEAL_PATH.joinpath('img')

with open(REVEAL_PATH.joinpath('slides.html'), 'w') as f:
    for i, path_pid in enumerate(Path(RE_RUNS_PATH).glob('*')):
        pid = path_pid.parts[-1]
        if len(list(QC_DIR.glob(f'{pid}*.png'))) < 15:
            continue
        for label in ['original', '1.4.0alpha']:
            f.write(f"<section>\n")
            f.write(reveal.slide_image(next(QC_DIR.glob(f'{pid}*_raster_{label}*.png')).name, title=f'raster {label}'))
            fgr = next(QC_DIR.glob(f'{pid}*_raster_good*{label}*.png'), None)
            if fgr is not None:
                f.write(reveal.slide_image(fgr.name, title=f'good units {label}'))
            f.write(reveal.slide_compare_images(
                next(QC_DIR.glob(f'{pid}*_raw_T0600_{label}*.png')).name,
                next(QC_DIR.glob(f'{pid}*_destripe_T0600_{label}*.png')).name,
                title=f"{label}, T0600",
            ))
            f.write(reveal.slide_compare_images(
                next(QC_DIR.glob(f'{pid}*_raw_T1800_{label}*.png')).name,
                next(QC_DIR.glob(f'{pid}*_destripe_T1800_{label}*.png')).name,
                title=f"{label}, T1800",
            ))
            f.write(reveal.slide_compare_images(
                next(QC_DIR.glob(f'{pid}*_raw_T3000_{label}*.png')).name,
                next(QC_DIR.glob(f'{pid}*_destripe_T3000_{label}*.png')).name,
                title=f"{label}, T3000",
            ))
            f.write(f"</section>\n")

reveal.build(REVEAL_PATH, theme='white', title='reruns')
