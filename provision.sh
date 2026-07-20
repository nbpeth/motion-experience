#!/usr/bin/env bash
# Builds ./venv and installs dependencies.
#
# NOTE: a script cannot change its parent shell's environment, so plain
# `./provision.sh` provisions everything but leaves your shell unactivated
# (start.sh activates the venv itself, so that's fine). If you also want the
# venv active in your current shell, run this as: `source provision.sh`

echo "Provisioning the environment"

python3 -m venv ./venv

echo "Activating the virtual environment"
source ./venv/bin/activate

echo "Installing dependencies"
pip3 install -r requirements.txt
