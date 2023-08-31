from pathlib import Path
import pandas as pd
import numpy as np
from iblutil.numerical import ismember
from one.api import ONE
from brainbox.io.one import SpikeSortingLoader
from ibllib.atlas import BrainRegions
from PIL import Image
import pandas as pd
import reveal

regions = BrainRegions()
REVEAL_PATH = Path.home().joinpath('Documents/JS/reruns')
QC_DIR = REVEAL_PATH.joinpath('img')

one = ONE(base_url='https://alyx.internationalbrainlab.org')


def raster(ssl, label, spike_sorter, regions=regions):
    spikes, clusters, channels = ssl.load_spike_sorting(spike_sorter=spike_sorter)
    compute_metrics = True if spike_sorter == 'ks2' else False
    clusters = ssl.merge_clusters(spikes, clusters, channels, compute_metrics=compute_metrics)
    good_units = clusters['label'] == 1
    isok, _ = ismember(spikes['clusters'], clusters['cluster_id'][good_units])
    if next(QC_DIR.glob(f'{ssl.pid}*_raster_good_units.png'), None) is None and np.sum(good_units) > 0:
        ssl.raster({k: spikes[k][isok] for k in spikes}, channels, save_dir=QC_DIR, br=regions,
                   label=f'raster_good_units_{label}')
    if next(QC_DIR.glob(f'{ssl.pid}*_raster.png'), None) is None and np.sum(good_units) > 0:
        ssl.raster(spikes, channels, save_dir=QC_DIR, br=regions, label=f'raster_{label}')


dsets = one.alyx.rest('datasets', 'list', collection='alf/probe01', name='spikes.times.npy')
dsets2 = one.alyx.rest('datasets', 'list', collection='alf/probe00', name='spikes.times.npy')


dsets = list(dsets) + list(dsets2)
for dset in dsets:
    eid = dset['session'][-36:]
    pname = dset['collection'].split('/')[1]
    pid = one.alyx.rest('insertions', 'list', session=eid, name=pname)
    if len(pid) == 0:
        continue
    pid = pid[0]['id']
    ssl = SpikeSortingLoader(pid=pid, one=one)

    if len(list(QC_DIR.glob(f'{ssl.pid}*_raster*.png'))) >= 4:
        continue
    raster(ssl, label='ks2', spike_sorter='', regions=regions)
    raster(ssl, label='pykilosort', spike_sorter='pykilosort', regions=regions)


