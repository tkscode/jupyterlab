FROM continuumio/miniconda3:4.10.3

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY
ARG http_proxy
ARG https_proxy
ARG no_proxy

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

USER root

RUN set -ex \
    && apt-get update \
    && apt-get install --no-install-recommends gosu

RUN set -ex \
    && pip install --no-cache-dir -U setuptools pip \
    && pip install --no-cache-dir mlflow==1.19.0 \
    && rm -rf ~/.cache/

COPY material/entrypoint.sh /entrypoint.sh
COPY material/run.sh /run.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/run.sh"]
