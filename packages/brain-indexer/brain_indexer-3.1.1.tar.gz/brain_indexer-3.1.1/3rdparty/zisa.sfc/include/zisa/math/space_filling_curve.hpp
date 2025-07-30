// SPDX-License-Identifier: MIT
// Copyright (c) 2021 ETH Zurich, Luc Grosheintz-Laval

#ifndef ZISA_SPACE_FILLING_CURVE_HPP_XYGQB
#define ZISA_SPACE_FILLING_CURVE_HPP_XYGQB

#include <cassert>
#include <array>
#include <bitset>
#include <vector>
#include <tuple>

namespace zisa {

template <int N>
std::bitset<N> binary_digits(double x) {
  auto digits = std::bitset<N>{};

  assert(x >= 0);
  assert(x < 1.0);

  for (int i = N - 1; i >= 0; --i) {
    if (x < 0.5) {
      digits[i] = false;
      x = 2.0 * x;
    } else {
      digits[i] = true;
      x = 2.0 * (x - 0.5);
    }
  }

  return digits;
}

std::bitset<2> hilbert_transform(const std::bitset<2> &digits,
                                 std::array<unsigned short, 4> &sigma);

template <int N>
std::bitset<2 * N> hilbert_index(const std::bitset<2 * N> &coords) {
  std::bitset<2 * N> index;
  std::array<unsigned short, 4> sigma = {0, 3, 1, 2};

  for (int i = N - 1; i >= 0; --i) {
    std::bitset<2> xy;
    xy[1] = coords[i * 2 + 1];
    xy[0] = coords[i * 2];

    auto digits = hilbert_transform(xy, sigma);

    index[i * 2 + 1] = digits[1];
    index[i * 2] = digits[0];
  }

  return index;
}

template <int N>
std::bitset<2 * N> hilbert_index(double x, double y) {
  auto x_digits = binary_digits<N>(x);
  auto y_digits = binary_digits<N>(y);

  auto coords = std::bitset<2 * N>{};
  for (int i = 0; i < N; ++i) {
    coords[2 * i] = x_digits[i];
    coords[2 * i + 1] = y_digits[i];
  }

  return hilbert_index<N>(coords);
}

template <int N>
std::bitset<2 * N> hilbert_index(std::array<double, 2> xy) {
  auto [x, y] = xy;
  return hilbert_index<N>(x, y);
}

namespace three_dimensional {
using PolyHilbertState
    = std::tuple<std::array<unsigned short, 8>, unsigned short>;

/// Permutation and generators of poly-Hilbert curves.
/** Hilbert curves can be generated recursively applying transformations of a
   fixed number of basic traversal patterns of all 8 vertices of a cube. The
   basic pattern is stored in `generators`. Additionally, a generator also
   defines the order in which each of the 8 subcubes should be traversed. Since,
   these are either rotations or reflections of one of the basic traversal
   pattern, we store, for each generator, a permutation and the index of the
   basic pattern.

   The permutation must be applied to the corners of the subcube before applying
   the basic pattern to determine the Hilbert index.
 */
struct PolyHilbertTable {
  std::vector<std::array<PolyHilbertState, 8>> state_transform;
  std::vector<std::array<unsigned short, 8>> generators;
};

/// A 3D Hilbert curve with near optimal properties.
/** Source: Haverkort, 2011, arXiv:1109.2323v2
 */
PolyHilbertTable luna_curve();

std::bitset<3> hilbert_transform(const std::bitset<3> &xy,
                                 PolyHilbertState &state,
                                 PolyHilbertTable &table);

template <int N>
std::bitset<3 * N> hilbert_index(const std::bitset<3 * N> &coords) {
  auto table = luna_curve();

  std::bitset<3 * N> index;
  auto state = PolyHilbertState{{0, 1, 2, 3, 4, 5, 6, 7}, 0};

  for (int i = N - 1; i >= 0; --i) {
    std::bitset<3> xyz;
    xyz[2] = coords[i * 3 + 2];
    xyz[1] = coords[i * 3 + 1];
    xyz[0] = coords[i * 3];

    auto digits = hilbert_transform(xyz, state, table);

    index[i * 3 + 2] = digits[2];
    index[i * 3 + 1] = digits[1];
    index[i * 3] = digits[0];
  }

  return index;
}
}

template <int N>
std::bitset<3 * N> hilbert_index(double x, double y, double z) {
  auto x_digits = binary_digits<N>(x);
  auto y_digits = binary_digits<N>(y);
  auto z_digits = binary_digits<N>(z);

  auto coords = std::bitset<3 * N>{};
  for (int i = 0; i < N; ++i) {
    coords[3 * i] = x_digits[i];
    coords[3 * i + 1] = y_digits[i];
    coords[3 * i + 2] = z_digits[i];
  }

  return three_dimensional::hilbert_index<N>(coords);
}

template <int N>
std::bitset<3 * N> hilbert_index(std::array<double, 3> xyz) {
  auto [x, y, z] = xyz;
  return hilbert_index<N>(x, y, z);
}

}
#endif // ZISA_SPACE_FILLING_CURVE_HPP
