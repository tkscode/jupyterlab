import importlib
import json
import os
import pickle as pkl
import re
import shutil
import subprocess
import tempfile
import urllib
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import git
import mlflow
import torch
from IPython.lib import kernel
from ipylab import JupyterFrontEnd
from lightgbm import LGBMModel
from pandas import DataFrame
from sklearn.base import BaseEstimator
from torch import nn
from transformers import PreTrainedModel, PreTrainedTokenizerBase


JUPYTER_ROOT_DIR = os.environ.get("JUPYTER_ROOT_DIR", "/opt/jupyter")

class ObjectDumper():
    """任意のオブジェクトを出力するクラス."""

    def __init__(self):
        # モジュール（型）ごとの出力関数を定義
        self.dump_func: Dict[str, Callable] = {
            # 文字列（プレーンテキスト）
            "str": self.__dump_plain_text,
            # ファイルパスオブジェクト
            "pathlib.Path": self.__copy_object,
            # pandasのDataFrame
            "pandas.DataFrame": self.__dump_dataframe,
            # LightGBMのモデル
            "lightgbm.LGBMModel": self.__dump_lgb_model,
            # Huggingface transformersのモデル
            "transformers.PreTrainedModel": self.__dump_transformers_model,
            # Huggingface transformersのトークナイザ
            "transformers.PreTrainedTokenizerBase": self.__dump_transformers_model,
            # PyTorchのモデル
            "torch.nn.Module": self.__dump_pytorch_model,
            # Scikit-learnのモデル
            "sklearn.base.BaseEstimator": self.__dump_sklearn_model,
        }
        
        # モジュール（型）の名前と実際のオブジェクトを紐付ける
        # -> 後の型チェック時に利用する
        self.allow_types: Dict[str, Any] = {}
        for module_path in self.dump_func.keys():
            self.allow_types[module_path] = self.__resolve_module(module_path)

    def __resolve_module(self, module_path: str) -> Any:
        """モジュール名（文字列）から実際のオブジェクトをimportする.
        
        Parameters
        ----------
        module_path : str
            モジュール名のフルパス
        
        Returns
        -------
        Any
            importしたモジュールのオブジェクト
        """
        if module_path == "str":
            return str
        
        idx = module_path.rfind(".")
        prefix = module_path[:idx]
        module_name = module_path[idx+1:]
        
        return getattr(importlib.import_module(prefix), module_name)

    def __dump_plain_text(self, text: str, target_path: Path) -> None:
        """プレーンテキストを出力する.
        
        Parameters
        ----------
        text : str
            出力するテキスト
        target_path : Path
            出力先のパス
        """
        target_path.write_text(text)

    def __dump_dataframe(self, df: DataFrame, target_path: Path) -> None:
        """pandasのDataFrameをCSV形式で出力する.
        
        Parameters
        ----------
        df : DataFrame
            出力するDataFrame
        target_path : Path
            出力先のパス
        """
        df.to_csv(target_path, encoding="utf-8-sig", index=False)

    def __copy_object(self, source_path: Path, target_path: Path) -> None:
        """指定したファイル/ディレクトリをコピーする.
        
        Parameters
        ----------
        source_path : Path
            コピー元のパス
        target_path : Path
            コピー先のパス
        """
        if source_path.is_dir():
            shutil.copytree(source_path, target_path)
        else:
            shutil.copyfile(source_path, target_path)

    def __dump_lgb_model(self, model: LGBMModel, target_path: Path) -> None:
        """LightGBMのモデルを出力する.
        
        Parameters
        ----------
        model : LGBMModel
            出力するモデル
        target_path : Path
            出力先のパス
        """
        model.booster_.save_model(target_path.as_posix())

    def __dump_transformers_model(self, model: Union[PreTrainedModel, PreTrainedTokenizerBase],
                                  target_path: Path) -> None:
        """Huggingface transformersのモデルやトークナイザを出力する.
        
        Parameters
        ----------
        model : Union[PreTrainedModel, PreTrainedTokenizerBase]
            出力するモデルまたはトークナイザ
        target_path : Path
            出力先のパス
        """
        model.save_pretrained(target_path.as_posix())

    def __dump_pytorch_model(self, model: nn.Module, target_path: Path) -> None:
        """PyTorchのモデルを出力する.
        
        Parameters
        ----------
        model : nn.Module
            出力するモデル
        target_path : Path
            出力先のパス
        """
        torch.save(model.to("cpu").state_dict(), target_path.as_posix())

    def __dump_sklearn_model(self, model: BaseEstimator, target_path: Path) -> None:
        """Scikit-learnのモデルを出力する.
        
        Parameters
        ----------
        model : BaseEstimator
            出力するモデル
        target_path : Path
            出力先のパス
        """
        with open(target_path, "wb") as fp:
            pkl.dump(model, fp)

    def __call__(self, obj: Any, target_path: Path, expect_types: List[str]) -> None:
        """オブジェクトを指定したパスに出力する.
        
        Parameters
        ----------
        obj : Any
            出力するオブジェクト
        target_path : Path
            出力先のパス
        expect_types : List[str]
            期待するオブジェクトのモジュール（型）
        """
        for expect_type in expect_types:
            if isinstance(obj, self.allow_types[expect_type]):
                self.dump_func[expect_type](obj, target_path)
                break
        else:
            raise ValueError(f'Unexpected object type {type(obj)} (Expected: {", ".join(expect_types)})')

