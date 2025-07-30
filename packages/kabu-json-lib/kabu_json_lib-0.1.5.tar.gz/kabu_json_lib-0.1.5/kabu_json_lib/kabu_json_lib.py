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


def order_to_one_line(order):
    """
    注文情報を1行の文字列にフォーマットする

    Args:
        order (dict): convert_order_dataで変換された注文情報
            - datetime_obj: datetimeオブジェクト

    Returns:
        str: フォーマットされた1行の文字列
    """
    time_str = order["datetime_obj"].strftime("%Y-%m-%d %H:%M:%S")
    return f"""[{order["long_or_short"].ljust(5)}-{order["entry_or_exit"].ljust(5)} ]{order["symbol"]:>5} @{order["price"]:>6} * {order["quantity"]:>5} (¥{order["value"]:>9}) [{order["order_type"]}] {time_str}"""
