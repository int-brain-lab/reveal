import gc

import scipy
import numpy as np
from pathlib import Path
import logging

from PIL import Image


from one.api import ONE
from brainbox.io.spikeglx import Streamer
from brainbox.io.one import SessionLoader, SpikeSortingLoader
from viewephys.gui import viewephys
from neurodsp.voltage import destripe
from iblatlas.regions import BrainRegions
from iblutil.numerical import ismember
from one.alf.exceptions import ALFObjectNotFound

logger = logging.getLogger(__name__)
REVEAL_PATH = Path.home().joinpath('Documents/JS/reveal.js')


class Presentation(object):
    """
    prez = Presentation(name='prez')
    """
    def __init__(self, name, path_reveal=REVEAL_PATH):
        self.name = name  # this is the name of the presentation
        self.list_buffer = []
        self.path_reveal = path_reveal
        self.path_images = Path(path_reveal).joinpath('images', name)
        self.path_images.mkdir(parents=True, exist_ok=True)

    def _convert_image(self, full_path_image, clobber=True):
        jpg_image = Path(self.path_images).joinpath(Path(full_path_image).name).with_suffix('.jpg')
        if clobber or not jpg_image.exists():
            pimg = Image.open(full_path_image)
            pimg.convert('RGB').save(jpg_image)
        return jpg_image.name

    def new_section(self):
        self.list_buffer.append("<section>\n")

    def close_section(self):
        self.list_buffer.append("</section>\n")

    def add_slide(self, **kwargs):
        # if 2 pictures, add slide compare, if one, add slide
        # TODO
        pass

    def add_slide_image(self, full_path_image, title=None, post=''):
        img_name = self._convert_image(full_path_image)
        if title is None:
            title = img_name
        str_slide = f"""
        <section>
            <p>{title}</p>
            <img data-src=images/{self.name}/{img_name}>
        {post}</section>
        """
        self.list_buffer.append(str_slide)

    def add_slide_compare(self, full_path_image1, full_path_image2, title=None, post=''):
        img_name1 = self._convert_image(full_path_image1)
        img_name2 = self._convert_image(full_path_image2)
        if title is None:
            title = img_name1
        str_slide = f"""
        <section>
            <p>{title}</p>
            <div class="r-stack"><div class="compare">
                <img data-src=images/{self.name}/{img_name1}>
                <img data-src=images/{self.name}/{img_name2}>
            </div></div>
        {post}</section>
        """
        self.list_buffer.append(str_slide)

    def build(self, theme='white', title=None):
        """Build reveal.js index.html file"""
        file_index_template = self.path_reveal.joinpath('index_template.html')
        file_presentation = self.path_reveal.joinpath(f'{self.name}.html')

        title = title or self.name
        with open(file_index_template, 'r') as f:
            template = f.read()

        html = template.replace("{% theme %}", theme)
        html = html.replace("{% title %}", title)
        html = html.replace("{% slides %}", ''.join(self.list_buffer))

        with open(file_presentation, 'w+') as f:
            f.write(html)


def make_raster_plot(path_qc, pid, one=None, regions=None, clobber=False):
    """
        For a given PID, outputs a set of pictures in the path_qc folder. Example for:
    -   febb430e-2d50-4f83-87a0-b5ffbb9a4943_2020-02-27_1_DY_009_probe00_raster_good_units.png
    -   febb430e-2d50-4f83-87a0-b5ffbb9a4943_2020-02-27_1_DY_009_probe00_raster.png
    :param path_qc:
    :param pid:
    :param one:
    :param regions:
    :param clobber:
    :return:
    """
    if len(list(path_qc.glob(f"{pid}*raster*.png"))) >= 2 and clobber is False:
        print(pid, 'skip')
        return
    gc.collect()
    one = one or ONE()

    eid, pname = one.pid2eid(pid)
    sl = SessionLoader(one=one, eid=eid)
    try:
        sl.load_trials()
    except ALFObjectNotFound:
        sl.trials = None

    # load data
    ssl = SpikeSortingLoader(pid=pid, one=one)
    spikes, clusters, channels = ssl.load_spike_sorting(dataset_types=['spikes.samples'])
    if len(spikes) == 0:
        logger.warning(f"{pid} doesn't have spike sorting - no raster available")
        return
    clusters = ssl.merge_clusters(spikes, clusters, channels)
    good_units = clusters['label'] == 1
    isok, _ = ismember(spikes['clusters'], clusters['cluster_id'][good_units])

    tbounds = [sl.trials['intervals_0'].iloc[0], sl.trials['intervals_1'].iloc[-1]]
    sbounds = np.array(ssl.samples2times(tbounds, direction='reverse'))

    # compute rasters
    fs = 1 / np.diff(ssl.samples2times([0, 1]))[0]
    if (next(path_qc.glob(f'{pid}*_raster_good_units.png'), None) is None or clobber) and np.sum(good_units) > 0:
        ssl.raster({k: spikes[k][isok] for k in spikes}, channels, br=regions,  save_dir=path_qc,
                   label='raster_good_units', time_series={'trials': sbounds / fs})
    if next(path_qc.glob(f'{pid}*_raster.png'), None) is None or clobber:
        ssl.raster(spikes, channels, save_dir=path_qc, br=regions, time_series={'trials': sbounds / fs})