def _save_notebook() -> None:
    """呼び出し元のノートブックを保存する.
    
    Notes
    -----
    * ref: https://github.com/jtpio/ipylab/issues/82
    """
    def _save():
        app.commands.execute('docmanager:save')

    app = JupyterFrontEnd()
    app.on_ready(_save)

def _get_kernel_id() -> str:
    """呼び出し者のノートブックのカーネルIDを取得する.
    
    Returns
    -------
    str
        カーネルID
    """
    conn_file = kernel.get_connection_file().split('/')[-1]
    kernel_id = re.findall('kernel-(.*)\.json', conn_file)[0]
    
    return kernel_id

def _get_sessions() -> List[Dict[str, Any]]:
    """JupyterLabのセッション一覧を取得する.
    
    Returns
    -------
    List[Dict[str, Any]]
        セッション一覧
    """
    # "jupyter server list"コマンドからJupyterLabのURLを取得する
    servers = subprocess.run(["jupyter", "server", "list"], capture_output=True).stdout.decode()
    server_url = re.search(r"(http://.+?)\s", servers).group(1)

    # JupyterLabのURLからセッション一覧取得APIのURLを作成する
    sessions_api_url = re.sub("\?token", "api/sessions?token", server_url)

    # セッション一覧を取得
    return json.loads(urllib.request.urlopen(sessions_api_url).read())

def _get_self_notebook() -> Optional[Dict[str, Any]]:
    """呼び出し元のノートブック情報（ファイルパスなど）を取得する.
    
    Returns
    -------
    Optional[Dict[str, Any]]
        ノートブック情報（取得できない場合はNone）
    """
    # 起動中のセッション一覧を取得して、カーネルIDが一致するノートブックの情報を返す
    kernel_id = _get_kernel_id()
    sessions = _get_sessions()
    for session in sessions:
        if session["kernel"]["id"] == kernel_id:
            return session["notebook"]
    
    return None

def _get_git_remote_url(repo_dir: str) -> Optional[str]:
    """GitのリモートリポジトリのURLを取得する.

    Parameters
    ----------
    repo_dir : str
        Gitリポジトリの場所
    
    Returns
    -------
    Optional[str]
        リモートリポジトリのURL（設定されていない/取得できない場合はNone）
    """
    remotes = list(git.Repo(repo_dir).remote().urls)
    if len(remotes) == 0:
        return None
    
    remote_url = remotes[0]
    if remote_url.startswith("http"):
        return remote_url
    
    m = re.search(r"git@([^:]+:?[0-9]*):([^\.]+)\.git", remote_url)
    if m:
        return f'https://{m.group(1)}/{m.group(2)}'
    
    return None

def _get_git_branch(repo_dir: str) -> str:
    """Gitのカレントブランチ名を取得する.

    Parameters
    ----------
    repo_dir : str
        Gitリポジトリの場所
    
    Returns
    -------
    str
        カレントブランチ名
    """
    return git.Repo(repo_dir).active_branch.name

def _commit_notebook(repo_dir: str) -> Optional[str]:
    """ノートブックファイルをコミットする.

    Parameters
    ----------
    repo_dir : str
        リポジトリのディレクトリパス
    
    Returns
    -------
    Optional[str]
        コミットハッシュ（ノートブックの情報が取得できなかった場合はコミットできないのでNone）
    """
    # ノートブックを保存する
    _save_notebook()

    # ノートブック情報を取得する
    notebook = _get_self_notebook()
    if notebook is None:
        # ノートブックの情報が取得できない場合は何もしない
        return None

    # ノートブックのファイルパスを取得する
    notebook_path = os.path.join(JUPYTER_ROOT_DIR, notebook["path"])
    # JupyTextにより.pyファイルも生成されるので、そちらのパスも取得する
    notebook_text_path = notebook_path.replace(".ipynb", ".py")

    # ノートブックのipynbファイルとJupyTextによるpyファイルをコミットする
    repo = git.Repo(repo_dir)
    repo.index.add([notebook_path, notebook_text_path])
    commit = repo.index.commit(f'[Auto] Update {notebook["path"]}')
    
    return commit.hexsha

