"""
各種デコレータを提供するモジュール

このモジュールは、ライブラリ内で使用される共通のデコレータを提供する。
現在は認証関連のデコレータが実装されている。
"""

from functools import wraps


def login_required(func):
    """
    ログインが必要なメソッドや関数に適用するデコレータ

    このデコレータを適用したメソッドや関数は、実行前に自動的にログイン状態をチェックする。
    ログインしていない場合はLoginRequiredExceptionが送出される。

    クライアントインスタンスは以下の優先順位で検索される：
    1. client という名前の引数
    2. Client クラスのインスタンスである引数
    3. self.client（呼び出し元オブジェクトの属性）
    4. selfが持つ属性が持つclientクラス（例：self.site.client）

    Parameters
    ----------
    func : callable
        デコレートする関数またはメソッド

    Returns
    -------
    callable
        ラップされた関数またはメソッド

    Raises
    ------
    ValueError
        クライアントインスタンスが見つからない場合
    LoginRequiredException
        ログインしていない場合（client.login_check()による）
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        client = None
        if "client" in kwargs:
            client = kwargs["client"]
        else:
            from wikidot.module.client import Client

            for arg in args:
                if isinstance(arg, Client):
                    client = arg
                    break

            # selfに存在するか？
            if client is None and args:
                if hasattr(args[0], "client"):
                    client = args[0].client
                else:
                    # selfが持つ属性にclientが存在するか探索する
                    for attr_name in dir(args[0]):
                        if attr_name.startswith("_"):
                            continue
                        attr = getattr(args[0], attr_name)
                        if hasattr(attr, "client"):
                            client = getattr(attr, "client")
                            if isinstance(client, Client):
                                break

        if client is None:
            raise ValueError("Client is not found")

        client.login_check()

        return func(*args, **kwargs)

    return wrapper