def make_rawdata_plot(path_qc, pid, one=None, regions=None, clobber=False, cache_dir=None,
                      spikes=None, clusters=None, channels=None):
    """
        For a given PID, outputs a set of pictures in the path_qc folder. Example for:
    -   febb430e-2d50-4f83-87a0-b5ffbb9a4943_2020-02-27_1_DY_009_probe00_raw_T0600.jpg
    -   febb430e-2d50-4f83-87a0-b5ffbb9a4943_2020-02-27_1_DY_009_probe00_raw_T1800.jpg
    -   febb430e-2d50-4f83-87a0-b5ffbb9a4943_2020-02-27_1_DY_009_probe00_raw_T3000.jpg
    :param path_qc:
    :param pid:
    :param one:
    :param regions:
    :param clobber:
    :return: a list of output png full paths
    """
    # this is the path containing the metrics and clusters tables for fast releoading
    CACHE_DIR = cache_dir or Path(path_qc).joinpath('cache')
    CACHE_DIR.mkdir(exist_ok=True, parents=True)
    V_T0 = [600, 60 * 30, 60 * 50]  # sample at 10, 30, 50 min in
    N_SEC_LOAD = 1
    DISPLAY_TIME = 0.05  # second
    butter_kwargs = {'N': 3, 'Wn': 300 / 30000 * 2, 'btype': 'highpass'}
    regions = regions or BrainRegions()
    sos = scipy.signal.butter(**butter_kwargs, output='sos')

    if spikes is None:
        ssl = SpikeSortingLoader(pid=pid, one=one)
        spikes, clusters, channels = ssl.load_spike_sorting(dataset_types=['spikes.samples'])
        clusters = ssl.merge_clusters(spikes, clusters, channels)
        stub = f"{pid}_{ssl.pid2ref}"
    
    output_files = []
    eqcs = {}
    for T0 in V_T0:
        if len(list(path_qc.glob(f"{stub}_*_T{T0:04d}.png"))) == 2:
            continue
        sr = Streamer(pid=pid, one=one, remove_cached=False, typ='ap', cache_folder=CACHE_DIR)
        start = int(T0 * sr.fs)
        end = int((T0 + N_SEC_LOAD) * sr.fs)
        if end > sr.ns:
            continue
        raw = sr[start:end, :-sr.nsync].T
        raw = scipy.signal.sosfiltfilt(sos, raw)
        eqcs['raw'] = viewephys(raw, sr.fs, br=regions, title='raw', channels=channels)
        eqcs['destripe'] = viewephys(destripe(raw, fs=sr.fs, channel_labels=True)
                                     , sr.fs, br=regions, title='destripe', channels=channels)

        for label, eqc in eqcs.items():
            if len(spikes) != 0:
                spike_selection = slice(*np.searchsorted(spikes['samples'], [start, end]))
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
            output_file = path_qc.joinpath(f"{stub}_{label}_T{T0:04d}.png")
            output_files.append(output_file)
            eqc.grab().save(str(output_file))
            eqc.close()
    return output_files
