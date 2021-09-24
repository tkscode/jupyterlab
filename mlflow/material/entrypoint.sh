#!/bin/bash

useradd -u ${MLRUNS_UID:-1000} -g root -m -s /bin/bash mlruns

export HOME=/home/mlruns

exec /usr/sbin/gosu mlruns "$@"
