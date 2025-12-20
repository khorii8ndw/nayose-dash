"""
レコードレビュー用ダミーデータ

将来的にはAPIから取得する想定。
テスト時は get_xxx_data() 関数をモックして差し替え可能。
"""

# ========================================
# 比較元レコード
# ========================================

BASELINE_DATA = [
    {
        "is_new": False,
        "is_baseline": True,
        "record_id": "rec-001",
        "updated_at": "2025/11/12 14:22",
        "pair_info": None,
        "name": "佐々木 太郎",
        "address": "東京都千代田区千代田1-1",
        "phone": "+81-90-1234-5678",
    }
]


# ========================================
# 比較先レコード
# ========================================

COMPARISONS_DATA = [
    {
        "is_new": True,
        "is_baseline": False,
        "record_id": "rec-002",
        "updated_at": "2025/11/14 09:00",
        "pair_info": {"score": 0.92},
        "name": "佐々木 太郎",
        "address": "東京都千代田区千代田1-1",
        "phone": "+81-90-1111-2222",
    },
    {
        "is_new": False,
        "is_baseline": False,
        "record_id": "rec-003",
        "updated_at": "2025/11/10 10:05",
        "pair_info": {"score": 0.85},
        "name": "佐々木 太郎",
        "address": "東京都中央区銀座1-1",
        "phone": "+81-90-1234-5678",
    },
    {
        "is_new": False,
        "is_baseline": False,
        "record_id": "rec-004",
        "updated_at": "2025/11/11 15:30",
        "pair_info": {"score": 0.78},
        "name": "ササキ タロウ",
        "address": "東京都千代田区千代田1-1",
        "phone": "+81-80-9999-8888",
    },
]


# ========================================
# データ取得関数（UT時にモック差し替え用）
# ========================================

def get_baseline_data():
    """比較元レコードを取得"""
    return BASELINE_DATA


def get_comparisons_data():
    """比較先レコードを取得"""
    return COMPARISONS_DATA
