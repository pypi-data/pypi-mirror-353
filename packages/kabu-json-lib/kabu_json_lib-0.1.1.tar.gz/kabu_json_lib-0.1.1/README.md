# kabu-json-lib

システムトレーディングに必要な計算や便利なPythonライブラリをまとめたパッケージです。

## 機能一覧
- bp関数: パーセント表記をベーシスポイント（bp）に変換します。
- fetch_now関数: 現在の日本時間をdatetimeオブジェクトで返します。

## インストール方法
（PyPI公開後に記載予定）

## 使い方
```python
from kabu_json_lib import bp, fetch_now

print(bp(0.05))  # 500
print(bp(None))  # None

now = fetch_now()
print(now)  # 2023-10-01 12:34:56+09:00
``` 
