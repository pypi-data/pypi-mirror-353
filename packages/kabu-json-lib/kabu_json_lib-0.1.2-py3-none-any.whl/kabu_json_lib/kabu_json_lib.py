from datetime import datetime
import pytz
jst = pytz.timezone("Asia/Tokyo")


def bp(percent):
    """
    パーセント表記をベーシスポイント（bp）に変換します。
    例: 0.05 → 500
    Noneの場合はNoneを返します。
    """
    # Noneの場合はそのままNoneを返す
    return int(percent * 10000) if percent is not None else None


def fetch_now():
    """
    現在の日本時間をdatetimeオブジェクトで返します。
    タイムゾーンはAsia/Tokyoに設定されています。
    """
    return datetime.now(jst)
