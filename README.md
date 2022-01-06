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

## Usage

コンテナ内のユーザのuidとコンテナを起動するユーザのuidを一緒にするためにuidを`.env`ファイルに出力する
```
$ echo "CONTAINER_UID=$(id -u)" >> .env
```

### Run

+ JupyterLabをrootユーザで実行する場合は`docker-compose.yml`の`jupyter.environment`に`RUN_AS_ROOT`という名前の環境変数名をセットする。
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

+ MLFlowがデフォルトで利用するディレクトリを変更する場合は`docker-compose.yml`の`mlflow.environment`に`MLFLOW_STORE_DIR`という名前の環境変数名でディレクトリを指定する。（デフォルトは`/opt/mlflow`）
    + 設定例
```
- MLFLOW_STORE_DIR="/mnt/fs/mlflow"
```

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

### Stop

### CPUの場合

```
$ docker-compose stop
```

### GPUの場合

```
$ docker-compose -f docker-compose.yml -f docker-compose.gpu.yml stop
```

**`docker-compose down`する場合はコンテナが削除され、永続化されていないデータも削除されるため注意すること**

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

+ Jupyter LabのコンテナにインストールされるPythonライブラリやそのバージョンは[requirements.common.txt](./jupyter/requirements.common.txt)や[requirements.cpu.txt](./jupyter/requirements.cpu.txt)などを参照してください
+ Jupyter Lab内のNotebookファイルは`./volume/jupyter/`以下に配置されます
    + デフォルトでjupytextが有効になっているため、Notebookファイルの保存と同時に`.py`ファイルが生成されます
+ MLFlowのartifactは`./volume/mlflow/`以下にRun IDごとに配置されます
+ 学習データや学習済みのモデルなどをMLFlowにアップロードするためのユーティリティ `jupyter_utils` を用意しました
    + **予めJupyterLabのGitプラグインでリモートリポジトリをCloneしておく必要があります**
        + JupyterLabの上部メニューにある「Git」から「Clone a Repository」をクリックし、リモートリポジトリのURL（HTTPSまたはSSH）を指定することでCloneが可能です
        + SSHによるCloneを行う場合、JupyterLabのターミナルを開いてSSH鍵の生成し、リモートリポジトリへの鍵登録を行ってください
    + `jupyter_utils`モジュールの`save_mlflow`関数を呼び出すことで呼び出し元のノートブックファイルをGitコミットし、データセットやモデルなどをMLFlowにアップロードすることができます
    + `save_mlflow`関数の引数については以下の通りです
        + **（必須）**`experiment_name`：MLFlowの実験名に対応する情報
        + `run_name`：実行ラスクの名前
        + `descrption`：実行タスクの説明
        + `params`：学習パラメータ。`dict`型でキーにパラメータ名、値にそのパラメータを指定する
        + `metrics`：各種精度指標ごとの値。`dict`型でキーに指標名（RecallやF1など）、値に精度を指定する
        + `dataset`：学習データやテストデータ。`dict`型でキーに出力ファイル名、値にデータのオブジェクトを指定する
            + 出力可能なオブジェクトはプレーンテキスト（`str`）、pandasのDataFrame（`pandas.DataFrame`）、PythonのPath（`pathlib.Path`）の3種類
                + pandasのDataFrameの場合は、BOM付きUTF-8のCSV形式で出力されます
                + PythonのPathの場合、そのパスのファイルまたはディレクトリがMLFlowに保存されます
            + MLFlowのArtifactには`dataset`ディレクトリ以下に保存されます
        + `model`：学習済みのモデル。`dict`型でキーに出力ファイル名、値にモデルオブジェクトを指定する
            + 出力可能なモデルは以下のライブラリのものになります
                + Huggingface transformers（`transformers`）：ファインチューニング後のモデルおよびトークナイザ
                + PyTorch（`torch`）：モデル内部のパラメータ（レイヤー数など）は保持されないため、別途`params`で保存するようにしてください
                + LightGBM（`lightgbm`）
                + Scikit-learn（`sklearn`）
            + MLFlowのArtifactには`model`ディレクトリ以下に保存されます
        + `result`：テストデータなどの推論結果。`dict`型でキーに出力ファイル名、値に結果のオブジェクトを指定する
            + 出力仕様は`dataset`と同様になります
            + MLFlowのArtifactには`result`ディレクトリ以下に保存されます
        + `do_commit`：コミットを行うかどうかのフラグ。Trueならコミットを行い、Falseなら行わない（デフォルトはコミットを行う）
        + `git_repo_dir`：ローカルのGitリポジトリのディレクトリパス（デフォルトはノートブックファイルのあるディレクトリ）
        + `mlf_uri`：MLFlowのサーバURL（デフォルトはMLFlowのコンテナで起動したMLFlowのURL）
    + 利用例
        ```python
        import pandas as pd
        import jupyter_utils

        train_dataset = pd.DataFrame(...)
        val_dataset = pd.DataFrame(...)
        test_dataset = pd.DataFrame(...)
        params = {"p1": 1.0, "p2": 10, ...}
        model = ...
        metrics = {"recall": 0.8, "precision": 0.7, ...}
        results = pd.DataFrame(...)

        jupyter_utils.save_mlflow(experiment_name="test_exp", description="Test experiment",
                                params=params, metics=metrics,
                                dataset={"train.csv": train_dataset, "val.csv": val_dataset, "test.csv": test_dataset},
                                model={"classifier.mdl": model},
                                result={"test_results.csv": results})
        ```

## 免責事項

+ Linux（Ubuntu 18.04）やWSL2上での動作確認は行っていますが、他の環境でも同様に動くかどうかの保証はいたしかねます。
+ 本リポジトリで公開しているJupyter Labやその内部でインストールされたライブラリ・ツール、MLFlowを利用して何らかの不都合や損害が発生しても何ら責任を負うものではありません。
