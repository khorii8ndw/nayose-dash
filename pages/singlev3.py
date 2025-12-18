"""
単一名寄せ（single_v3）:
- 行の構造（固定 + 可変）は row_frame で維持
- 可変列を隠したとき、その横にコンテンツ2を表示
- コンテンツ1だけのときはフル幅
"""

import dash
from dash import html
from dash import Output, Input, callback
import dash_mantine_components as dmc

dash.register_page(__name__, path="/single_v3")


COLUMN_DEFS = {
    "is_new": {"label": "", "fixed": True, "w": 30, "ta": "center"},
    "id": {"label": "ID", "fixed": True, "w": 90, "ta": "center"},
    "updated_at": {"label": "更新日時", "fixed": True, "w": 150, "ta": "center"},
    "score": {"label": "スコア", "fixed": True, "w": 60, "ta": "center"},
    "actions": {"label": "", "fixed": True, "w": 60, "ta": "center"},
    "name": {"label": "氏名", "fixed": False, "ta": "left", "style": {"flex": "1 0 0"}},
    "address": {"label": "住所", "fixed": False, "ta": "left", "style": {"flex": "3 0 0"}},
    "phone": {"label": "電話番号", "fixed": False, "ta": "left", "style": {"flex": "1 0 0"}},
}

# -----------------------------
# 小物コンポーネント
# -----------------------------

def labeled_divider(label: str):
    return dmc.Group(
        align="center",
        children=[
            dmc.Divider(style={"width": 30}),
            dmc.Text(label, size="sm"),
            dmc.Divider(style={"flex": 10}),
        ],
    )


def header_cell(label, **text_props):
    default = {
        "className": "header_cell",
        "size": "sm",
        "ta": "center",
    }
    return dmc.Text(
        label,
        **{**default, **text_props},
    )


def value_cell_text(val, **text_props):
    default = {
        "className": "value_cell_text",
        "size": "sm",
    }
    return dmc.Text(
        val,
        **{**default, **text_props},
    )


# -----------------------------
# 行構造（固定 + 可変）※変えない
# -----------------------------

def row_frame(fixed, flexible, show_flexible: bool = True):
    """
    1行分の枠。
    - fixed: 左側（区分・更新日時など）のセル群
    - flexible: 右側（可変列）のセル群
    - show_flexible: False のときは右側を空にする
    """
    return dmc.Group(
        className="row",
        children=[
            dmc.Group(
                children=fixed,
            ),
            dmc.Group(
                style={"flex": 1},
                children=flexible if show_flexible else [],
            ),
        ],
    )


def dmc_props(col_def):
    control_keys = {"label", "fixed"}
    return {k: v for k, v in col_def.items() if k not in control_keys}

def header_row(column_defs, show_flexible = True):
    return row_frame(
        fixed=[
            header_cell(label=col["label"], **dmc_props(col))
            for col in column_defs.values() if col["fixed"]
        ],
        flexible=[
            header_cell(label=col["label"], **dmc_props(col))
            for col in column_defs.values() if not col["fixed"]
        ],
        show_flexible=show_flexible,
    )


def data_row(column_defs, record, show_flexible = True):
    cell_style = {
        "whiteSpace": "normal",
        "wordBreak": "break-word",
        "minWidth": 0,
    }
    return row_frame(
        fixed=[
            value_cell_text(val=record["is_new"], **dmc_props(column_defs["is_new"])),
            value_cell_text(val=record["id"], **dmc_props(column_defs["id"])),
            value_cell_text(val=record["updated_at"], **dmc_props(column_defs["updated_at"])),
            value_cell_text(val=record["score"], **dmc_props(column_defs["score"])),
            value_cell_text(val="", **dmc_props(column_defs["actions"])),
        ],
        flexible=[
            value_cell_text(record.get(key), **dmc_props(col))
            for key, col in column_defs.items() if not col["fixed"]
        ],
        show_flexible=show_flexible,
    )

def baseline_section(column_defs, records, show_flexible: bool = True):
    return dmc.Stack(
        className="baseline_section",
        children=[
            data_row(column_defs, r, show_flexible=show_flexible) for r in records
        ],
    )

def comparisons_section(column_defs, records, show_flexible: bool = True):
    return dmc.Stack(
        className="comparisons_section",
        children=[
            data_row(column_defs, r, show_flexible=show_flexible) for r in records
        ],
    )

# ========================================
# ダミーデータ
# ========================================

