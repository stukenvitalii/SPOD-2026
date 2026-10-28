#!/usr/bin/env bash
set -euo pipefail

lab_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
mode="${1:-unordered}"
processes="${2:-8}"
if (( $# > 0 )); then shift; fi
if (( $# > 0 )); then shift; fi
case "$mode" in
    unordered|ordered) ;;
    *) echo 'Mode must be unordered or ordered.' >&2; exit 1 ;;
esac
if [[ ! "$processes" =~ ^[1-9][0-9]*$ ]]; then
    echo 'Process count must be a positive integer.' >&2
    exit 1
fi
command -v mpirun >/dev/null || { echo 'Install Open MPI: brew install open-mpi' >&2; exit 1; }
[[ -x "$lab_dir/build/$mode" ]] || { echo 'Run bash practical-01/build.sh first.' >&2; exit 1; }
mpi_args=()
if [[ "${OVERSUBSCRIBE:-0}" == 1 ]]; then mpi_args+=(--oversubscribe); fi
exec mpirun "${mpi_args[@]}" -n "$processes" "$lab_dir/build/$mode" "$@"
