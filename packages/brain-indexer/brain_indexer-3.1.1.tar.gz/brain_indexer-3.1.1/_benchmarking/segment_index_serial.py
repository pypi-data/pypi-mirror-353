"""
    Blue Brain Project - Spatial-Index

    A small example script on how to load circuits,
    index them and perform some queries
"""

import os

import numpy as np
from brain_indexer import MorphIndexBuilder
from line_profiler import LineProfiler


# Loading some small circuits and morphology files on BB5
CIRCUIT_2K = "/gpfs/bbp.cscs.ch/project/proj12/jenkins/cellular/circuit-2k"
CIRCUIT_FILE = os.path.join(CIRCUIT_2K, "nodes.h5")
MORPH_FILE = os.path.join(CIRCUIT_2K, "morphologies/ascii")


def do_query_serial(min_corner, max_corner):
    builder = MorphIndexBuilder(MORPH_FILE, CIRCUIT_FILE)
    builder.process_range((700, 100))
    idx = builder.find_intersecting_window(min_corner, max_corner)
    assert len(idx) > 0
    print("Number of elements within window:", len(idx))
    builder.find_nearest(center, 10)
    pos = builder.find_intersecting_window_pos(min_corner, max_corner)
    builder.find_intersecting_window_objs(min_corner, max_corner)
    return idx, pos


if __name__ == "__main__":
    # Defining first and second corner for box query
    min_corner = np.array([-50, 0, 0], dtype=np.float32)
    max_corner = np.array([0, 50, 50], dtype=np.float32)
    center = np.array([0.0, 0.0, 0.0], dtype=np.float32)

    profiler = LineProfiler(do_query_serial)
    idx, pos = profiler.runcall(do_query_serial, min_corner, max_corner)

    # Print resulting IDs and Positions
    for i in range(idx.size):
        gid, section_id, segment_id = idx[i]
        print("Coordinates of gid %d section %d segment %d: %s"
              % (gid, section_id, segment_id, pos[i]))
        if i >= 20:
            print("...")
            break

    # Save results to csv file
    np.savetxt("query_SI_v6.csv", pos, delimiter=",", fmt="%1.3f")

    profiler.print_stats()
