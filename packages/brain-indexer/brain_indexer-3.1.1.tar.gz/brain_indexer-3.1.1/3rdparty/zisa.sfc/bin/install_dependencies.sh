#! /usr/bin/env bash

# SPDX-License-Identifier: MIT
# Copyright (c) 2021 ETH Zurich, Luc Grosheintz-Laval

set -e

component_name="ZisaSFC"

if [[ "$#" -lt 2 ]]
then
    echo "Usage: $0 COMPILER DESTINATION [--cmake=CUSTOM_CMAKE_BINARY]"
    echo "                               [--print_install_dir]"
    exit -1
fi

for arg in "$@"
do
    case $arg in
        --cmake=*)
            CMAKE=$(realpath ${arg#*=})
            ;;
        --print_install_dir)
            PRINT_INSTALL_PATH=1
            ;;
        *)
            ;;
    esac
done

if [[ -z "${CMAKE}" ]]
then
    CMAKE=cmake
fi

zisa_root="$(realpath "$(dirname "$(readlink -f "$0")")"/..)"

CC="$1"
CXX="$(${zisa_root}/bin/cc2cxx.sh $CC)"

install_dir="$("${zisa_root}/bin/install_dir.sh" "$1" "$2")"
source_dir="${install_dir}/sources"
conan_file="${zisa_root}/conanfile.txt"

if [[ ${PRINT_INSTALL_PATH} -eq 1 ]]
then
  echo "$install_dir"
  exit 0
fi

mkdir -p "${install_dir}/conan" && cd "${install_dir}/conan"
conan install "$conan_file" \
        -s compiler=$(basename "${CC}") \
        -s compiler.libcxx=libstdc++11

echo "The dependencies were installed at"
echo "    export DEP_DIR=${install_dir}"
echo ""
echo "Use"
echo "    ${CMAKE} \\ "
echo "        -DCMAKE_PROJECT_${component_name}_INCLUDE=${install_dir}/conan/conan_paths.cmake \\ "
echo "        -DCMAKE_PREFIX_PATH=${install_dir}/zisa/lib/cmake/zisa \\ "
echo "        -DCMAKE_MODULE_PATH=${install_dir}/zisa/lib/cmake/zisa \\ "
echo "        -DCMAKE_C_COMPILER=${CC} \\ "
echo "        -DCMAKE_CXX_COMPILER=${CXX} \\ "
echo "        -DCMAKE_BUILD_TYPE=FastDebug \\ "
echo "        -B build \\ "
