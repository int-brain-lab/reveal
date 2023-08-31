from pathlib import Path
from one.api import ONE

import spikeglx
from brainbox.io.one import SpikeSortingLoader
import scipy
from viewephys.gui import viewephys
from neurodsp.voltage import destripe
from ibllib.atlas import BrainRegions
from brainbox.io.spikeglx import Streamer
from iblutil.util import Bunch
import neuropixel
from neurodsp.waveforms import peak_trough_tip
import numpy as np
import pandas as pd
import torch
from scipy.signal import convolve2d

one = ONE()

def load_phy(path_phy, ks4=False):
    file_metrics = path_phy.joinpath('metrics.pqt')

    if not ks4:
        whitening = np.load(path_phy.joinpath('whitening_mat.npy'))
        whitening_inv = np.load(path_phy.joinpath('whitening_mat_inv.npy'))
        #assert (np.linalg.cond(whitening_inv)) == 1
    else:
    # file_ops = path_ks4.joinpath('ops_cpu.npy')
    # ops = np.load(file_ops, allow_pickle=True).tolist()
    # whitening = ops['Wrot'].cpu()
        whitening = np.load(path_phy.joinpath("Wrot.npy"))
        whitening_inv = np.linalg.inv(whitening)


    templates = Bunch({
        'waveforms': np.load(path_phy.joinpath('templates.npy')),
        'indices': np.load(path_phy.joinpath('templates_ind.npy')),
    })

    # gets the channel map from ks4 and compute the mapping to raw indices
    chks2probe = h['ind'][np.load(path_phy.joinpath('channel_map.npy'))]

    # apply inverse whitening to templates
    raw_waveforms = np.zeros_like(templates.waveforms)
    # for k in np.arange(templates.waveforms[0]):
    #     raw_waveforms[k, :, :] = np.matmul(templates.waveforms[k, :, :] * 1)
    # pick the maximum of the waveform on the templates

    ptt = peak_trough_tip(templates.waveforms)

    templates.amps = np.max(ptt[['peak_val', 'trough_val', 'tip_val']], axis=1).values - np.min(
        ptt[['peak_val', 'trough_val', 'tip_val']], axis=1).values
    templates.amps *= neuropixel.S2V_AP

    templates_indices = templates.indices
    if not ks4:
        templates_indices = np.tile(np.arange(templates_indices.shape[0]), (templates_indices.shape[1], 1))

    print(templates_indices.shape)
    ich = peak_trough_tip(templates.waveforms)['peak_trace_idx'].values
    idx = templates_indices[np.arange(templates_indices.shape[0]), ich]
    templates.channels = chks2probe[idx]
    # clusters and templates are interchangeable here
    spikes = Bunch({
        'samples': np.load(path_phy.joinpath('spike_times.npy')),
        'clusters': np.load(path_phy.joinpath('spike_clusters.npy')),
        'templates': np.load(path_phy.joinpath('spike_templates.npy')),
        'amps_au': np.load(path_phy.joinpath('amplitudes.npy')),
    })
    spikes.amps = spikes.amps_au * templates.amps[spikes.templates]
    spikes.times = spikes.samples / FS
    spikes.channels = templates.channels[spikes.templates]
    spikes.depths = spikes.channels * np.NaN

    if file_metrics.exists():
        metrics = pd.read_parquet(file_metrics)
    else:
        metrics = SpikeSortingLoader.compute_metrics(spikes)
        metrics.to_parquet(file_metrics)
    return spikes, metrics, templates, whitening, whitening_inv

FOLDER_DATA = Path.home().joinpath('Documents/PYTHON/int-brain-lab/ibldevtools/chris/spikesorting/')
REVEAL_PATH = Path.home().joinpath('Documents/JS/ks_rerun')

pids = [
    '1a276285-8b0e-4cc9-9f0a-a3a002978724',
    '1e104bf4-7a24-4624-a5b2-c2c8289c0de7',
    '5d570bf6-a4c6-4bf1-a14b-2c878c84ef0e',
    '5f7766ce-8e2e-410c-9195-6bf089fea4fd',
    '6638cfb3-3831-4fc2-9327-194b76cf22e1',
    '749cb2b7-e57e-4453-a794-f6230e4d0226',
]

pids = pids[5:]
pids.sort()

