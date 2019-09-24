#!/usr/bin/env bash

set -o nounset      # exit with non-zero status if expansion is attempted on an unset variable
set -o errexit      # exit immediately if a pipeline, a list, or a compound command fails
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


echo "Start integration testing of Python package 'sportmonks'"

echo "Loading SportMonks API key from environment variable SPORTMONKS_API_KEY, with fallback to ~/.sportmonks_api_key file."


# Check if variable is set (https://stackoverflow.com/questions/3601515/how-to-check-if-a-variable-is-set-in-bash)
if [[ -z ${SPORTMONKS_API_KEY+x} ]]; then

    echo "Environment variable SPORTMONKS_API_KEY not set. Falling back to ~/.sportmonks_api_key"
    echo "Check if ~/.sportmonks_api_key exists"

    if [[ -f ~/.sportmonks_api_key ]]; then
        echo "~/.sportmonks_api_key exists."
        sportmonks_api_key=$(head -1 ~/.sportmonks_api_key | tr -d '\n')
        echo "Loaded API key from ~/.sportmonks_api_key"
    else
        echo "~/.sportmonks_api_key does not exist. Quit with exit code 1."
        exit 1
    fi

else
    sportmonks_api_key=$(echo $SPORTMONKS_API_KEY)
    echo "Loaded API key from environment variable SPORTMONKS_API_KEY"

fi


echo "Run the tests"
PYTHONPATH=~/sportmonks ~/sportmonks/venv/bin/python3 -m pytest -vv --sportmonks-api-key "$sportmonks_api_key" ~/sportmonks/integration-tests

