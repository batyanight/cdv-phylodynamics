#!/bin/bash
set -e
echo "=== seed 12345 started $(date) ==="
cd /Users/batyanightingale/projects/cdv-phylodynamics/beast/clade3/run100M/seed12345
'/Applications/BEAST 2.7.7/bin/beast' -seed 12345 -threads 4 -overwrite /Users/batyanightingale/projects/cdv-phylodynamics/beast/clade3/run100M/seed12345/clade3_5state.xml > run.out 2>&1
echo "=== seed 12345 finished $(date) ==="
echo "=== seed 54321 started $(date) ==="
cd /Users/batyanightingale/projects/cdv-phylodynamics/beast/clade3/run100M/seed54321
'/Applications/BEAST 2.7.7/bin/beast' -seed 54321 -threads 4 -overwrite /Users/batyanightingale/projects/cdv-phylodynamics/beast/clade3/run100M/seed54321/clade3_5state.xml > run.out 2>&1
echo "=== seed 54321 finished $(date) ==="
