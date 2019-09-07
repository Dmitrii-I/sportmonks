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

echo 'This script sets up a virtual environment in which `sportmonks` can be tested and developed'


echo 'Delete ~/sportmonks/venv directory'
rm -rf ~/sportmonks/venv

echo 'Create virtual environment in `venv` directory'
python3 -m venv venv --copies

echo 'Activate virtual environment'
source venv/bin/activate

echo 'Upgrade pip'
pip install pip --upgrade

echo 'Install from requirements.txt'
pip install -r requirements.txt

echo 'Check for broken requirements'
pip check

