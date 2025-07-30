#!/bin/bash

path="$1"

# Run pytests
if [ "$path" != "" ]; then
    read -p "Do you want to show logs? [y/n]: " logs
    if [[ "$logs" == "y" ]]; then
        echo "Showing logs..."
        python -m pytest "$path" -s --disable-pytest-warnings
    else
        echo "Not showing logs..."
        python -m pytest "$path" --disable-pytest-warnings
    fi
else
    coverage run --rcfile=./pyproject.toml -m pytest --disable-pytest-warnings && coverage report
    # delete coverage file
    rm .coverage
fi

# delete all cache of tests
find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
