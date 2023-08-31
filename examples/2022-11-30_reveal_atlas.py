from pathlib import Path
import numpy as np
import yaml

from one.api import ONE
from viewephys.gui import viewephys
from brainbox.io.one import SpikeSortingLoader
from ibllib.atlas import BrainRegions


import reveal
regions = BrainRegions()
def load_npy_float16(path):
    with open(path.with_suffix('.yml'), 'rb') as fp:
         yaml_dict = yaml.safe_load(fp)
    return np.load(path).astype(np.float32), yaml_dict



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
ROOT_PATH = Path("/mnt/s1/ephys-atlas-sample")

ROOT_PATH = Path("/mnt/s1/ephys-atlas")
pids = [p.parts[-1] for p in ROOT_PATH.glob('*') if p.is_dir()]

# ROOT_PATH = Path("/datadisk/Data/ephys-atlas-sample")
one = ONE(base_url='https://alyx.internationalbrainlab.org')


def pid_pictures(pid, one=None):
    assert one
    path_pid = ROOT_PATH.joinpath(pid)
    path_img = path_pid.joinpath('pics')
    path_img.mkdir(exist_ok=True)

    ssl = SpikeSortingLoader(pid=pid, one=one)
    channels = ssl.load_channels()

    reveal.make_raster_plot(path_img, pid, one=one, regions=regions, clobber=False)

    for ap_file in path_pid.rglob('ap.npy'):
        eqcs = {}
        tlabel = ap_file.parts[-2]
        if next(path_img.glob(f"{tlabel}_voltage*.png"), None):
            continue
        raw = np.load(ap_file.parent.joinpath('raw.npy')).astype(np.float32)
        destripe, fh_ap = load_npy_float16(ap_file)
        lfp, fh_lf = load_npy_float16(ap_file.parent.joinpath('lf.npy'))
        eqcs['ap_raw'] = viewephys(raw, fh_ap['fs'], channels=channels, title='ap_raw', br=regions, t0=0.5)
        eqcs['ap_destripe'] = viewephys(destripe[:, slice(int(.5 * 30000), int((.5 + 0.05) * 30000))], fh_ap['fs'],
                                        channels=channels, title='ap_destripe', br=regions)
        # eqcs['lf'] = viewephys(lfp, fh_lf['fs'], channels=channels, title='lf', br=regions)


        for label, eqc in eqcs.items():
            eqc.viewBox_seismic.setYRange(0, raw.shape[0])
            eqc.viewBox_seismic.setXRange(0, 50)
            eqc.ctrl.set_gain(26)
            eqc.resize(1960, 1200)
            eqc.grab().save(str(path_img.joinpath(f"{tlabel}_voltage_{label}.png")))
            eqc.close()
    return pid

for pid in pids:
    pid_pictures(pid, one=one)

#
# import dask
# from dask.distributed import Client, progress
# client = Client(threads_per_worker=4, n_workers=1, dashboard_address=':12345')
#
#
#
# # dask.persist(*all_tasks)
# ## %%
# big_one = client.scatter(one)  # good
#
# all_tasks = [dask.delayed(pid_pictures)(pid, one=big_one) for pid in pids]
# # tada = dask.compute(*all_tasks)
#
# # futures = [client.submit(pid_pictures, pid, big_one) for pid in pids]