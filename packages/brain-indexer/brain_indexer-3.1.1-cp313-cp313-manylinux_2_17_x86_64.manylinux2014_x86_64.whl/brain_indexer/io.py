import os
import json
import tempfile
import contextlib

import libsonata

from brain_indexer import logger
from brain_indexer import core


def read_something(filename, command, mode="r", **kwargs):
    with open(filename, mode, **kwargs) as f:
        return command(f)


def write_something(filename, command, mode="w", **kwargs):
    with open(filename, mode=mode, **kwargs) as f:
        command(f)


def read_json(filename):
    return read_something(filename, lambda f: json.load(f))


class NumpyEncoder(json.JSONEncoder):
    # credit: https://stackoverflow.com/a/47626762

    def default(self, obj):
        import numpy as np

        transforms = [
            (np.ndarray, lambda obj: obj.tolist()),
            (np.float16, lambda obj: float(obj)),
            (np.float32, lambda obj: float(obj)),
            (np.float64, lambda obj: float(obj)),
            (np.float128, lambda obj: float(obj)),
            (np.int16, lambda obj: int(obj)),
            (np.int32, lambda obj: int(obj)),
            (np.int64, lambda obj: int(obj)),
        ]

        for T, f in transforms:
            if isinstance(obj, T):
                return f(obj)

        return json.JSONEncoder.default(self, obj)


def write_json(filename, obj):
    write_something(filename, lambda f: json.dump(obj, f, indent=2, cls=NumpyEncoder))


class MetaData:
    _Constants = core._MetaDataConstants

    class _SubConfig:
        def __init__(self, meta_data, sub_config_name):
            self._raw_sub_config = meta_data._raw_meta_data[sub_config_name]
            self._meta_data = meta_data

        @property
        def index_path(self):
            return self._meta_data._meta_data_filename

        def value(self, key):
            return self._raw_sub_config[key]

        def path(self, name):
            # expand path somehow
            return self._meta_data.resolve_path(self._raw_sub_config[name])

    class _MultiPopulationConfig:
        def __init__(self, meta_data):
            self._raw_sub_config = meta_data._raw_meta_data["multi_population"]
            self._meta_data = meta_data

        @property
        def index_paths(self):
            raw_populations = self._raw_sub_config["populations"]
            return {
                pop: self._meta_data.resolve_path(pop_conf["index_path"])
                for pop, pop_conf in raw_populations.items()
            }

    def __init__(self, path):
        self._meta_data_filename = self._deduce_meta_data_filename(path)
        self._raw_meta_data = read_json(self._meta_data_filename)
        self._dirname = os.path.dirname(self._meta_data_filename)

    @property
    def element_type(self):
        return self._raw_meta_data["element_type"]

    @property
    def index_variant(self):
        known_index_variants = [
            MetaData._Constants.in_memory_key,
            MetaData._Constants.multi_index_key
        ]

        variants = list(
            filter(lambda k: k in self._raw_meta_data, known_index_variants)
        )

        assert len(variants) == 1, "A meta data file can't have multiple index variants."
        return variants[0]

    @property
    def extended(self):
        return self._sub_config("extended")

    @property
    def in_memory(self):
        return self._sub_config(MetaData._Constants.in_memory_key)

    @property
    def multi_index(self):
        return self._sub_config(MetaData._Constants.multi_index_key)

    @property
    def multi_population(self):
        if "multi_population" in self._raw_meta_data:
            return self._MultiPopulationConfig(self)

    def resolve_path(self, path):
        return os.path.join(self._dirname, path)

    def _sub_config(self, sub_config_name):
        if sub_config_name in self._raw_meta_data:
            return MetaData._SubConfig(self, sub_config_name)

    def _deduce_meta_data_filename(self, path):
        return core.deduce_meta_data_path(path)


