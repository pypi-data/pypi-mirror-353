#! /usr/bin/bash

## Synapses

rm -r tests/data/tiny_circuits/syn-2k/indexes/synapse/in_memory || true
spatial-index-synapses tests/data/tiny_circuits/syn-2k/edges.h5 -o tests/data/tiny_circuits/syn-2k/indexes/synapse/in_memory

rm -r tests/data/tiny_circuits/syn-2k/indexes/synapse/multi_index || true
srun -n3 -A proj12 spatial-index-synapses tests/data/tiny_circuits/syn-2k/edges.h5 --multi-index -o tests/data/tiny_circuits/syn-2k/indexes/synapse/multi_index

rm -r tests/data/tiny_circuits/syn-2k/indexes/synapse_no_sonata || true
cp -r tests/data/tiny_circuits/syn-2k/indexes/synapse tests/data/tiny_circuits/syn-2k/indexes/synapse_no_sonata
