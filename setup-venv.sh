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

source ~/sportmonks/functions.sh
set_environment_variables


echo 'Delete ~/sportmonks/venv directory'
rm -rf ~/sportmonks/venv

echo 'Create virtual environment in `venv` directory'
$PYTHON -m venv ~/sportmonks/venv --copies

echo 'Activate virtual environment'
activate_virtual_environment

echo 'Upgrade pip'
# On Windows you cannot replace a binary that is running, hence pip install pip --upgrade fails.
# https://stackoverflow.com/questions/58627922/pip-install-upgrade-pip-fails-inside-a-windows-virtualenv-with-access-denie
$PYTHON -m pip install pip==20.2.4

echo 'Install wheel'
pip install wheel==0.35.1

echo 'Install pip-tools'
pip install pip-tools==6.4.0

echo 'Install from requirements.txt'
pip-sync ~/sportmonks/requirements-tests.txt

echo 'Check for broken requirements'
pip check

