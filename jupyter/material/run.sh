#!/bin/bash

which pyenv >/dev/null 2>&1
if [ $? = 0 ]; then
    eval "$(pyenv init --path)"
fi

if [ -v $RUN_AS_ROOR ]; then
    root_opt="--allow-root"
else
    root_opt=""
fi

exec jupyter lab --JupyterApp.config_file=/jupyter_lab_config.py $root_opt
