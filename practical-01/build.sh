#!/usr/bin/env bash
set -euo pipefail

lab_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
compiler="${MPICXX:-mpic++}"
command -v "$compiler" >/dev/null || { echo 'Install Open MPI: brew install open-mpi' >&2; exit 1; }
mkdir -p "$lab_dir/build"
for mode in unordered ordered; do
    "$compiler" -std=c++17 -O2 -Wall -Wextra -Wpedantic \
        "$lab_dir/src/$mode.cpp" -o "$lab_dir/build/$mode"
done
printf 'Built: %s\n' "$lab_dir/build"
