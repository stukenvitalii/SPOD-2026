#!/usr/bin/env bash
set -euo pipefail

lab_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
rounds="${ROUNDS:-1000}"
repeats="${REPEATS:-3}"
if [[ ! "$rounds" =~ ^[1-9][0-9]*$ || ! "$repeats" =~ ^[1-9][0-9]*$ ]]; then
    echo 'ROUNDS and REPEATS must be positive integers.' >&2
    exit 1
fi
mkdir -p "$lab_dir/results"
output="$lab_dir/results/timings-$(date +%Y%m%d-%H%M%S)-$$.csv"
printf 'mode,processes,count,rounds,total_seconds,seconds_per_round,repeat\n' > "$output"
for mode in unordered ordered; do
    for count in 1 256 16384; do
        for processes in 1 2 4 8 16; do
            bash "$lab_dir/run.sh" "$mode" "$processes" --rounds 10 --count "$count" --benchmark >/dev/null
            for ((repeat = 1; repeat <= repeats; ++repeat)); do
                row="$(bash "$lab_dir/run.sh" "$mode" "$processes" --rounds "$rounds" --count "$count" --benchmark)"
                printf '%s,%s\n' "$row" "$repeat" >> "$output"
            done
        done
    done
done
printf 'Saved: %s\n' "$output"
