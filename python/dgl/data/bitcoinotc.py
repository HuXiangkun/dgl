"""  """
import numpy as np
import os
import datetime

from .dgl_dataset import DGLBuiltinDataset
from .utils import deprecate_class, download, extract_archive, save_graphs, load_graphs, check_sha1
from ..graph import DGLGraph


class BitcoinOTCDataset(DGLBuiltinDataset):
    r"""BitcoinOTC dataset for fraud detection

    This is who-trusts-whom network of people who trade using Bitcoin on
    a platform called Bitcoin OTC. Since Bitcoin users are anonymous,
    there is a need to maintain a record of users' reputation to prevent
    transactions with fraudulent and risky users.

    Offical website: https://snap.stanford.edu/data/soc-sign-bitcoin-otc.html

    Parameters
    ----------
    raw_dir : str
        Raw file directory to download/contains the input data directory.
        Default: ~/.dgl/
    force_reload : bool
        Whether to reload the dataset. Default: False
    verbose: bool
        Whether to print out progress information. Default: True.

    Returns
    -------
    BitcoinOTCDataset object with two properties:
        graphs: list of DGLGraph objects each contains the graph structure and edge features
            - edata['h']: edge feature
        is_temporal: bool, is temporal graph

    Examples
    --------
    >>> data = BitcoinOTCDataset()
    >>> for g in data:
    ....    # get edge feature
    ....    e_feat = g.edata['h']
    ....    # your code here
    >>>
    """

    _url = 'https://snap.stanford.edu/data/soc-sign-bitcoinotc.csv.gz'
    _sha1_str = 'c14281f9e252de0bd0b5f1c6e2bae03123938641'

    def __init__(self, raw_dir=None, force_reload=False, verbose=False):
        super(BitcoinOTCDataset, self).__init__(name='bitcoinotc',
                                                url=self._url,
                                                raw_dir=raw_dir,
                                                force_reload=force_reload,
                                                verbose=verbose)

    def download(self):
        gz_file_path = os.path.join(self.raw_dir, self.name + '.csv.gz')
        download(self.url, path=gz_file_path)
        if not check_sha1(gz_file_path, self._sha1_str):
            raise UserWarning('File {} is downloaded but the content hash does not match.'
                              'The repo may be outdated or download may be incomplete. '
                              'Otherwise you can create an issue for it.'.format(self.name + '.csv.gz'))
        extract_archive(gz_file_path, self.raw_path)

    def process(self, root_path):
        filename = os.path.join(root_path, self.name + '.csv')
        data = np.loadtxt(filename, delimiter=',').astype(np.int64)
        data[:, 0:2] = data[:, 0:2] - data[:, 0:2].min()
        num_nodes = data[:, 0:2].max() - data[:, 0:2].min() + 1
        delta = datetime.timedelta(days=14).total_seconds()
        # The source code is not released, but the paper indicates there're
        # totally 137 samples. The cutoff below has exactly 137 samples.
        time_index = np.around(
            (data[:, 3] - data[:, 3].min()) / delta).astype(np.int64)

        self._graphs = []
        for i in range(time_index.max()):
            g = DGLGraph()
            g.add_nodes(num_nodes)
            row_mask = time_index <= i
            edges = data[row_mask][:, 0:2]
            rate = data[row_mask][:, 2]
            g.add_edges(edges[:, 0], edges[:, 1])
            g.edata['h'] = rate.reshape(-1, 1)
            self._graphs.append(g)

    def has_cache(self):
        graph_path = os.path.join(self.save_path, 'dgl_graph.bin')
        return os.path.exists(graph_path)

    def save(self):
        graph_path = os.path.join(self.save_path, 'dgl_graph.bin')
        save_graphs(graph_path, self.graphs)

    def load(self):
        graph_path = os.path.join(self.save_path, 'dgl_graph.bin')
        self._graphs = load_graphs(graph_path)[0]

    @property
    def graphs(self):
        return self._graphs

    def __len__(self):
        return len(self.graphs)

    def __getitem__(self, item):
        return self.graphs[item]

    @property
    def is_temporal(self):
        return True


class BitcoinOTC(BitcoinOTCDataset):
    def __init__(self):
        deprecate_class('BitcoinOTC', 'BitcoinOTCDataset')
        super(BitcoinOTC, self).__init__()

