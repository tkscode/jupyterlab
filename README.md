# jupyterlab

自然言語処理のためのディープラーニング用JupyterLabコンテナを作るリポジトリです。

## Pre-require

+ Docker version 20.X
    + https://docs.docker.com/engine/install/
+ docker-compose version 1.29.X
    + https://docs.docker.com/compose/install/
+ nvidia-docker2（GPUを利用する場合）
    + https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker

## Usage

コンテナ内のユーザのuidとコンテナを起動するユーザのuidを一緒にするためにuidを`.env`ファイルに出力する
```
$ echo "CONTAINER_UID=$(id -u)" >> .env
```

### Run

### CPUの場合

```
$ docker-compose pull
$ docker-compose up -d
```

### GPUの場合

```
$ docker-compose -f docker-compose.yml -f docker-compose.gpu.yml pull
$ docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

+ JupyterLab: `http://<hostname>:18080/lab`
    + JupyterLabにアクセスした際に入力するパスワード（トークン）は`docker-compose logs jupyter`でコンテナのログを表示し、ログ中にあるトークン（`http://127.0.0.1:8080/lab?token=<トークン>`の部分）を利用する
+ MLFlow: `http://<hostname>:15000`

### Stop

### CPUの場合

```
$ docker-compose stop
```

### GPUの場合

```
$ docker-compose -f docker-compose.yml -f docker-compose.gpu.yml stop
```

**`docker-compose down`する場合はコンテナが削除され、永続化されていないデータやノートブック上でインストールしたライブラリも削除されるため注意すること**

## Build

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

## 補足

+ JupyterLabにアクセスするポートを変えたい場合は`.env`ファイルに`JUPYTER_PORT`変数でポート番号を指定してください。
    ```
    $ echo "JUPYTER_PORT=18080" >> .env
    ```
    + 設定例（セットする値は何でも良い）
        ```
        - RUN_AS_ROOT=1
        ```
+ JupyterLabがデフォルトで利用するディレクトリを変更する場合は`docker-compose.yml`の`jupyter.environment`に`JUPYTER_ROOT_DIR`と`JUPYTER_NOTEBOOK_DIR`という名前の環境変数名でディレクトリを指定する。（デフォルトは`/opt/jupyter`）
    + 設定例
        ```
        - JUPYTER_ROOT_DIR="/mnt/fs/jupyter"
        - JUPYTER_NOTEBOOK_DIR="/mnt/fs/jupyter"
        ```

## 免責事項

+ Linux（Ubuntu 18.04）やWSL2上での動作確認は行っていますが、他の環境でも同様に動くかどうかの保証はいたしかねます。
+ 本リポジトリで公開しているJupyter Labやその内部でインストールされたライブラリ・ツール、MLFlowを利用して何らかの不都合や損害が発生しても何ら責任を負うものではありません。
