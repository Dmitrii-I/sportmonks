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

echo 'Loading functions.sh'

function set_environment_variables {
    if [[ "$OSTYPE" == "linux-gnu" ]]; then
        PYTHON="python3"
        VENV_EXECUTABLES_DIR="bin"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        PYTHON="python3"
        VENV_EXECUTABLES_DIR="bin"
    elif [[ "$OSTYPE" == "cygwin" ]]; then
        PYTHON="python"
        VENV_EXECUTABLES_DIR="Scripts"
    elif [[ "$OSTYPE" == "msys" ]]; then
        export PYTHON="python"
        VENV_EXECUTABLES_DIR="Scripts"
    elif [[ "$OSTYPE" == "win32" ]]; then
        PYTHON="python"
        VENV_EXECUTABLES_DIR="Scripts"
    elif [[ "$OSTYPE" == "freebsd"* ]]; then
        PYTHON="python3"
        VENV_EXECUTABLES_DIR="bin"
    else
        echo "Unknow operating system"
        exit 1
    fi
}


function activate_virtual_environment {
    source ~/sportmonks/venv/$VENV_EXECUTABLES_DIR/activate
}

