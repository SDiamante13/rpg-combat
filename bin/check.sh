#!/usr/bin/env bash
set -euo pipefail
output=$(npm test 2>&1) || {
  echo "$output"
  exit 1
}