def open_core_from_meta_data(meta_data, *, max_cache_size_mb=None, resolver=None):
    if in_memory_conf := meta_data.in_memory:
        return resolver.core_class("in_memory")(in_memory_conf.index_path)

    elif multi_index_conf := meta_data.multi_index:
        max_cache_size_mb = max_cache_size_mb or 1024
        mem = 1024 ** 2 * max_cache_size_mb

        return resolver.core_class("multi_index")(
            multi_index_conf.index_path, max_cached_bytes=mem
        )

    else:
        raise ValueError("Invalid 'meta_data'.")


def _open_sonata_dataset(sonata_filename, population_name, storage_class):
    storage = storage_class(sonata_filename)
    if population_name is None:
        if len(storage.population_names) > 1:
            raise RuntimeError("No population chosen, multiple available")
        population_name = next(iter(storage.population_names), None)
        logger.info(
            f"Population not set. Auto-selecting: '{population_name}'."
        )

    return storage.open_population(population_name)


def open_sonata_edges(sonata_filename, population_name):
    return _open_sonata_dataset(sonata_filename, population_name, libsonata.EdgeStorage)


def open_sonata_nodes(sonata_filename, population_name):
    return _open_sonata_dataset(sonata_filename, population_name, libsonata.NodeStorage)


def _validated_sonata_population_name(sonata_dataset, population_name):
    population_names = sonata_dataset.population_names

    if population_name is not None:
        message = f"Population '{population_name}' not found."
        assert population_name in population_names, message

    else:
        message = "Multiple populations but no population was selected."
        assert len(population_names) == 1, message

        population_name = next(iter(population_names))

    return population_name


def validated_sonata_nodes_population_name(nodes_file, population_name):
    nodes = libsonata.NodeStorage(nodes_file)
    return _validated_sonata_population_name(nodes, population_name)


def validated_sonata_edges_population(edges_file, population_name):
    edges = libsonata.EdgeStorage(edges_file)
    return _validated_sonata_population_name(edges, population_name)


def write_sonata_meta_data_section(index_path, edge_filename, population_name):
    meta_data_path = core.deduce_meta_data_path(index_path)
    meta_data = read_json(meta_data_path)
    meta_data["extended"] = {
        "dataset_path": os.path.abspath(edge_filename),
        "population": population_name,
    }

    write_json(meta_data_path, meta_data)


def write_multi_population_meta_data(index_path, element_type, populations):
    meta_data_path = core.default_meta_data_path(index_path)

    multi_population_conf = {
        "populations": {}
    }

    for pop in populations:
        multi_population_conf["populations"][pop] = {"index_path": pop}

    meta_data = {
        "version": MetaData._Constants.version,
        "element_type": element_type,
        "multi_population": multi_population_conf,
    }

    write_json(meta_data_path, meta_data)


@contextlib.contextmanager
def shared_temporary_directory(*args, mpi_comm=None, **kwargs):
    """An MPI compatible wrapper for the context manager 'TemporaryDirectory'.

    Will act like a context manager to create a temporary directory on a shared
    filesystem. When using MPI, we don't want every MPI rank to create their own
    temporary directory, but rather we want them to share the same directory.

    Note, any positional arguments and any keyword arguments other than `mpi_comm`
    are passed to `TemporaryDirectory`.

    If `mpi_comm` is `None` then we assume this a sequential run and doesn't use
    MPI, i.e. is equivalent to `TemporaryDirectory`.

    Examples:

        with shared_temporary_directory(prefix="foo", mpi_comm=comm) as tmp_dir:
            print(tmp_dir)
    """

    mpi_rank = mpi_comm.Get_rank() if mpi_comm is not None else 0

    if mpi_rank == 0:
        with tempfile.TemporaryDirectory(*args, **kwargs) as tmp_dir:
            if mpi_comm is not None:
                mpi_comm.bcast(tmp_dir, root=0)

            yield tmp_dir

    else:
        assert mpi_comm is not None

        tmp_dir = mpi_comm.bcast(None, root=0)
        yield tmp_dir
