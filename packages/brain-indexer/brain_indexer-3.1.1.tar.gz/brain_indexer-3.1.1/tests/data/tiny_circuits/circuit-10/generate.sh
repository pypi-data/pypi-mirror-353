#! /usr/bin/bash

# Morphologies

rm -r tests/data/tiny_circuits/circuit-10/indexes/morphology/{in_memory,multi_index} || true

spatial-index-nodes tests/data/tiny_circuits/circuit-10/nodes.h5 tests/data/tiny_circuits/circuit-10/morphologies/ascii -o tests/data/tiny_circuits/circuit-10/indexes/morphology/in_memory
srun -n3 -A proj12 spatial-index-nodes tests/data/tiny_circuits/circuit-10/nodes.h5 tests/data/tiny_circuits/circuit-10/morphologies/ascii --multi-index -o tests/data/tiny_circuits/circuit-10/indexes/morphology/multi_index

rm -r tests/data/tiny_circuits/circuit-10/indexes/morphology_no_sonata || true
cp -r tests/data/tiny_circuits/circuit-10/indexes/morphology tests/data/tiny_circuits/circuit-10/indexes/morphology_no_sonata
