#!/bin/bash

if [ -v $RUN_AS_ROOT ]; then
    exec "$@"
else
    useradd -u ${JUPYTER_UID:-1000} -g root -m -s /bin/bash jupyter

    export HOME=/home/jupyter
    export PATH="${HOME}/.local/bin:${PATH}"
    export PYTHONPATH="${HOME}/.local/lib/python${PYTHON_VERSION%.*}/site-packages:${PYTHON_PATH}"

    exec /usr/sbin/gosu jupyter "$@"
fi