def save_mlflow(experiment_name: str, run_name: Optional[str]=None, description: str="", params: Dict[str, Any]={}, metrics: Dict[str, float]={},
                    dataset: Dict[str, Any]={}, model: Dict[str, Any]={}, result: Dict[str, Any]={},
                    do_git_commit: bool=True, git_repo_dir: str=".",
                    mlf_uri: str="http://mlflow:5000") -> None:
    """MLFlowに実験結果を保存する.
    
    Parameters
    ----------
    experiment_name : str
        実験名（MLFlowで管理されるExperimentに相当）
    run_name : Optional[str]
        実行名, default: None
    description : str
        実行の説明, default: ""
    params : Dict[str, Any]
        モデルのパラメータ（key: パラメータ名, value: 値）, default: {}
    metrics : str
        各種精度指標の値（key: 指標, value: 精度）, default: {}
    dataset : Dict[str, Any]
        保存するデータセット（key: ファイル名, value: データセットのオブジェクト）, default: {}
        プレーンテキスト、pandasのDataFrame、データのファイルパス（ディレクトリも可）に対応
        ファイル/ディレクトリパスの場合はファイル/ディレクトリがコピーされます
    model : Dict[str, Any]
        保存するモデル（key: ファイル名, value: モデルオブジェクト）, default: {}
        LightGBM、Huggingface transformers、PyTorch、Scikit-learnのモデルに対応
    result : Dict[str, Any]
        保存するテストデータに対する推論結果など（key: ファイル名, value: 推論結果のオブジェクト）, default: {}
        プレーンテキスト、pandasのDataFrame、データのファイルパス（ディレクトリも可）に対応
        ファイル/ディレクトリパスの場合はファイル/ディレクトリがコピーされます
    do_git_commit : bool
        ノートブックをGitコミットするかどうかのフラグ（True: コミットする, False: コミットしない）, default: True
    git_repo_dir : str
        Gitリポジトリの場所, default: .
    mlf_uri : str
        MLFlowのサーバURI, default: http://mlflow:5000
    
    Notes
    -----
    * 指定した`experiment_name`に対応するMLFlowのExperimentに実験結果が保存されます
    * `dataset`, `model`, `result`で指定したオブジェクトはMLFlowのArtifactとして保存されます
    * GitのPushは実行しないため、JupyterLabのGitプラグインなどを利用してPushをしてください
    
    Examples
    --------
    >>> jupyter_util.save_mlflow("test_exp", run_name="test1", description="Test Experiment1", params={"p1": 0.1, "p2": 10}, metrics={"recall": 0.7, "precision": 0.8, "f1": 0.7467}, dataset={"train.csv": DataFrame(...), "val.csv": DataFrame(...), "test": Path("/path/to/test_data")}, model={"t5_model": ..., "tokenizer": ...}, result={"test_result.csv": DataFrame(...)})
    """
    mlflow.set_tracking_uri(mlf_uri)
    mlflow.set_experiment(experiment_name)

    # 一時的なディレクトリを作成
    with tempfile.TemporaryDirectory() as tmp_dir:
        print("- make temporary dir")
        print(f"    dir: {tmp_dir}")
        
        dumper = ObjectDumper()

        # データセットの保存
        print("- save dataset to temporary dir")
        dataset_dir_path = Path(tmp_dir) / "dataset"
        dataset_dir_path.mkdir(parents=True, exist_ok=True)
        for key, value in dataset.items():
            save_path = dataset_dir_path / key
            print(f"    file: {save_path}")
            dumper(value, save_path,
                   expect_types=["str", "pathlib.Path", "pandas.DataFrame"])

        # モデルの保存
        print("- save model to temporary dir")
        model_dir_path = Path(tmp_dir) / "model"
        model_dir_path.mkdir(parents=True, exist_ok=True)
        for key, value in model.items():
            save_path = model_dir_path / key
            print(f"    file: {save_path}")
            dumper(value, save_path,
                   expect_types=["lightgbm.LGBMModel",
                                 "transformers.PreTrainedModel", "transformers.PreTrainedTokenizerBase",
                                 "torch.nn.Module",
                                 "sklearn.base.BaseEstimator"])

        # 結果の保存
        print("- save result to temporary dir")
        result_dir_path = Path(tmp_dir) / "result"
        result_dir_path.mkdir(parents=True, exist_ok=True)
        for key, value in result.items():
            save_path = result_dir_path / key
            print(f"    file: {save_path}")
            dumper(value, save_path,
                   expect_types=["str", "pathlib.Path", "pandas.DataFrame"])

        # コミットする
        if do_git_commit:
            print("- commit notebook file")
            commit_id = _commit_notebook(git_repo_dir)
            print(f"    hash: {commit_id}")
        else:
            commit_id = None

        # MLFlowにパラメータやデータ、モデル、結果などを格納する
        print("- upload data to MLFlow")
        with mlflow.start_run(run_name=run_name):
            mlflow.set_tag("mlflow.note.content", description)
            if commit_id:
                git_remote_url = _get_git_remote_url(git_repo_dir)
                git_branch = _get_git_branch(git_repo_dir)
                # print(f"    git repo: {git_remote_url}")
                # print(f"    git branch: {git_branch}")
                mlflow.set_tag("mlflow.source.git.repoURL", git_remote_url)
                mlflow.set_tag("mlflow.source.git.branch", git_branch)
                mlflow.set_tag("mlflow.source.git.commit", commit_id)

            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            mlflow.log_artifacts(tmp_dir)
