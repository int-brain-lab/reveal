import numpy as np
import pandas as pd

import iblatlas.atlas
from brainbox.io.one import SpikeSortingLoader, SessionLoader


def pid_electrophysiology_qc(path_reveal, pid=None, one=None, regions=None):
    """
    Generate and save a set of reveal figures for a given probe insertion.

    This function creates various plots related to spike sorting and raw electrophysiology data
    for a specific probe insertion. It saves these plots as PNG files in a directory structure
    based on the provided path and probe insertion ID.

    Parameters:
    -----------
    path_reveal : pathlib.Path
        The base path where the figures will be saved.
    pid : str, optional
        The probe insertion ID. Must be provided.
    one : ONE object, optional
        An instance of the ONE API for data retrieval. Must be provided.
    regions : BrainRegions object, optional
        An instance of iblatlas.atlas.BrainRegions. If not provided, a new instance will be created.

    Returns:
    --------
    None

    Side Effects:
    -------------
    - Creates a directory for the probe insertion under path_reveal if it doesn't exist.
    - Saves up to 8 PNG files in this directory, including raster plots and raw data snippets.
    - If 8 PNG files already exist in the directory, the function returns without doing anything.
    ├── fe41986d-4966-4a77-af7e-e7f71c25aec5
         ├── 01.png  # raster all units
         ├── 02.png  # raster QC passing units
         ├── 03a.png  # snippet 1 raw
         ├── 03b.png  # snippet 1 processed
         ├── 04a.png  # snippet 2 raw
         ├── 04b.png  # snippet 2 ...
         ├── 05a.png
         └── 05b.png

    Notes:
    ------
    - The function requires the brainbox and iblatlas libraries.
    - It uses SpikeSortingLoader and SessionLoader to retrieve necessary data.
    - The function generates plots for all units, QC passing units, and raw data snippets at different time points.
    """
    assert one is not None, 'one must be provided'
    assert pid is not None, 'pid must be provided'
    if regions is None:
        regions = iblatlas.atlas.BrainRegions()

    path_pid = path_reveal.joinpath(pid)
    path_pid.mkdir(exist_ok=True, parents=True)
    if len(list(path_pid.glob('*.png'))) == 8:
        return

    # loads spike sorting, trial data, and recording meta-data
    ssl = SpikeSortingLoader(one=one, pid=pid)
    sl = SessionLoader(one=one, eid=ssl.eid)
    sl.load_trials()
    sr = ssl.raw_electrophysiology(band="ap", stream=True)
    spikes, clusters, channels = ssl.load_spike_sorting(dataset_types=['spikes.samples'])
    df_clusters = pd.DataFrame(ssl.merge_clusters(spikes, clusters, channels))
    drift = ssl.load_spike_sorting_object('drift')

    # computes the passing qc masks and the behaviour session length
    icok = np.where(df_clusters['bitwise_fail'] == 0)[0]
    isok = np.isin(spikes['clusters'], icok)
    behaviour_bounds = {'bounds': sl.trials['stimOn_times'].to_numpy()[[0, -1]]}

    # raster plots
    ssl.raster(spikes, channels, save_dir=path_pid.joinpath('01.png'), br=regions, time_series=behaviour_bounds,
               drift=drift, title='All Units')
    spikes_ok = {k: v[isok] for k, v in spikes.items()}
    ssl.raster(spikes_ok, channels, save_dir=path_pid.joinpath('02.png'), br=regions, time_series=behaviour_bounds,
               drift=drift, title='QC Passing Units')

    # raw data plots
    c = 2
    for t0 in np.floor(np.linspace(0, sr.rl, 5)[1:4]):
        c += 1
        ssl.plot_rawdata_snippet(sr, spikes, clusters, t0, channels=channels,
                                 br=regions,
                                 save_dir=path_pid.joinpath(f'{c:02.0f}a.png'),
                                 gain=-96,
                                 label=f'T{str(t0)}_raw',
                                 title=f'T {t0:.2f}',
                                 alpha=0,
                                 processing=None)
        ssl.plot_rawdata_snippet(sr, spikes, clusters, t0, channels=channels,
                                 br=regions,
                                 save_dir=path_pid.joinpath(f'{c:02.0f}b.png'),
                                 gain=-96,
                                 label=f'T{str(t0)}_destripe',
                                 title=f'T {t0:.2f} s')