prez = reveal.Presentation(name="ks4", path_reveal=REVEAL_PATH)
h = neuropixel.trace_header()
FS = 30000
KS4_PATH = FOLDER_DATA / "data" / "ks4"
KS25_RERUN_PATH = FOLDER_DATA / "data" / "ks25_new"
OUT_IMGS_PATH = FOLDER_DATA / "residuals"
OUT_IMGS_PATH.mkdir(exist_ok=True)
ALPHA = 120
S0 = 600 * FS
# get raw data
for pid in pids:
    eqcs = {}
    eid, probe = one.pid2eid(pid)
    #dsets = one.list_datasets(eid, collection=f'raw_ephys_data/{probe}', filename='*.ap.cbin')
    #raw_data, _ = one.load_datasets(eid, dsets, query_type="local")
    bin_path = one.eid2path(eid).joinpath(f"raw_ephys_data/{probe}/_spikeglx_ephysData_g0_t0.imec{probe[-1]}.ap.cbin")
    sr = spikeglx.Reader(bin_path)
    raw = sr[S0:S0 + FS,:-sr.nsync].T
    butter_kwargs = {'N': 3, 'Wn': 300 / 30000 * 2, 'btype': 'highpass'}
    sos = scipy.signal.butter(**butter_kwargs, output='sos')
    raw = scipy.signal.sosfiltfilt(sos, raw)
    destriped = destripe(raw, fs=sr.fs, channel_labels=True)
    eqcs["DESTRIPED"] = viewephys(destriped, title="Destriped", fs=FS)
    eqcs["DESTRIPED"].viewBox_seismic.setYRange(0, raw.shape[0])
    eqcs["DESTRIPED"].viewBox_seismic.setXRange(S0 / 1000, S0 / 1000 + 0.05 * 1000)


    # Get PyKS data
    _ks25_path = one.eid2path(eid).joinpath(f"spike_sorters/pykilosort/{probe}")
    chan_remapping = np.load(_ks25_path / "channel_map.npy")
    spikes, metrics, templates, whitening, whitening_inv = load_phy(_ks25_path)
    template_window = templates.waveforms.shape[1]
    spike_selection = slice(*np.searchsorted(spikes['samples'], [S0, S0 + 30000]))
    sc = spikes['channels'][spike_selection]
    st = ((spikes['samples'][spike_selection] - S0) / sr.fs) * 1000
    ss = spikes["samples"][spike_selection]
    su = spikes["clusters"][spike_selection]
    model = np.zeros(raw.shape)
    units = np.unique(su)
    #units = [368]
    for u in units:
        ind = np.where(su == u)[0]
        amps = spikes["amps_au"][spike_selection][ind]
        for i, e in enumerate(ind):
            if ss[e] - S0 < 50:
                continue
            if ss[e] - S0 > FS - 50:
                continue
            idx = slice(-template_window // 2 + (int(ss[e]) - S0), template_window // 2 + (int(ss[e]) - S0))
            unwhitened_waveform = whitening_inv @ templates.waveforms[u].T
            model[chan_remapping, idx] += amps[i] * unwhitened_waveform[chan_remapping,:]
        # _res = np.zeros(raw.shape)
        # _res[:, spikes["samples"][spike_selection][ind].astype(int)] = amps * np.ones((384, amps.shape[0]))
        # for i in range(res.shape[0]-sr.nsync):
        #     res[i,:] += np.convolve(_res[i,:], templates.waveforms[u, :, i], mode="same")
    #eqc1 = viewephys(res, title="Res", fs=FS)
    #eqc1 = viewephys(raw, title="Raw", fs=FS)
    model *= sr.sample2volts[0]
    res = destriped - model
    eqcs["MODEL_PYKS"] = viewephys(model, title="Model PyKS", fs=sr.fs)
    eqcs["RES_PYKS"] = viewephys(res, title="Residual PyKS", fs=sr.fs)

    #eqc1.ctrl.add_scatter(st, sc, (255, 0, 0, ALPHA), label='KS4')
    #eqc2.ctrl.add_scatter(st, sc, (255, 0, 0, ALPHA), label='KS4')
    #eqc2.ctrl.add_scatter(st[ind]*1000.0, sc[ind], (0, 0, 255, ALPHA), label='KS4')



    if False:
        # Get KS4 data
        _ks4_path = KS4_PATH / pid
        chan_remapping = np.load(_ks4_path / "channel_map.npy")
        spikes, metrics, templates, whitening, whitening_inv = load_phy(_ks4_path, ks4=True)
        template_window = templates.waveforms.shape[1]
        spike_selection = slice(*np.searchsorted(spikes['samples'], [S0, S0 + 30000]))
        sc = spikes['channels'][spike_selection]
        st = ((spikes['samples'][spike_selection] - S0) / sr.fs) * 1000
        ss = spikes["samples"][spike_selection]
        su = spikes["clusters"][spike_selection]
        model = np.zeros(raw.shape)
        units = np.unique(su)
        # units = [368]
        for u in units:
            ind = np.where(su == u)[0]
            amps = spikes["amps"][spike_selection][ind]
            for i, e in enumerate(ind):
                if ss[e] - S0 < 50:
                    continue
                if ss[e] - S0 > FS - 50:
                    continue
                idx = slice(-template_window // 2 + (int(ss[e]) - S0), template_window // 2 + (int(ss[e]) - S0))
                unwhitened_waveform = whitening_inv @ templates.waveforms[u].T
                model[chan_remapping, idx] += amps[i] * unwhitened_waveform
            # _res = np.zeros(raw.shape)
            # _res[:, spikes["samples"][spike_selection][ind].astype(int)] = amps * np.ones((384, amps.shape[0]))
            # for i in range(res.shape[0]-sr.nsync):
            #     res[i,:] += np.convolve(_res[i,:], templates.waveforms[u, :, i], mode="same")
        # eqc1 = viewephys(res, title="Res", fs=FS)
        # eqc1 = viewephys(raw, title="Raw", fs=FS)
        model *= sr.sample2volts[0]
        res = destriped - model
        eqcs["MODEL_KS4"] = viewephys(model, title="Model KS4", fs=sr.fs)
        eqcs["RES_KS4"] = viewephys(res, title="Residual KS4", fs=sr.fs)
        # eqc1.ctrl.add_scatter(st, sc, (255, 0, 0, ALPHA), label='KS4')
        # eqc2.ctrl.add_scatter(st, sc, (255, 0, 0, ALPHA), label='KS4')
        # eqc2.ctrl.add_scatter(st[ind]*1000.0, sc[ind], (0, 0, 255, ALPHA), label='KS4')

    # Get KS2.5 RERUN data
    _ks25_rerun_path = KS25_RERUN_PATH / pid
    chan_remapping = np.load(_ks25_rerun_path / "channel_map.npy")
    spikes, metrics, templates, whitening, whitening_inv = load_phy(_ks25_rerun_path)
    template_window = templates.waveforms.shape[1]
    spike_selection = slice(*np.searchsorted(spikes['samples'], [S0, S0 + 30000]))
    sc = spikes['channels'][spike_selection]
    st = ((spikes['samples'][spike_selection] - S0) / sr.fs) * 1000
    ss = spikes["samples"][spike_selection]
    su = spikes["clusters"][spike_selection]
    model = np.zeros(raw.shape)
    units = np.unique(su)
    # units = [368]
    for u in units:
        ind = np.where(su == u)[0]
        amps = spikes["amps_au"][spike_selection][ind]
        for i, e in enumerate(ind):
            if ss[e] - S0 < 50:
                continue
            if ss[e] - S0 > FS - 50:
                continue
            idx = slice(-template_window // 2 + (int(ss[e]) - S0), template_window // 2 + (int(ss[e]) - S0))
            unwhitened_waveform = whitening_inv @ templates.waveforms[u].T
            model[chan_remapping, idx] += amps[i] * unwhitened_waveform[chan_remapping, :]
        # _res = np.zeros(raw.shape)
        # _res[:, spikes["samples"][spike_selection][ind].astype(int)] = amps * np.ones((384, amps.shape[0]))
        # for i in range(res.shape[0]-sr.nsync):
        #     res[i,:] += np.convolve(_res[i,:], templates.waveforms[u, :, i], mode="same")
    # eqc1 = viewephys(res, title="Res", fs=FS)
    # eqc1 = viewephys(raw, title="Raw", fs=FS)
    model *= sr.sample2volts[0]
    res = destriped - model
    eqcs["MODEL_RERUN"] = viewephys(model, title="Model Rerun", fs=sr.fs)
    eqcs["RES_RERUN"] = viewephys(res, title="Residual Rerun", fs=sr.fs)
    # eqc1.ctrl.add_scatter(st, sc, (255, 0, 0, ALPHA), label='KS4')
    # eqc2.ctrl.add_scatter(st, sc, (255, 0, 0, ALPHA), label='KS4')
    # eqc2.ctrl.add_scatter(st[ind]*1000.0, sc[ind], (0, 0, 255, ALPHA), label='KS4')

    for label, eqc in eqcs.items():
        eqc.viewBox_seismic.setYRange(0, sr.shape[0])
        eqc.viewBox_seismic.setXRange(500, 500 + 0.05 * 1000)
        eqc.ctrl.set_gain(25)
        eqc.resize(1960, 1200)
        eqc.save_current_trace(str(OUT_IMGS_PATH / f"{label}_{pid}.png"))
