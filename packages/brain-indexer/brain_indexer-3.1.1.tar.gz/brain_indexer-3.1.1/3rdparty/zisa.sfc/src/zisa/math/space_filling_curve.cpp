// SPDX-License-Identifier: MIT
// Copyright (c) 2021 ETH Zurich, Luc Grosheintz-Laval

#include <zisa/math/space_filling_curve.hpp>

namespace zisa {

std::bitset<2> hilbert_transform(const std::bitset<2> &digits,
                                 std::array<unsigned short, 4> &sigma) {

  auto tile = sigma[digits.to_ulong()];

  auto tau = [](auto tile) {
    if (tile == 0) {
      return std::array<unsigned short, 4>{0, 3, 2, 1};
    }

    if (tile == 3) {
      return std::array<unsigned short, 4>{2, 1, 0, 3};
    }

    return std::array<unsigned short, 4>{0, 1, 2, 3};
  }(tile);

  for (unsigned short i = 0; i < 4; ++i) {
    sigma[i] = tau[sigma[i]];
  }

  return std::bitset<2>(tile);
}

namespace three_dimensional {

PolyHilbertTable luna_curve() {
  return {{{PolyHilbertState{/* q0 */ {0, 2, 1, 3, 4, 6, 5, 7}, 1},
            PolyHilbertState{/* q1 */ {3, 7, 2, 6, 1, 5, 0, 4}, 1},
            PolyHilbertState{/* q2 */ {6, 7, 2, 3, 4, 5, 0, 1}, 1},
            PolyHilbertState{/* q3 */ {0, 1, 2, 3, 4, 5, 6, 7}, 1},

            PolyHilbertState{/* q4 */ {6, 2, 4, 0, 7, 3, 5, 1}, 0},
            PolyHilbertState{/* q5 */ {3, 7, 1, 5, 2, 6, 0, 4}, 0},
            PolyHilbertState{/* q6 */ {5, 1, 7, 3, 4, 0, 6, 2}, 1},
            PolyHilbertState{/* q7 */ {6, 4, 2, 0, 7, 5, 3, 1}, 1}},

           {PolyHilbertState{/* q0 */ {0, 2, 1, 3, 4, 6, 5, 7}, 1},
            PolyHilbertState{/* q1 */ {3, 1, 2, 0, 7, 5, 6, 4}, 1},
            PolyHilbertState{/* q2 */ {6, 7, 2, 3, 4, 5, 0, 1}, 1},
            PolyHilbertState{/* q3 */ {0, 1, 2, 3, 4, 5, 6, 7}, 0},

            PolyHilbertState{/* q4 */ {6, 2, 4, 0, 7, 3, 5, 1}, 0},
            PolyHilbertState{/* q5 */ {0, 4, 1, 5, 2, 6, 3, 7}, 0},
            PolyHilbertState{/* q6 */ {5, 1, 7, 3, 4, 0, 6, 2}, 1},
            PolyHilbertState{/* q7 */ {0, 4, 2, 6, 1, 5, 3, 7}, 1}}},
          {{0, 7, 3, 4, 1, 6, 2, 5}, {0, 5, 3, 4, 1, 6, 2, 7}}};
}

std::bitset<3> hilbert_transform(const std::bitset<3> &xy,
                                 PolyHilbertState &state,
                                 PolyHilbertTable &table) {

  auto octant = xy.to_ulong();
  auto &[sigma, c] = state;

  auto rot_octant = sigma[octant];

  const auto &tau = std::get<0>(table.state_transform[c][rot_octant]);
  const auto &generator = table.generators[c];
  c = std::get<1>(table.state_transform[c][rot_octant]);

  for (unsigned short i = 0; i < 8; ++i) {
    sigma[i] = tau[sigma[i]];
  }

  return std::bitset<3>(generator[rot_octant]);
}

}
}