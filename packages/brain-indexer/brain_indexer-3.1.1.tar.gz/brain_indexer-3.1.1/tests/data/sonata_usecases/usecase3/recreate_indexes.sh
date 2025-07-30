#! /usr/bin/env bash


output_dir=indexes/morphology/in_memory
rm -r ${output_dir}
spatial-index-circuit segments circuit_sonata.json \
    --populations NodeA NodeB \
    -o ${output_dir}

output_dir=indexes/synapse/in_memory
rm -r ${output_dir}
spatial-index-circuit synapses circuit_sonata.json \
    --populations NodeA__NodeA__chemical NodeB__NodeB__chemical \
    -o ${output_dir}
