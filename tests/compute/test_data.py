import dgl.data as data


@unittest.skipIf(F._default_context_str == 'gpu', reason="Datasets don't need to be tested on GPU.")
def test_minigc():
    ds = data.MiniGCDataset(16, 10, 20)
    g, l = list(zip(*ds))
    print(g, l)


@unittest.skipIf(F._default_context_str == 'gpu', reason="Datasets don't need to be tested on GPU.")
def test_gin():
    ds_n_graphs = {
        'MUTAG': 188,
        'COLLAB': 5000,
        'IMDBBINARY': 1000,
        'IMDBMULTI': 1500,
        'NCI1': 4110,
        'PROTEINS': 1113,
        'PTC': 344,
        'REDDITBINARY': 2000,
        'REDDITMULTI5K': 4999
    }
    for name, n_graphs in ds_n_graphs.items():
        ds = data.GINDataset(name, self_loop=False, degree_as_nlabel=False)
        assert len(ds) == n_graphs, (len(ds), name)
        ds = data.GINDataset(name, self_loop=True, degree_as_nlabel=False)
        assert len(ds) == n_graphs, (len(ds), name)
        ds = data.GINDataset(name, self_loop=False, degree_as_nlabel=True)
        assert len(ds) == n_graphs, (len(ds), name)
        ds = data.GINDataset(name, self_loop=True, degree_as_nlabel=True)
        assert len(ds) == n_graphs, (len(ds), name)


@unittest.skipIf(F._default_context_str == 'gpu', reason="Datasets don't need to be tested on GPU.")
def test_data_hash():
    class HashTestDataset(data.DGLDataset):
        def __init__(self, hash_key=()):
            super(HashTestDataset, self).__init__('hashtest', hash_key=hash_key)
        def _load(self):
            pass

    a = HashTestDataset((True, 0, '1', (1,2,3)))
    b = HashTestDataset((True, 0, '1', (1,2,3)))
    c = HashTestDataset((True, 0, '1', (1,2,4)))
    assert a.hash == b.hash
    assert a.hash != c.hash

if __name__ == '__main__':
    test_minigc()
    test_gin()
    test_data_hash()
