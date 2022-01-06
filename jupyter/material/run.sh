#!/bin/bash

which pyenv >/dev/null 2>&1
if [ $? = 0 ]; then
    eval "$(pyenv init --path)"
fi

if [ -v RUN_AS_ROOT ]; then
    root_opt="--allow-root"
else
    root_opt=""
    mkdir -p $HOME/.config/git
    cp /.gitignore $HOME/.config/git/ignore
fi

if [ -n "$JUPYTER_PASSWORD" ]; then
    # パスワードがセットされている場合はハッシュを計算して上書き
    export JUPYTER_PASSWORD=$(python -c "from notebook.auth import passwd;print(passwd(\"${JUPYTER_PASSWORD}\"))")
fi

exec jupyter lab --JupyterApp.config_file=/jupyter_lab_config.py $root_opt
