// SPDX-License-Identifier: MIT
// Copyright (c) 2021 ETH Zurich, Luc Grosheintz-Laval

#include <catch2/catch_test_macros.hpp>

#include <iostream>

#include <vector>
#include <zisa/math/space_filling_curve.hpp>

TEST_CASE("Space Filling Curve; basics", "[math][sfc]") {

  REQUIRE(zisa::binary_digits<4>(0.25) == std::bitset<4>("0100"));
  REQUIRE(zisa::binary_digits<4>(0.5) == std::bitset<4>("1000"));
  REQUIRE(zisa::binary_digits<4>(0.75) == std::bitset<4>("1100"));
  REQUIRE(zisa::binary_digits<4>(0.625) == std::bitset<4>("1010"));
  REQUIRE(zisa::binary_digits<4>(0.9999) == std::bitset<4>("1111"));
  REQUIRE(zisa::binary_digits<4>(0.00001) == std::bitset<4>("0000"));

  REQUIRE(std::bitset<6>(42) == std::bitset<6>("101010"));
  auto forty_two = std::bitset<6>(42);
  REQUIRE(forty_two[0] == 0);
  REQUIRE(forty_two[1] == 1);
  REQUIRE(forty_two[2] == 0);
  REQUIRE(forty_two[3] == 1);
  REQUIRE(forty_two[4] == 0);
  REQUIRE(forty_two[5] == 1);

  auto level2 = std::vector<std::tuple<std::bitset<4>, std::bitset<4>>>{
      {std::bitset<4>("0000"), std::bitset<4>("0000")},
      {std::bitset<4>("0001"), std::bitset<4>("0001")},
      {std::bitset<4>("0100"), std::bitset<4>("1110")},
      {std::bitset<4>("0101"), std::bitset<4>("1111")},

      {std::bitset<4>("0010"), std::bitset<4>("0011")},
      {std::bitset<4>("0011"), std::bitset<4>("0010")},
      {std::bitset<4>("0110"), std::bitset<4>("1101")},
      {std::bitset<4>("0111"), std::bitset<4>("1100")},

      {std::bitset<4>("1000"), std::bitset<4>("0100")},
      {std::bitset<4>("1001"), std::bitset<4>("0111")},
      {std::bitset<4>("1100"), std::bitset<4>("1000")},
      {std::bitset<4>("1101"), std::bitset<4>("1011")},

      {std::bitset<4>("1010"), std::bitset<4>("0101")},
      {std::bitset<4>("1011"), std::bitset<4>("0110")},
      {std::bitset<4>("1110"), std::bitset<4>("1001")},
      {std::bitset<4>("1111"), std::bitset<4>("1010")}};

  for (auto [in, out] : level2) {
    REQUIRE(zisa::hilbert_index<2>(in) == out);
  }

  auto level3 = std::vector<std::tuple<std::bitset<6>, std::bitset<6>>>{
      {std::bitset<6>("011000"), std::bitset<6>("110110")},
      {std::bitset<6>("011001"), std::bitset<6>("110111")},
      {std::bitset<6>("011010"), std::bitset<6>("110101")},
      {std::bitset<6>("011011"), std::bitset<6>("110100")},
  };

  for (auto [in, out] : level3) {
    REQUIRE(zisa::hilbert_index<3>(in) == out);
  }

  auto xy_l2 = std::vector<std::bitset<4>>{std::bitset<4>("0000"),
                                           std::bitset<4>("0001"),
                                           std::bitset<4>("1110"),
                                           std::bitset<4>("1111"),

                                           std::bitset<4>("0011"),
                                           std::bitset<4>("0010"),
                                           std::bitset<4>("1101"),
                                           std::bitset<4>("1100"),

                                           std::bitset<4>("0100"),
                                           std::bitset<4>("0111"),
                                           std::bitset<4>("1000"),
                                           std::bitset<4>("1011"),

                                           std::bitset<4>("0101"),
                                           std::bitset<4>("0110"),
                                           std::bitset<4>("1001"),
                                           std::bitset<4>("1010")};

  for (int j = 0; j < 4; ++j) {
    double y = (2.0 * j + 1.0) / 8.0;

    for (int i = 0; i < 4; ++i) {
      double x = (2.0 * i + 1.0) / 8.0;

      REQUIRE(zisa::hilbert_index<2>(x, y) == xy_l2[i + 4 * j]);
    }
  }
}

