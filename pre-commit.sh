#!/usr/bin/env bash

# Install this script as git pre-commit hook with by
# creating a symlink called `pre-commit` in .git/hooks directory

set -o nounset      # exit with non-zero status if expansion is attempted on an unset variable
set -o errexit      # exit immediatelly if a pipeline, a list, or a compound command fails
set -o pipefail     # failures in pipe in the commands before last one, also count as failures

# Trapping non-zero exit codes:
on_error() {
    line_num="$1"
    echo "Caught error on line $line_num"
}

on_exit() {
    true
}

on_interrupt() {
    true
}
trap 'on_error $LINENO' ERR
trap on_exit EXIT
trap on_interrupt INT

echo "Run static code checks"
./run-static-code-checks.sh

echo "Run unit tests"
./run-unit-tests.sh

