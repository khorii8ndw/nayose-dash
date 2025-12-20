"""
レコードレビュー用の列定義

セルレンダラーと列定義を含む。
将来、共通セルレンダラーが増えたら components/cells.py に切り出す。
"""

import dash_mantine_components as dmc


# ========================================
# セルレンダラー
# ========================================

def status_cell(row_data, **props):
    """NEW バッジを表示"""
    if row_data.get("is_new"):
        return dmc.Badge(
            "NEW",
            color="green",
            size="sm",
            variant="light",
            className="rr-table__cell rr-table__cell--status",
            **props,
        )
    return dmc.Text("", className="rr-table__cell rr-table__cell--status", **props)


def score_cell(row_data, **props):
    """スコアを表示（比較元の場合は "—"）"""
    if row_data.get("is_baseline"):
        return dmc.Text(
            "—",
            size="sm",
            className="rr-table__cell rr-table__cell--score",
            **props,
        )
    score = row_data.get("pair_info", {}).get("score") if row_data.get("pair_info") else None
    return dmc.Text(
        f"{score:.2f}" if score else "—",
        size="sm",
        className="rr-table__cell rr-table__cell--score",
        **props,
    )


def text_cell(key):
    """テキストセルのレンダラーを生成"""
    def _render(row_data, **props):
        return dmc.Text(
            row_data.get(key) or "—",
            size="sm",
            className="rr-table__cell",
            **props,
        )
    return _render


def action_cell(row_data, **props):
    """アクションメニューを表示"""
    record_id = row_data.get("record_id")
    menu_items = [
        dmc.MenuItem("スコア詳細", id={"type": "rr-menu-score", "id": record_id}),
        dmc.MenuItem("比較元に変更", id={"type": "rr-menu-baseline", "id": record_id}),
        dmc.MenuItem("cannot設定", id={"type": "rr-menu-cannot-add", "id": record_id}),
    ]
    return dmc.Menu([
        dmc.MenuTarget(
            dmc.ActionIcon(
                dmc.Text("⋮"),
                variant="subtle",
                size="sm",
                className="rr-table__cell rr-table__cell--action",
                **props,
            )
        ),
        dmc.MenuDropdown(menu_items),
    ])


# ========================================
# 列定義
# ========================================

FIXED_COLUMNS = [
    {
        "key": "is_new",
        "label": "",
        "render": status_cell,
        "props": {"w": 45},
    },
    {
        "key": "record_id",
        "label": "ID",
        "render": text_cell("record_id"),
        "props": {"w": 75, "ta": "center"},
    },
    {
        "key": "updated_at",
        "label": "更新日時",
        "render": text_cell("updated_at"),
        "props": {"w": 120, "ta": "center"},
    },
    {
        "key": "score",
        "label": "スコア",
        "render": score_cell,
        "props": {"w": 60, "ta": "center"},
    },
    {
        "key": "action",
        "label": "",
        "render": action_cell,
        "props": {"w": 60, "ta": "left"},
    },
]

FLEXIBLE_COLUMNS = [
    {
        "key": "name",
        "label": "氏名",
        "render": text_cell("name"),
        "props": {"ta": "left", "style": {"flex": "3 0 0"}},
    },
    {
        "key": "address",
        "label": "住所",
        "render": text_cell("address"),
        "props": {"ta": "left", "style": {"flex": "6 0 0"}},
    },
    {
        "key": "phone",
        "label": "電話番号",
        "render": text_cell("phone"),
        "props": {"ta": "left", "style": {"flex": "3 0 0"}},
    },
]


# ========================================
# 設定取得関数
# ========================================

def get_config():
    """列定義を取得"""
    return {
        "fixed": FIXED_COLUMNS,
        "flexible": FLEXIBLE_COLUMNS,
    }