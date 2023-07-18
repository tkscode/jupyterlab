# jupyterlab

自然言語処理のためのディープラーニング用JupyterLabコンテナを作るリポジトリです。

## 前提

+ Docker version 24.X
    + https://docs.docker.com/engine/install/
+ nvidia-container-toolkit（GPUを利用する場合）
    + https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#docker

## 利用方法

本リポジトリをcloneしてください。
```
$ git clone https://github.com/tkscode/jupyterlab.git
$ cd jupyterlab/
```

コンテナ内のユーザのuidとコンテナを起動するユーザのuidを一緒にするためにuidを`.env`ファイルに出力してください。
```
$ echo "CONTAINER_UID=$(id -u)" >> .env
```

### コンテナの起動

### CPUの場合

```
$ docker compose pull
$ docker compose up -d
```

### GPUの場合

```
$ docker compose -f docker-compose.yml -f docker-compose.gpu.yml pull
$ docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

+ JupyterLabは`http://<hostname>:8080/lab`になります。
    + JupyterLabにアクセスした際に入力するパスワード（トークン）は`docker compose logs`でコンテナのログを表示し、ログ中にあるトークン（`http://127.0.0.1:8080/lab?token=<トークン>`の部分）を利用してください。

### コンテナの停止

### CPUの場合

```
$ docker compose stop
```

### GPUの場合

```
$ docker compose -f docker-compose.yml -f docker-compose.gpu.yml stop
```

## コンテナイメージのビルド

プロキシ環境下の場合、`.env`ファイルにプロキシ設定を記述してください。
```
$ echo 'HTTP_PROXY=http://<proxy_user>:<proxy_pass>@<proxy_host>:<proxy_port>' >> .env
$ echo 'HTTPS_PROXY=http://<proxy_user>:<proxy_pass>@<proxy_host>:<proxy_port>' >> .env
$ echo 'NO_PROXY=<no_proxy_host>,...' >> .env
```

### CPUの場合

```
$ docker compose build
```

### GPUの場合

```
$ docker compose -f docker-compose.yml -f docker-compose.gpu.yml build
```

プロキシ設定を行わない場合、以下のような警告メッセージが表示されますが無視して問題ありません。
```
WARNING: The HTTP_PROXY variable is not set. Defaulting to a blank string.
WARNING: The HTTPS_PROXY variable is not set. Defaulting to a blank string.
WARNING: The NO_PROXY variable is not set. Defaulting to a blank string.
```

## 補足

+ デフォルトでPython `3.10.12`がインストールされていますが、他のPythonバージョンを使いたい場合は`.env`ファイルに`PYTHON_VERSION`変数でバージョンを指定してください。
    ```
    $ echo "PYTHON_VERSION=3.9.17" >> .env
    ```
+ GPU利用のコンテナイメージのCUDAバージョンは`11.8.0`ですが、他のCUDAバージョンを使いたい場合は`.env`ファイルに`CUDA_VERSION`変数でバージョンを指定してください。
    ```
    $ echo "CUDA_VERSION=12.2.0" >> .env
    ```
    + **GPUドライバのバージョンによって利用可能なCUDAのバージョンが異なるため、[NVIDIAの公式ページ](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html#id5)でバージョンの組み合わせを確認した上で指定してください。**
        + 利用不可なCUDAバージョンの場合、コード実行時に以下のような警告メッセージが表示されることがあります。（以下はPyTorchを利用した例）
            ```
            UserWarning: CUDA initialization: Unexpected error from cudaGetDeviceCount(). Did you run some cuda functions before calling NumCudaDevices() that might have already set an error? Error 804: forward compatibility was attempted on non supported HW
            ```
    + **CUDAのバージョンによってはベースイメージのUbuntuのバージョンを変える必要があるため、その際は`.env`ファイルに`UBUNTU_VERSION`変数でバージョンを指定してください。**
        + 利用可能なCUDAとUbuntuのバージョンの組み合わせは[DockerHubのNVIDIAのページ](https://hub.docker.com/r/nvidia/cuda/tags)を参照してください。
+ JupyterLabのコンテナにインストールされるPythonライブラリやそのバージョンは[requirements.txt](./jupyter/requirements.txt)を参照してください。
    + **実施したい内容によってバージョンの変動があり得るDeepLearning系のライブラリ（`torch`や`transformers`など）は明示的にインストールしていないので、必要に応じてpip installを行ってください。**
+ Jupyter Lab内のNotebookファイルは`./volume/jupyter/`以下に配置されます。
+ JupyterLabにアクセスするポートを変えたい場合は`.env`ファイルに`JUPYTER_PORT`変数でポート番号を指定してください。
    ```
    $ echo "JUPYTER_PORT=18080" >> .env
    ```
+ JupyterLabをrootユーザで実行する場合は`docker-compose.yml`の`jupyter.environment`に`RUN_AS_ROOT`という名前の環境変数名をセットしてください。
    + 設定例
        ```
        - RUN_AS_ROOT=1
        ```
+ JupyterLabがデフォルトで利用するディレクトリを変更する場合は`docker-compose.yml`の`jupyter.environment`に`JUPYTER_ROOT_DIR`と`JUPYTER_NOTEBOOK_DIR`という名前の環境変数名でディレクトリを指定してください。（デフォルトは`/opt/jupyter`）
    + 設定例
        ```
        - JUPYTER_ROOT_DIR="/mnt/fs/jupyter"
        - JUPYTER_NOTEBOOK_DIR="/mnt/fs/jupyter"
        ```

## 免責事項

+ Linux（Ubuntu 20.04）上での動作確認は行っていますが、他の環境でも同様に動くかどうかの保証はいたしかねます。
+ 本リポジトリで公開しているJupyterLabやその内部でインストールされたライブラリ・ツールを利用して何らかの不都合や損害が発生しても何ら責任を負うものではありません。
