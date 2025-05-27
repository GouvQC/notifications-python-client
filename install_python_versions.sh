#!/bin/bash
set -e

export PATH="/root/.pyenv/bin:$PATH"
export PYENV_ROOT="/root/.pyenv"

eval "$(pyenv init --path)"
eval "$(pyenv init -)"

for v in $(cat tox-python-versions); do
  pyenv install -s "$v"
  "$PYENV_ROOT/versions/$v/bin/pip" install --upgrade setuptools==78.1.1
done
