# jupyterlab

テキスト系のディープラーニング用JupyterLabコンテナの構築  
MLFlowを使った実験管理も可能

## Pre-require

+ Docker version 20.X
    + https://docs.docker.com/engine/install/
+ docker-compose version 1.29.X
    + https://docs.docker.com/compose/install/
+ nvidia-docker2（GPUを利用する場合）
    + https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker

## Build

コンテナ内のユーザのuidとコンテナを起動するユーザのuidを一緒にするためにuidを`.env`ファイルに出力する
```
$ echo "CONTAINER_UID=$(id -u)" >> .env
```

プロキシ環境下の場合、`.env`ファイルにプロキシ設定を記述する。（プロキシ設定は環境に応じて変更すること）
```
$ echo 'HTTP_PROXY=http://<proxy_user>:<proxy_pass>@<proxy_host>:<proxy_port>' >> .env
$ echo 'HTTPS_PROXY=http://<proxy_user>:<proxy_pass>@<proxy_host>:<proxy_port>' >> .env
$ echo 'NO_PROXY=<no_proxy_host>,...' >> .env
```

### CPUの場合

```
$ docker-compose build
```

### GPUの場合

```
$ docker-compose -f docker-compose.yml -f docker-compose.gpu.yml build
```

プロキシ設定を行わない場合、以下のような警告メッセージが表示されるが無視して良い。
```
WARNING: The HTTP_PROXY variable is not set. Defaulting to a blank string.
WARNING: The HTTPS_PROXY variable is not set. Defaulting to a blank string.
WARNING: The NO_PROXY variable is not set. Defaulting to a blank string.
```

## Run

### CPUの場合

```
$ docker-compose up -d
```

### GPUの場合

```
$ docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

+ JupyterLab: `http://<hostname>:18080/lab`
+ MLFlow: `http://<hostname>:15000`

## Stop

### CPUの場合

```
$ docker-compose stop
```

### GPUの場合

```
$ docker-compose -f docker-compose.yml -f docker-compose.gpu.yml stop
```

`docker-compose down`する場合はコンテナが削除され、永続化されていないデータも削除されるため注意すること

## 補足

+ Jupyter LabのコンテナにインストールされるPythonライブラリやそのバージョンは[requirements.common.txt](./jupyter/requirements.common.txt)や[requirements.cpu.txt](./jupyter/requirements.cpu.txt)などを参照してください
+ Jupyter Lab内のNotebookファイルは`./volume/jupyter/`以下に配置されます
    + デフォルトでjupytextが有効になっているため、Notebookファイルの保存と同時に`.py`ファイルが生成されます
+ MLFlowのartifactは`./volume/mlflow/`以下にRun IDごとに配置されます

## 免責事項

+ Linux（Ubuntu 18.04）やWSL2上での動作確認は行っていますが、他の環境でも同様に動くかどうかの保証はいたしかねます。
+ 本リポジトリで公開しているJupyter Labやその内部でインストールされたライブラリ・ツール、MLFlowを利用して何らかの不都合や損害が発生しても何ら責任を負うものではありません。
