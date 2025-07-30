# ZisaSFC
[![Build Status](https://github.com/1uc/ZisaSFC/actions/workflows/basic_integrity_checks.yml/badge.svg?branch=main)](https://github.com/1uc/ZisaSFC/actions)
[![Docs Status](https://github.com/1uc/ZisaSFC/actions/workflows/publish_docs.yml/badge.svg?branch=main)](https://1uc.github.io/ZisaSFC)

ZisaSFC strives to compute space-filling curves in two and three dimensions.
Currently, in 2D the Hilbert curve and in 3D a generalized Hilbert curve called Luna
\[[1]\] are implemented.

[1]: https://arxiv.org/abs/1109.2323
\[1\]: [https://arxiv.org/abs/1109.2323](https://arxiv.org/abs/1109.2323)

## Quickstart
Start by cloning the repository

    $ git clone --recursive https://github.com/1uc/ZisaSFC.git

and change into the newly created directory. You can simply build using
standard `cmake` commands. There's a build type called `FastDebug` which keeps
asserts and debug symbols but has optimizations turned on.
