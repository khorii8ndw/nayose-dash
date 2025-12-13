"""
複数名寄せ - CSVアップロードで一括比較
"""

import dash
from dash import dcc
import dash_mantine_components as dmc

dash.register_page(__name__, path="/batch")

layout = dmc.Container(
    className="page-content",
    children=[
        dmc.Title("複数名寄せ", order=2),
        dmc.Text("CSVファイルをアップロードして一括で名寄せを実行します。", color="dimmed"),
        dmc.Divider(my="sm"),
        dmc.Paper(
            className="input-card",
            children=dcc.Upload(
                id="batch-upload",
                className="upload-area",
                children=dmc.Stack(
                    align="center",
                    children=[
                        dmc.Text("ファイルをドラッグ＆ドロップ"),
                        dmc.Text("または クリックして選択", color="dimmed", size="sm"),
                    ],
                ),
            ),
        ),
        dmc.Button("名寄せ実行", id="batch-run-btn", className="btn-full", disabled=True),
        dmc.Paper(
            className="result-area",
            withBorder=True,
            children=dmc.Text("結果がここに表示されます", id="batch-result", color="dimmed"),
        ),
    ],
)