TEST_CASE("Space Filling Curve 3D; basics", "[math][sfc]") {
  auto level1 = std::vector<std::tuple<std::bitset<3>, std::bitset<3>>>{
      {std::bitset<3>("000"), std::bitset<3>("000")},
      {std::bitset<3>("001"), std::bitset<3>("111")},
      {std::bitset<3>("010"), std::bitset<3>("011")},
      {std::bitset<3>("011"), std::bitset<3>("100")},
      {std::bitset<3>("100"), std::bitset<3>("001")},
      {std::bitset<3>("101"), std::bitset<3>("110")},
      {std::bitset<3>("110"), std::bitset<3>("010")},
      {std::bitset<3>("111"), std::bitset<3>("101")},
  };

  for (auto [in, out] : level1) {
    REQUIRE(zisa::three_dimensional::hilbert_index<1>(in) == out);
  }

  auto level2 = std::vector<std::tuple<std::bitset<6>, std::bitset<6>>>{
      {std::bitset<6>("110101"), std::bitset<6>("010000")},
      {std::bitset<6>("110110"), std::bitset<6>("010010")},
      {std::bitset<6>("111111"), std::bitset<6>("101101")}};

  for (auto [in, out] : level2) {
    REQUIRE(zisa::three_dimensional::hilbert_index<2>(in) == out);
  }
}

template <size_t n_dims>
static std::array<double, n_dims> box_center(std::array<int, n_dims> i, int n) {
  auto x = std::array<double, n_dims>{};
  for (size_t k = 0; k < n_dims; ++k) {
    x[k] = (i[k] + 0.5) / n;
  }

  return x;
}

bool is_safe_dir(int i, int n) { return 0 <= i && i < n; };

template <size_t n_dims>
bool is_safe_dir(std::array<int, n_dims> i, int n) {
  for (size_t k = 0; k < n_dims; ++k) {
    if (!is_safe_dir(i[k], n)) {
      return false;
    }
  }

  return true;
};

template<size_t n_dims>
int count_cells(int n) {
  int N = 1;
  for(size_t k = 0; k < n_dims; k++) {
    N *= n;
  }

  return N;
}

template <size_t n_dims>
std::vector<std::array<int, n_dims>> all_multi_indexes(int n) {
  auto N = count_cells<n_dims>(n);
  std::vector<std::array<int, n_dims>> i(N);

  for (size_t j = 0; j < i.size(); ++j) {
    int ld = 1;
    for (size_t k = 0; k < n_dims; ++k) {
      i[j][k] = (j / ld) % n;
      ld *= n;
    }
  }

  return i;
}

template <size_t n_dims>
std::array<int, n_dims> add_multi_indexes(const std::array<int, n_dims> &i,
                                          const std::array<int, n_dims> &j) {
  auto ipj = std::array<int, n_dims>{};
  for (size_t k = 0; k < n_dims; ++k) {
    ipj[k] = i[k] + j[k];
  }

  return ipj;
}

template<size_t n_dims, int n_levels>
void check_sfc_is_continuous(const std::vector<std::array<int, n_dims>>& cardinal_directions) {
  int n = 1 << n_levels;

  auto multi_indexes = all_multi_indexes<n_dims>(n);
  for (auto i : multi_indexes) {
    auto x = box_center(i, n);
    auto idx_self = zisa::hilbert_index<n_levels>(x).to_ulong();

    auto path = std::bitset<2*n_dims>{};

    for (size_t l = 0; l < cardinal_directions.size(); ++l) {
      auto ii = add_multi_indexes(i, cardinal_directions[l]);

      if (is_safe_dir(ii, n)) {
        auto xx = box_center(ii, n);
        auto idx_neighbour = zisa::hilbert_index<n_levels>(xx).to_ulong();

        auto diff = abs(int(idx_self) - int(idx_neighbour));
        REQUIRE(diff > 0);

        if (diff == 1) {
          path[l] = true;
        }
      }
    }

    if (idx_self == 0u || idx_self == (1u << n_dims * n_levels) - 1) {
      REQUIRE(path.count() == 1);
    } else {
      REQUIRE(path.count() == 2);
    }
  }
}

TEST_CASE("Space Filling Curve 2D; continuous", "[math][sfc]") {
  constexpr int n_dims = 2;
  constexpr int n_levels = 5;

  auto cardinal_directions = std::vector<std::array<int, n_dims>>{
      {-1, 0}, {1, 0}, {0, -1}, {0, 1}};


  check_sfc_is_continuous<n_dims, n_levels>(cardinal_directions);
}


TEST_CASE("Space Filling Curve 3D; continuous", "[math][sfc]") {
  constexpr int n_dims = 3;
  constexpr int n_levels = 5;

  auto cardinal_directions = std::vector<std::array<int, n_dims>>{
      {-1, 0, 0}, {1, 0, 0}, {0, -1, 0}, {0, 1, 0}, {0, 0, -1}, {0, 0, 1}};


  check_sfc_is_continuous<n_dims, n_levels>(cardinal_directions);
}
