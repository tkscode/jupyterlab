#!/bin/bash

which pyenv >/dev/null 2>&1
if [ $? = 0 ]; then
    eval "$(pyenv init --path)"
fi

exec jupyter lab --JupyterApp.config_file=/jupyter_lab_config.py
