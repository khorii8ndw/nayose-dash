"""
レコードレビュー（record-review）

単一テーブル内のレコードを比較・レビューするページ。
- 行の構造（固定 + 可変）は row_frame で維持
- 可変列を隠したとき、その横に詳細パネルを表示
- 可変列を表示するときはフル幅
"""

import dash
from dash import Output, Input, callback
import dash_mantine_components as dmc

from components.page_layout import page_layout
from configs.record_review import get_config
from data.mock.record_review import get_baseline_data, get_comparisons_data

dash.register_page(__name__, path="/record-review")


# ========================================
# コンポーネント群
# ========================================

# --- 小物コンポーネント ---

def labeled_divider(label: str):
    """ラベル付きディバイダー"""
    return dmc.Group(
        className="rr-divider",
        align="center",
        children=[
            dmc.Divider(style={"width": 45}),
            dmc.Text(label, size="sm", className="rr-divider__label"),
            dmc.Divider(style={"flex": 10}),
        ],
    )


def header_cell(label, **props):
    """ヘッダーセル"""
    default = {
        "className": "rr-table__cell rr-table__cell--header",
        "size": "sm",
        "ta": "center",
    }
    return dmc.Text(label, **{**default, **props})


# --- 行構造 ---

def row_frame(fixed, flexible, show_flexible: bool = True):
    """
    1行分の枠。
    - fixed: 左側（固定列）のセル群
    - flexible: 右側（可変列）のセル群
    - show_flexible: False のときは右側を空にする
    """
    return dmc.Group(
        className="rr-table__row",
        children=[
            dmc.Group(className="rr-table__row-fixed", children=fixed),
            dmc.Group(
                className="rr-table__row-flexible",
                style={"flex": 1},
                children=flexible if show_flexible else [],
            ),
        ],
    )


def header_row(config, show_flexible=True):
    """ヘッダー行を生成"""
    fixed_cells = [
        header_cell(col["label"], **col.get("props", {}))
        for col in config["fixed"]
    ]
    flexible_cells = [
        header_cell(col["label"], **col.get("props", {}))
        for col in config["flexible"]
    ]
    return row_frame(fixed_cells, flexible_cells, show_flexible=show_flexible)


def data_row(config, row_data, show_flexible=True):
    """データ行を生成"""
    fixed_cells = [
        col["render"](row_data, **col.get("props", {}))
        for col in config["fixed"]
    ]
    flexible_cells = [
        col["render"](row_data, **col.get("props", {}))
        for col in config["flexible"]
    ]
    return row_frame(fixed_cells, flexible_cells, show_flexible=show_flexible)



# --- セクション ---

def baseline_section(config, records, show_flexible: bool = True):
    """比較元セクション"""
    return dmc.Stack(
        className="rr-section rr-section--baseline",
        children=[data_row(config, r, show_flexible=show_flexible) for r in records],
    )


def comparisons_section(config, records, show_flexible: bool = True):
    """比較先セクション"""
    return dmc.Stack(
        className="rr-section rr-section--comparisons",
        children=[data_row(config, r, show_flexible=show_flexible) for r in records],
    )


# --- フッター ---
def review_action_buttons():
    """レビュー用アクションボタン（右寄せ）"""
    return dmc.Group(
        position="right",
        spacing="sm",
        children=[
            dmc.Button(
                "保留",
                id="rr-btn-hold",
                variant="outline",
                color="gray",
            ),
            dmc.Button(
                "承認",
                id="rr-btn-approve",
                color="blue",
            ),
        ],
    )


# ========================================
# コンテンツビルダー
# ========================================

def build_main_table(show_flexible: bool):
    """メインテーブルを生成"""
    config = get_config()
    baseline_data = get_baseline_data()
    comparisons_data = get_comparisons_data()
    return dmc.Stack(
        className="rr-table",
        children=[
            header_row(config, show_flexible=show_flexible),
            labeled_divider("比較元レコード"),
            baseline_section(config, baseline_data, show_flexible=show_flexible),
            labeled_divider("比較先レコード"),
            comparisons_section(config, comparisons_data, show_flexible=show_flexible),
        ],
    )


def build_detail_panel(show_flexible: bool):
    """詳細パネルを生成（右側パネル用）"""
    config = get_config()
    comparisons_data = get_comparisons_data()
    return dmc.Stack(
        className="rr-detail-panel",
        children=[
            comparisons_section(config, comparisons_data, show_flexible=show_flexible)
            for _ in range(6)
        ],
    )


# ========================================
# レイアウト定義
# ========================================

header = dmc.Stack(
    spacing="xs",
    children=[
        # 1行目：タイトル + スイッチ
        dmc.Group(
            position="apart",
            children=[
                dmc.Title("レコードレビュー", order=2),
                dmc.Switch(
                    id="rr-toggle-detail",
                    label="詳細パネルを表示",
                    size="sm",
                ),
            ],
        ),

        # 2行目：作業コンテキスト
        dmc.Text(
            "users_master を名寄せ中 · 残り 123 件",
            size="sm",
            c="dimmed",
        ),
    ],
)

footer = dmc.Stack(
    className="rr-footer",
    spacing="sm",
    children=[
        dmc.Divider(),
        review_action_buttons(),
    ],
)

layout = page_layout(
    header,
    #top=dmc.Group(
    #    position="apart",
    #    children=[
    #        dmc.Title("レコードレビュー", order=2),
    #        dmc.Switch(
    #            id="rr-toggle-detail",
    #            label="詳細パネルを表示",
    #            size="sm",
    #            checked=False,
    #        ),
    #    ],
    #),
    middle=dmc.Stack(id="rr-main-content"),
    #bottom=dmc.Title("フッター", order=2),
    bottom=footer,
)


# ========================================
# コールバック
# ========================================

@callback(
    Output("rr-main-content", "children"),
    Input("rr-toggle-detail", "checked"),
)
def update_rr_main_content(show_detail: bool):
    """表示モードの切り替え"""
    if show_detail:
        return dmc.Grid(
            gutter=0,
            children=[
                dmc.Col(span=4, children=build_main_table(show_flexible=False)),
                dmc.Col(span=8, children=build_detail_panel(show_flexible=False)),
            ],
        )
    return build_main_table(show_flexible=True)