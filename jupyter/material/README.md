# material

## jupyter_utils

学習データや学習済みのモデルなどをMLFlowにアップロードするためのユーティリティ `jupyter_utils` を用意しました

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