baseline_data = [
    {
        "is_new": False,
        "id": "rec-001",
        "updated_at": "2025/11/12 14:22",
        "score": "80",
        "name": "佐々木 太郎",
        "address": "東京都千代田区千代田1-1",
        "phone": "+81-90-1234-5678",
    }
]

comparisons_data = [
    {
        "is_new": True,
        "id": "rec-002",
        "updated_at": "2025/11/14 09:00",
        "score": "80",
        "name": "佐々木 太郎",
        "address": "東京都千代田区千代田1-1",
        "phone": "+81-90-1111-2222",
    },
    {
        "is_new": False,
        "id": "rec-003",
        "updated_at": "2025/11/10 10:05",
        "score": "80",
        "name": "佐々木 太郎",
        "address": "東京都中央区銀座1-1",
        "phone": "+81-90-1234-5678",
    },
    {
        "is_new": False,
        "id": "rec-004",
        "updated_at": "2025/11/11 15:30",
        "score": "80",
        "name": "ササキ タロウ",
        "address": "東京都千代田区千代田1-1",
        "phone": "+81-80-9999-8888",
    },
]


# -----------------------------
# コンテンツ1 / コンテンツ2
# -----------------------------

def build_contents(show_flexible: bool):
    """
    コンテンツ1（表全体）。
    show_flexible=False のときは右側の可変列を非表示にする。
    """
    return dmc.Stack(
        className="stack",
        children=[
            header_row(COLUMN_DEFS, show_flexible=show_flexible,),
            labeled_divider("比較元レコード"),
            baseline_section(COLUMN_DEFS, baseline_data, show_flexible=show_flexible),
            labeled_divider("比較先レコード"),
            comparisons_section(COLUMN_DEFS, comparisons_data, show_flexible=show_flexible),
        ],
    )


def build_contents2():
    """
    コンテンツ2（右側に出したい別の内容）。
    例として comparisons_section を複数並べておく。
    """
    return dmc.Stack(
        children=[
            comparisons_section(comparisons_data),
            comparisons_section(comparisons_data),
            comparisons_section(comparisons_data),
            comparisons_section(comparisons_data),
            comparisons_section(comparisons_data),
            comparisons_section(comparisons_data),
        ],
    )


# -----------------------------
# ページ共通レイアウト
# （Container を使わない版）
# -----------------------------

def page_layout(
    top,
    middle,
    bottom,
    *,
    py: str = "xl",
):
    """
    AppShell の main 内で使うページ共通レイアウト
    - page-root: ページ全体のラッパー（Stack）
    - page-stack: 縦に「上 / 真ん中 / 下」を並べる土台
    - ScrollArea: 真ん中だけスクロール
    """
    return dmc.Stack(
        className="page-root",
        py=py,  # 上下の余白だけ Mantine の spacing で付ける
        children=[
            dmc.Stack(
                className="page-stack",
                children=[
                    top,
                    dmc.ScrollArea(
                        className="page-scroll",
                        type="auto",
                        children=middle,
                    ),
                    bottom,
                ],
            )
        ],
    )


# -----------------------------
# layout 本体
#  middle はプレースホルダだけ置いて、コールバックで中身を切り替える
# -----------------------------

layout = page_layout(
    top=dmc.Group(
        position="apart",
        children=[
            dmc.Title("単一名寄せ", order=2),
            dmc.Switch(
                id="single-v3-toggle-alt",
                label="コンテンツ2を表示",
                size="sm",
                checked=False,
            ),
        ],
    ),
    middle=dmc.Stack(
        id="single-v3-middle",
    ),
    bottom=dmc.Title("フッター", order=2),
)


@callback(
    Output("single-v3-middle", "children"),
    Input("single-v3-toggle-alt", "checked"),
)
def update_single_v3_middle(show_alt: bool):
    if show_alt:
        # コンテンツ2表示モード：
        # 左：固定だけ（可変列は非表示）を広めに
        # 右：コンテンツ2 を狭めに
        return dmc.Grid(
            gutter=0,   # 列間の余白
            children=[
                dmc.Col(
                    span=4,
                    children=build_contents(show_flexible=False),
                ),
                dmc.Col(
                    span=8,
                    children=build_contents2(),
                ),
            ],
        )
    else:
        # 通常モード：
        # コンテンツ1だけ（可変列あり）をフル幅で表示
        return build_contents(show_flexible=True)
 