"""
単一名寄せ - 2つのレコードを比較
"""

import dash
from dash import html
import dash_mantine_components as dmc

dash.register_page(__name__, path="/single")


def create_record_card(suffix):
    return dmc.Paper(
        className="input-card",
        withBorder=True,
        children=dmc.Stack([
            dmc.Title(f"レコード {suffix}", order=4),
            dmc.TextInput(label="名前", id=f"single-name-{suffix.lower()}", placeholder="山田 太郎"),
            dmc.TextInput(label="住所", id=f"single-addr-{suffix.lower()}", placeholder="東京都渋谷区..."),
            dmc.TextInput(label="電話", id=f"single-phone-{suffix.lower()}", placeholder="03-1234-5678"),
        ]),
    )


layout = dmc.Container(
    className="page-content",
    children=[
        dmc.Title("単一名寄せ", order=2),
        dmc.Text("2つのレコードを比較して類似度を計算します。", color="dimmed"),
        dmc.Divider(my="sm"),
        html.Div(
            className="two-column",
            children=[
                create_record_card("A"),
                create_record_card("B"),
            ],
        ),
        dmc.Button("比較する", id="single-compare-btn", className="btn-full"),
        dmc.Paper(
            className="result-area",
            withBorder=True,
            children=dmc.Text("結果がここに表示されます", id="single-result", color="dimmed"),
        ),
    ],
)
