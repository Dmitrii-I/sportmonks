#!/usr/bin/env bash

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

source ~/sportmonks/functions.sh

echo "Activate virtual environment"
set_environment_variables
activate_virtual_environment

echo "Test code"

echo "Clear mypy cache"
# Stale cache has lead to tests passing on my machine but not in GitHub Actions
rm -rf ~/sportmonks/.mypy_cache/

paths="$(/usr/bin/find ~/sportmonks/sportmonks -name '*.py')"
cd ~/sportmonks

for path in $paths; do
    echo
    echo "##############################################################################"
    path="sportmonks/$(basename $path)"
    echo "Test $path"
    pylava --verbose --options ~/sportmonks/setup.cfg --format pep8 "$path"
    mypy --verbose --config-file ~/sportmonks/setup.cfg "$path"
    echo
done

echo "Check that package and tests code is formatted with 'black --line-length 120'"
black --check --line-length 120 ~/sportmonks/unit-tests
black --check --line-length 120 ~/sportmonks/sportmonks
black --check --line-length 120 ~/sportmonks/integration-tests
